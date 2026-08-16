"""PySide6 dashboard panel acting as PMLA-SCWE's main command center."""

from __future__ import annotations
import os
import datetime
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QScrollArea, QProgressBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap

from core import student_service
from core.database import get_db_status, execute_select

from desktop.widgets.animated_card import AnimatedCard
from desktop.widgets.reusable_ui_components import (
    AnimatedProgressBar, SectionHeader, StatusBadge, EmptyState,
)


class KPICard(AnimatedCard):
    def __init__(self, parent, title, initial_val, trend_text, click_cmd, bar_variant="red"):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.click_cmd = click_cmd

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        self.title_lbl = QLabel(title, self)
        self.title_lbl.setStyleSheet(
            "color: #8D96A8; font-size: 10px; font-weight: 700;"
            " letter-spacing: 1px; background: transparent; border: none;"
        )
        layout.addWidget(self.title_lbl)

        self.val_lbl = QLabel(initial_val, self)
        self.val_lbl.setStyleSheet(
            "color: #F5F7FA; font-size: 26px; font-weight: 800;"
            " background: transparent; border: none;"
        )
        layout.addWidget(self.val_lbl)

        # Parse trend text to determine color
        trend_color = "#8D96A8"
        if trend_text.startswith("↑") or trend_text.startswith("+") or "Healthy" in trend_text:
            trend_color = "#30C48D"
        elif trend_text.startswith("↓") or trend_text.startswith("-"):
            trend_color = "#E5484D"
        else:
            trend_color = "#4D8DFF"

        self.trend_lbl = QLabel(trend_text, self)
        self.trend_lbl.setStyleSheet(
            f"color: {trend_color}; font-size: 10px; background: transparent; border: none;"
        )
        layout.addWidget(self.trend_lbl)

        layout.addSpacing(6)

        # Animated progress bar — initialized at 0, updated in refresh
        self.progress_bar = AnimatedProgressBar(value=0.0, variant=bar_variant, bar_height=5, animate=False)
        layout.addWidget(self.progress_bar)

    def set_value(self, val_text: str, progress: float = 0.0):
        self.val_lbl.setText(val_text)
        self.progress_bar.set_value(progress, animate=True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.click_cmd()


class DashboardFrame(QWidget):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(15)
        
        # 1. Friendly Header Block
        self.create_header_section()
        
        # 2. KPI Section
        self.create_kpi_section()

        # 3. Smart Teacher Actions (v1.7)
        self.create_smart_actions_section()
        
        # 4. Row 1 Grid: [Needs Attention] + [Class Performance Trend]
        self.create_row1_section()

        
        # 4. Row 2 Grid: [Students Needing Support] + [Quick Actions]
        self.create_row2_section()
        
        # 5. Row 3 Grid: [Today's Attendance] + [AI Daily Insight]
        self.create_row3_section()
        
        # 6. Bottom Grid: [Recent Activity Timeline]
        self.create_timeline_section()
        
        self.scroll.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll)
        
        self.refresh_dashboard()

    def create_header_section(self):
        self.header = QFrame(self.scroll_content)
        self.header.setObjectName("CardFrame")
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(20, 15, 20, 15)

        txt_widget = QWidget(self.header)
        txt_widget.setStyleSheet("background: transparent;")
        txt_layout = QVBoxLayout(txt_widget)
        txt_layout.setContentsMargins(0, 0, 0, 0)
        txt_layout.setSpacing(3)

        self.welcome_text = QLabel("Good Morning, Admin 👋", txt_widget)
        self.welcome_text.setFont(QFont("Outfit", 20, QFont.Bold))
        self.welcome_text.setStyleSheet(
            "color: #F5F7FA; background: transparent; border: none;"
        )
        txt_layout.addWidget(self.welcome_text)

        subtitle = QLabel(
            "Here is today’s learning intelligence overview.",
            txt_widget
        )
        subtitle.setFont(QFont("Outfit", 12))
        subtitle.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        txt_layout.addWidget(subtitle)

        h_layout.addWidget(txt_widget)
        h_layout.addStretch(1)

        # Right controls
        right_widget = QWidget(self.header)
        right_widget.setStyleSheet("background: transparent;")
        right_layout = QHBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        self.db_status_lbl = QLabel("●  MySQL", right_widget)
        self.db_status_lbl.setFont(QFont("Outfit", 11, QFont.Bold))
        self.db_status_lbl.setStyleSheet(
            "color: #30C48D; background: transparent; border: none;"
        )
        right_layout.addWidget(self.db_status_lbl)

        refresh_btn = QPushButton("Refresh", right_widget)
        refresh_btn.setFont(QFont("Outfit", 11))
        refresh_btn.clicked.connect(self.refresh_dashboard)
        right_layout.addWidget(refresh_btn)

        h_layout.addWidget(right_widget)
        self.scroll_layout.addWidget(self.header)

    def create_kpi_section(self):
        kpi_widget = QWidget(self.scroll_content)
        layout = QHBoxLayout(kpi_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.kpi_students = KPICard(
            kpi_widget, "TOTAL STUDENTS", "0",
            "+4 this month",
            lambda: self.controller.switch_to_frame("students"),
            bar_variant="blue",
        )
        self.kpi_performance = KPICard(
            kpi_widget, "CLASS PERFORMANCE", "0.0%",
            "↑ 3% vs prev period",
            lambda: self.controller.switch_to_frame("analytics"),
            bar_variant="purple",
        )
        self.kpi_attendance = KPICard(
            kpi_widget, "ATTENDANCE RATE", "0.0%",
            "↓ 2% this month",
            lambda: self.controller.switch_to_frame("attendance"),
            bar_variant="success",
        )
        self.kpi_wellness = KPICard(
            kpi_widget, "CYBER-WELLNESS", "0.0%",
            "Healthy overall",
            lambda: self.controller.switch_to_frame("wellness"),
            bar_variant="success",
        )

        layout.addWidget(self.kpi_students)
        layout.addWidget(self.kpi_performance)
        layout.addWidget(self.kpi_attendance)
        layout.addWidget(self.kpi_wellness)

        self.scroll_layout.addWidget(kpi_widget)

    def create_smart_actions_section(self):
        self.smart_actions_panel = QFrame(self.scroll_content)
        self.smart_actions_panel.setObjectName("CardFrame")
        self.smart_actions_panel.setStyleSheet(
            "QFrame#CardFrame { background: #10131D; border-left: 4px solid #7C5CFF; border-radius: 8px; }"
        )
        sa_layout = QVBoxLayout(self.smart_actions_panel)
        sa_layout.setContentsMargins(18, 14, 18, 14)
        sa_layout.setSpacing(8)

        sa_header = QLabel("⚡ SMART RECOMMENDED TEACHER ACTIONS", self.smart_actions_panel)
        sa_header.setFont(QFont("Outfit", 12, QFont.Bold))
        sa_header.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        sa_layout.addWidget(sa_header)

        self.smart_actions_container = QWidget(self.smart_actions_panel)
        self.smart_actions_container.setStyleSheet("background: transparent;")
        self.smart_actions_layout = QVBoxLayout(self.smart_actions_container)
        self.smart_actions_layout.setContentsMargins(0, 0, 0, 0)
        self.smart_actions_layout.setSpacing(6)
        sa_layout.addWidget(self.smart_actions_container)

        self.scroll_layout.addWidget(self.smart_actions_panel)

    def create_row1_section(self):

        row1_widget = QWidget(self.scroll_content)
        layout = QHBoxLayout(row1_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Left Panel: Needs Attention
        self.needs_attention_panel = QFrame(row1_widget)
        self.needs_attention_panel.setObjectName("CardFrame")
        self.needs_attention_panel.setMinimumHeight(300)
        na_layout = QVBoxLayout(self.needs_attention_panel)
        na_layout.setContentsMargins(20, 15, 20, 15)
        
        na_title = QLabel("⚠️ NEEDS ATTENTION", self.needs_attention_panel)
        na_title.setFont(QFont("Outfit", 13, QFont.Bold))
        na_title.setStyleSheet("color: #F5A524; background: transparent; border: none;")
        na_layout.addWidget(na_title)
        
        # Alert rows
        self.high_risk_row = self.create_alert_row(self.needs_attention_panel, "🔴 High Risk Students", "0", lambda: self.controller.switch_to_frame("analytics"))
        self.attendance_alert_row = self.create_alert_row(self.needs_attention_panel, "🟠 Low Attendance Alerts", "0", lambda: self.controller.switch_to_frame("attendance"))
        self.wellness_alert_row = self.create_alert_row(self.needs_attention_panel, "🟡 Cyber-Wellness Alerts", "0", lambda: self.controller.switch_to_frame("wellness"))
        
        na_layout.addWidget(self.high_risk_row)
        na_layout.addWidget(self.attendance_alert_row)
        na_layout.addWidget(self.wellness_alert_row)
        
        view_all_alerts_btn = QPushButton("VIEW ALL ALERTS →", self.needs_attention_panel)
        view_all_alerts_btn.setStyleSheet("color: #E5484D; text-align: left; background: transparent; border: none;")
        view_all_alerts_btn.setFont(QFont("Outfit", 11, QFont.Bold))
        view_all_alerts_btn.setCursor(Qt.PointingHandCursor)
        view_all_alerts_btn.clicked.connect(lambda: self.controller.switch_to_frame("analytics"))
        na_layout.addWidget(view_all_alerts_btn)
        
        layout.addWidget(self.needs_attention_panel)
        
        # Right Panel: Class Performance Trend Chart
        self.chart_panel = QFrame(row1_widget)
        self.chart_panel.setObjectName("CardFrame")
        self.chart_panel.setMinimumHeight(300)
        cp_layout = QVBoxLayout(self.chart_panel)
        cp_layout.setContentsMargins(20, 15, 20, 15)
        
        chart_title = QLabel("📊 CLASS PERFORMANCE TREND", self.chart_panel)
        chart_title.setFont(QFont("Outfit", 13, QFont.Bold))
        chart_title.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
        cp_layout.addWidget(chart_title)
        
        self.chart_display_lbl = QLabel("Generating progress trends...", self.chart_panel)
        self.chart_display_lbl.setFont(QFont("Outfit", 13, QFont.Bold))
        self.chart_display_lbl.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        self.chart_display_lbl.setAlignment(Qt.AlignCenter)
        cp_layout.addWidget(self.chart_display_lbl, 1)
        
        view_analytics_btn = QPushButton("VIEW FULL ANALYTICS →", self.chart_panel)
        view_analytics_btn.setStyleSheet("color: #4D8DFF; text-align: left; background: transparent; border: none;")
        view_analytics_btn.setFont(QFont("Outfit", 11, QFont.Bold))
        view_analytics_btn.setCursor(Qt.PointingHandCursor)
        view_analytics_btn.clicked.connect(lambda: self.controller.switch_to_frame("analytics"))
        cp_layout.addWidget(view_analytics_btn)
        
        layout.addWidget(self.chart_panel)
        
        self.scroll_layout.addWidget(row1_widget)

    def create_alert_row(self, parent, label_text, count_val, click_cmd) -> QFrame:
        row_frame = QFrame(parent)
        row_frame.setObjectName("InnerCardFrame")
        row_frame.setCursor(Qt.PointingHandCursor)
        row_frame.setFixedHeight(45)
        
        layout = QHBoxLayout(row_frame)
        layout.setContentsMargins(15, 0, 15, 0)
        
        lbl = QLabel(label_text, row_frame)
        lbl.setFont(QFont("Outfit", 13, QFont.Bold))
        lbl.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
        layout.addWidget(lbl)
        
        layout.addStretch(1)
        
        cnt = QLabel(count_val, row_frame)
        cnt.setFont(QFont("Outfit", 15, QFont.Bold))
        cnt.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
        layout.addWidget(cnt)
        
        # Override mouse click
        def mousePressEvent(event):
            if event.button() == Qt.LeftButton:
                click_cmd()
        row_frame.mousePressEvent = mousePressEvent
        
        return row_frame

    def create_row2_section(self):
        row2_widget = QWidget(self.scroll_content)
        layout = QHBoxLayout(row2_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Left Column: Students Needing Support
        self.support_panel = QFrame(row2_widget)
        self.support_panel.setObjectName("CardFrame")
        s_layout = QVBoxLayout(self.support_panel)
        s_layout.setContentsMargins(20, 15, 20, 15)
        
        support_title = QLabel("👥 STUDENTS NEEDING SUPPORT", self.support_panel)
        support_title.setFont(QFont("Outfit", 13, QFont.Bold))
        support_title.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
        s_layout.addWidget(support_title)
        
        self.support_rows_container = QWidget(self.support_panel)
        self.support_rows_layout = QVBoxLayout(self.support_rows_container)
        self.support_rows_layout.setContentsMargins(0, 5, 0, 5)
        self.support_rows_layout.setSpacing(6)
        s_layout.addWidget(self.support_rows_container)
        
        view_all_students_btn = QPushButton("VIEW ALL STUDENTS →", self.support_panel)
        view_all_students_btn.setStyleSheet("color: #4D8DFF; text-align: left; background: transparent; border: none;")
        view_all_students_btn.setFont(QFont("Outfit", 11, QFont.Bold))
        view_all_students_btn.setCursor(Qt.PointingHandCursor)
        view_all_students_btn.clicked.connect(lambda: self.controller.switch_to_frame("students"))
        s_layout.addWidget(view_all_students_btn)
        
        layout.addWidget(self.support_panel)
        
        # Right Column: Quick Actions
        quick_actions_panel = QFrame(row2_widget)
        quick_actions_panel.setObjectName("CardFrame")
        qa_layout = QVBoxLayout(quick_actions_panel)
        qa_layout.setContentsMargins(20, 15, 20, 15)
        qa_layout.setSpacing(8)
        
        qa_title = QLabel("⚡ QUICK ACTIONS", quick_actions_panel)
        qa_title.setFont(QFont("Outfit", 13, QFont.Bold))
        qa_title.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
        qa_layout.addWidget(qa_title)
        
        # Action Buttons
        self.create_action_btn(quick_actions_panel, qa_layout, "👤 Register New Student", lambda: self.controller.switch_to_frame("students"))
        self.create_action_btn(quick_actions_panel, qa_layout, "✓ Mark Attendance Registry", lambda: self.controller.switch_to_frame("attendance"))
        self.create_action_btn(quick_actions_panel, qa_layout, "📝 Add Academic Assessment", lambda: self.controller.switch_to_frame("assessments"))
        self.create_action_btn(quick_actions_panel, qa_layout, "🛡️ Lodge Cyber Wellness Audit", lambda: self.controller.switch_to_frame("wellness"))
        self.create_action_btn(quick_actions_panel, qa_layout, "🤖 Ask AI Decision Assistant", lambda: self.controller.switch_to_frame("ai_assistant"))
        
        layout.addWidget(quick_actions_panel)
        
        self.scroll_layout.addWidget(row2_widget)

    def create_action_btn(self, parent, layout, text, action_cmd):
        btn = QPushButton(text, parent)
        btn.setStyleSheet("text-align: left; padding-left: 15px; height: 36px;")
        btn.setFont(QFont("Outfit", 12, QFont.Bold))
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(action_cmd)
        layout.addWidget(btn)

    def create_row2_student_row(self, parent, student_id, name, risk, lhs, reason):
        row_frame = QFrame(parent)
        row_frame.setObjectName("InnerCardFrame")
        row_frame.setCursor(Qt.PointingHandCursor)
        row_frame.setFixedHeight(45)
        
        layout = QHBoxLayout(row_frame)
        layout.setContentsMargins(15, 0, 15, 0)
        
        name_lbl = QLabel(name, row_frame)
        name_lbl.setFont(QFont("Outfit", 12, QFont.Bold))
        name_lbl.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
        layout.addWidget(name_lbl)
        
        risk_color = "#E5484D" if risk == "HIGH" else ("#FF7A00" if risk == "MEDIUM" else "#30C48D")
        risk_icon = "🔴" if risk == "HIGH" else ("🟠" if risk == "MEDIUM" else "🟢")
        
        risk_lbl = QLabel(f"{risk_icon} {risk}", row_frame)
        risk_lbl.setFont(QFont("Outfit", 11, QFont.Bold))
        risk_lbl.setStyleSheet(f"color: {risk_color}; background: transparent; border: none;")
        layout.addWidget(risk_lbl)
        
        lhs_lbl = QLabel(f"LHS: {lhs:.0f}%", row_frame)
        lhs_lbl.setFont(QFont("Outfit", 11, QFont.Bold))
        lhs_lbl.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
        layout.addWidget(lhs_lbl)
        
        layout.addStretch(1)
        
        reason_lbl = QLabel(reason, row_frame)
        reason_lbl.setFont(QFont("Outfit", 11))
        reason_lbl.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        layout.addWidget(reason_lbl)

        def mousePressEvent(event):
            if event.button() == Qt.LeftButton:
                self.controller.target_student_id = student_id
                self.controller.switch_to_frame("analytics")
                active_frame = self.controller.workspace.content_stack.currentWidget()
                if hasattr(active_frame, 'sid_entry') and active_frame.sid_entry:
                    active_frame.sid_entry.setText(str(student_id))
                    active_frame.load_student_analytics()
                    self.controller.target_student_id = None
                    
        row_frame.mousePressEvent = mousePressEvent
        self.support_rows_layout.addWidget(row_frame)

    def create_row3_section(self):
        row3_widget = QWidget(self.scroll_content)
        layout = QHBoxLayout(row3_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Left Column: Today's Attendance
        self.attendance_widget = QFrame(row3_widget)
        self.attendance_widget.setObjectName("CardFrame")
        self.attendance_widget.setMinimumHeight(180)
        att_layout = QVBoxLayout(self.attendance_widget)
        att_layout.setContentsMargins(20, 15, 20, 15)
        
        att_title = QLabel("📅 TODAY'S ATTENDANCE", self.attendance_widget)
        att_title.setFont(QFont("Outfit", 13, QFont.Bold))
        att_title.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
        att_layout.addWidget(att_title)
        
        self.attendance_details_frame = QWidget(self.attendance_widget)
        self.attendance_details_layout = QVBoxLayout(self.attendance_details_frame)
        self.attendance_details_layout.setContentsMargins(0, 5, 0, 5)
        att_layout.addWidget(self.attendance_details_frame)
        
        layout.addWidget(self.attendance_widget)
        
        # Right Column: AI Daily Insight
        ai_insight_panel = QFrame(row3_widget)
        ai_insight_panel.setObjectName("CardFrame")
        ai_insight_panel.setMinimumHeight(180)
        ai_layout = QVBoxLayout(ai_insight_panel)
        ai_layout.setContentsMargins(20, 15, 20, 15)
        
        ai_title = QLabel("🤖 AI DAILY INSIGHT", ai_insight_panel)
        ai_title.setFont(QFont("Outfit", 13, QFont.Bold))
        ai_title.setStyleSheet("color: #E5484D; background: transparent; border: none;")
        ai_layout.addWidget(ai_title)
        
        self.ai_insight_txt = QLabel("Today's Priority: Calculating recommendations...", ai_insight_panel)
        self.ai_insight_txt.setFont(QFont("Outfit", 12))
        self.ai_insight_txt.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
        self.ai_insight_txt.setWordWrap(True)
        ai_layout.addWidget(self.ai_insight_txt, 1)
        
        ai_actions = QWidget(ai_insight_panel)
        ai_actions_layout = QHBoxLayout(ai_actions)
        ai_actions_layout.setContentsMargins(0, 0, 0, 0)
        
        btn_analyze = QPushButton("ANALYZE CLASS", ai_actions)
        btn_analyze.setFont(QFont("Outfit", 11, QFont.Bold))
        btn_analyze.clicked.connect(lambda: self.controller.switch_to_frame("analytics"))
        ai_actions_layout.addWidget(btn_analyze)
        
        btn_ask_ai = QPushButton("ASK AI ASSISTANT", ai_actions)
        btn_ask_ai.setObjectName("PrimaryButton")
        btn_ask_ai.setFont(QFont("Outfit", 11, QFont.Bold))
        btn_ask_ai.clicked.connect(lambda: self.controller.switch_to_frame("ai_assistant"))
        ai_actions_layout.addWidget(btn_ask_ai)
        
        ai_layout.addWidget(ai_actions)
        
        layout.addWidget(ai_insight_panel)
        self.scroll_layout.addWidget(row3_widget)

    def create_timeline_section(self):
        timeline_panel = QFrame(self.scroll_content)
        timeline_panel.setObjectName("CardFrame")
        t_layout = QVBoxLayout(timeline_panel)
        t_layout.setContentsMargins(20, 15, 20, 15)
        
        t_title = QLabel("🕒 RECENT ACTIVITY TIMELINE", timeline_panel)
        t_title.setFont(QFont("Outfit", 13, QFont.Bold))
        t_title.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
        t_layout.addWidget(t_title)
        
        self.timeline_container = QWidget(timeline_panel)
        self.timeline_layout = QVBoxLayout(self.timeline_container)
        self.timeline_layout.setContentsMargins(0, 5, 0, 5)
        self.timeline_layout.setSpacing(6)
        t_layout.addWidget(self.timeline_container)
        
        self.scroll_layout.addWidget(timeline_panel)

    def refresh_dashboard(self):
        status = get_db_status()
        self.db_status_lbl.setText(f"● {status['display']}")
        color = "#30C48D" if status["backend"] == "MySQL" else "#F5A524"
        self.db_status_lbl.setStyleSheet(f"color: {color}; background: transparent; border: none;")

        # Update Welcome text if logged in
        if self.controller.current_user:
            self.welcome_text.setText(f"Good Morning, {self.controller.current_user.get('full_name', 'Admin')} 👋")

        # Clear smart actions
        while self.smart_actions_layout.count() > 0:
            item = self.smart_actions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Clear support rows
        while self.support_rows_layout.count() > 0:
            item = self.support_rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Clear attendance details
        while self.attendance_details_layout.count() > 0:
            item = self.attendance_details_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Clear timeline
        while self.timeline_layout.count() > 0:
            item = self.timeline_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Load metrics using the shared core command center & dashboard service
        from core.command_center_service import get_executive_command_center_data
        from core.dashboard_service import get_dashboard_summary
        cmd_data = get_executive_command_center_data()
        data = get_dashboard_summary()

        # Populate Smart Recommended Actions
        smart_actions = cmd_data.get("smart_teacher_actions", [])
        for act in smart_actions:
            sa_row = QFrame(self.smart_actions_container)
            sa_row.setStyleSheet(
                "QFrame { background: #151925; border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 6px 12px; }"
            )
            sr_layout = QHBoxLayout(sa_row)
            sr_layout.setContentsMargins(8, 4, 8, 4)

            prio = act.get("priority", "INFO")
            p_badge = StatusBadge(prio, variant="danger" if prio == "HIGH" else ("warning" if prio == "MEDIUM" else "success"))
            sr_layout.addWidget(p_badge)

            info_w = QWidget(sa_row)
            info_w.setStyleSheet("background: transparent;")
            iw_layout = QVBoxLayout(info_w)
            iw_layout.setContentsMargins(6, 0, 6, 0)
            iw_layout.setSpacing(1)

            t_lbl = QLabel(act.get("title", ""), info_w)
            t_lbl.setFont(QFont("Outfit", 10, QFont.Bold))
            t_lbl.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
            iw_layout.addWidget(t_lbl)

            d_lbl = QLabel(act.get("description", ""), info_w)
            d_lbl.setFont(QFont("Outfit", 9))
            d_lbl.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
            iw_layout.addWidget(d_lbl)
            sr_layout.addWidget(info_w, 1)

            btn_act = QPushButton("Take Action →", sa_row)
            btn_act.setObjectName("PrimaryButton")
            btn_act.setStyleSheet("font-size: 10px; padding: 4px 10px;")
            target_frame = act.get("target", "dashboard")
            def make_click(tgt=target_frame):
                def handler():
                    self.controller.switch_to_frame(tgt)
                return handler
            btn_act.clicked.connect(make_click())
            sr_layout.addWidget(btn_act)

            self.smart_actions_layout.addWidget(sa_row)

        stats = data["stats"]
        needs_attention = data["needs_attention"]
        support_list = data["support_list"]
        today_attendance = data["today_attendance"]
        ai_insight = data["ai_insight"]
        activity_timeline = data["activity_timeline"]


        # Update KPIs using set_value for animated progress bars
        n_students = stats["total_students"]
        self.kpi_students.set_value(str(n_students), min(float(n_students), 100.0))
        self.kpi_performance.set_value(f"{stats['avg_academic']:.1f}%", stats["avg_academic"])
        self.kpi_attendance.set_value(f"{stats['avg_attendance']:.1f}%", stats["avg_attendance"])

        # Wellness Pending smart empty state
        if stats["avg_wellness"] == 0.0 and stats["total_students"] > 0:
            self.kpi_wellness.set_value("Pending", 0.0)
            self.kpi_wellness.trend_lbl.setText("Wellness audit pending")
        else:
            self.kpi_wellness.set_value(f"{stats['avg_wellness']:.1f}%", stats["avg_wellness"])
            healthy = stats["avg_wellness"] >= 70.0
            self.kpi_wellness.trend_lbl.setText("Healthy overall" if healthy else "Declining safety indices")

        # Update Needs Attention values
        # We can dynamically search and update the labels inside alert rows
        # High Risk Row has label index 1, attendance 2, wellness 3. We'll fetch them from na_layout
        for i in range(self.needs_attention_panel.layout().count()):
            widget = self.needs_attention_panel.layout().itemAt(i).widget()
            if widget and hasattr(widget, "layout") and widget.layout():
                # Check labels inside
                lbl_left = widget.layout().itemAt(0).widget()
                lbl_right = widget.layout().itemAt(2).widget()
                if lbl_left and lbl_right:
                    if "High Risk" in lbl_left.text():
                        lbl_right.setText(str(needs_attention["high_risk"]))
                    elif "Low Attendance" in lbl_left.text():
                        lbl_right.setText(str(needs_attention["low_attendance"]))
                    elif "Cyber-Wellness" in lbl_left.text():
                        lbl_right.setText(str(needs_attention["wellness_alerts"]))

        # Render Student Support Rows
        if support_list:
            for item in support_list:
                self.create_row2_student_row(
                    self.support_rows_container, item["student_id"],
                    item["name"], item["risk"], item["lhs"], item["reason"]
                )
        else:
            lbl = QLabel("All students are currently on track! 🟢", self.support_rows_container)
            lbl.setStyleSheet("color: #30C48D; font-weight: bold;")
            lbl.setAlignment(Qt.AlignCenter)
            self.support_rows_layout.addWidget(lbl)

        # Render Today's Attendance Widget (Smart Empty State)
        if not today_attendance["marked"]:
            lbl = QLabel("⚠️ Attendance has not been marked today.", self.attendance_details_frame)
            lbl.setFont(QFont("Outfit", 12, QFont.Bold))
            lbl.setStyleSheet("color: #F5A524;")
            self.attendance_details_layout.addWidget(lbl)

            btn = QPushButton("MARK ATTENDANCE NOW", self.attendance_details_frame)
            btn.setObjectName("PrimaryButton")
            btn.setFont(QFont("Outfit", 11, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda: self.controller.switch_to_frame("attendance"))
            self.attendance_details_layout.addWidget(btn)
        else:
            summary_lbl = QLabel(f"{today_attendance['present']} Present | {today_attendance['absent']} Absent (Class: XII-A)", self.attendance_details_frame)
            summary_lbl.setFont(QFont("Outfit", 12, QFont.Bold))
            summary_lbl.setStyleSheet("color: #F5F7FA;")
            self.attendance_details_layout.addWidget(summary_lbl)

            rate_lbl = QLabel(f"Attendance Rate: {today_attendance['rate']:.1f}%", self.attendance_details_frame)
            rate_lbl.setFont(QFont("Outfit", 13, QFont.Bold))
            rate_lbl.setStyleSheet("color: #30C48D;")
            self.attendance_details_layout.addWidget(rate_lbl)

            pbar = QProgressBar(self.attendance_details_frame)
            pbar.setFixedHeight(10)
            pbar.setMaximum(100)
            pbar.setValue(int(today_attendance["rate"]))
            pbar.setTextVisible(False)
            pbar.setStyleSheet(
                "QProgressBar { background-color: #10131D; border: none; border-radius: 5px; }"
                "QProgressBar::chunk { background-color: #30C48D; border-radius: 5px; }"
            )
            self.attendance_details_layout.addWidget(pbar)

            btn = QPushButton("UPDATE ATTENDANCE", self.attendance_details_frame)
            btn.setFont(QFont("Outfit", 11, QFont.Bold))
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda: self.controller.switch_to_frame("attendance"))
            self.attendance_details_layout.addWidget(btn)

        # Render Trend Chart
        self.load_trend_chart()

        # Set AI Daily Insight
        self.ai_insight_txt.setText(ai_insight)

        # Render timeline activity log
        for act in activity_timeline:
            row = QWidget(self.timeline_container)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(5, 2, 5, 2)
            
            bullet = QLabel("•", row)
            bullet.setFont(QFont("Outfit", 16, QFont.Bold))
            bullet.setStyleSheet("color: #E5484D;")
            row_layout.addWidget(bullet)

            desc = QLabel(str(act["activity"]), row)
            desc.setFont(QFont("Outfit", 12))
            desc.setStyleSheet("color: #F5F7FA;")
            row_layout.addWidget(desc)

            row_layout.addStretch(1)

            time_val = act["activity_time"]
            if time_val and hasattr(time_val, "strftime"):
                time_str = time_val.strftime("%Y-%m-%d %I:%M %p")
            else:
                time_str = str(time_val or "")
            time_lbl = QLabel(time_str, row)
            time_lbl.setFont(QFont("Outfit", 11))
            time_lbl.setStyleSheet("color: #8D96A8;")
            row_layout.addWidget(time_lbl)

            self.timeline_layout.addWidget(row)

    def load_trend_chart(self):
        try:
            from core import graphs
            # Call trend chart generator
            chart_path = graphs.plot_class_performance_trend()
            if os.path.exists(chart_path):
                pixmap = QPixmap(chart_path)
                scaled_pixmap = pixmap.scaled(380, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.chart_display_lbl.setPixmap(scaled_pixmap)
                self.chart_display_lbl.setText("")
            else:
                self.chart_display_lbl.setPixmap(QPixmap())
                self.chart_display_lbl.setText("Not enough data for trend analysis")
        except Exception as e:
            self.chart_display_lbl.setPixmap(QPixmap())
            self.chart_display_lbl.setText(f"Not enough data for trend analysis\n({e})")
