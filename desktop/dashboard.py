"""CustomTkinter dashboard panel acting as PMLA-SCWE's main command center."""

from __future__ import annotations
import os
import datetime
import customtkinter as ctk

from core import student_service
from core.database import get_db_status, execute_select
from PIL import Image


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#0F0F0F")
        self.controller = controller

        # Main scrollable container for maximum responsiveness
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=0, pady=0)
        self.scroll_container.grid_columnconfigure(0, weight=1)
        self.scroll_container.grid_columnconfigure(1, weight=1)

        # 1. Friendly Header Block
        self.create_header_section()

        # 2. Four KPI Cards
        self.create_kpi_section()

        # Row 1 Grid: [Needs Attention] + [Class Performance Trend]
        self.create_row1_section()

        # Row 2 Grid: [Students Needing Support] + [Quick Actions]
        self.create_row2_section()

        # Row 3 Grid: [Today's Attendance] + [AI Daily Insight]
        self.create_row3_section()

        # Bottom Grid: [Recent Activity Timeline]
        self.create_timeline_section()

        # Initial Refresh
        self.refresh_dashboard()

    def create_header_section(self):
        header = ctk.CTkFrame(self.scroll_container, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)

        welcome_text = ctk.CTkLabel(
            header,
            text="Good Morning, Admin 👋",
            font=ctk.CTkFont(family="Outfit", size=22, weight="bold"),
            text_color="#FFFFFF"
        )
        welcome_text.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 2))

        subtitle = ctk.CTkLabel(
            header,
            text="Here's what's happening with your students today.",
            font=ctk.CTkFont(family="Outfit", size=13),
            text_color="#AAAAAA"
        )
        subtitle.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))

        # Right Controls: Database status + Refresh button
        right_controls = ctk.CTkFrame(header, fg_color="transparent")
        right_controls.grid(row=0, column=1, rowspan=2, sticky="e", padx=20)

        self.db_status_lbl = ctk.CTkLabel(
            right_controls,
            text="● MySQL Status",
            font=ctk.CTkFont(family="Outfit", size=12, weight="bold"),
            text_color="#34A853"
        )
        self.db_status_lbl.pack(side="left", padx=10)

        refresh_btn = ctk.CTkButton(
            right_controls,
            text="Refresh Dashboard",
            command=self.refresh_dashboard,
            fg_color="#272727",
            hover_color="#333333",
            text_color="#FFFFFF",
            border_width=1,
            border_color="#3A3A3A",
            width=130,
            font=ctk.CTkFont(family="Outfit", size=11, weight="bold")
        )
        refresh_btn.pack(side="left", padx=5)

    def create_kpi_section(self):
        kpi_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        kpi_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        for c in range(4):
            kpi_frame.grid_columnconfigure(c, weight=1)

        # 4 Clickable KPI cards
        self.kpi_students = self.create_kpi_card(
            kpi_frame, 0, "👨🎓 STUDENTS", "0", "+4 this month",
            lambda: self.controller.switch_to_frame("students")
        )
        self.kpi_performance = self.create_kpi_card(
            kpi_frame, 1, "📊 PERFORMANCE", "0.0%", "↑ 3% vs prev",
            lambda: self.controller.switch_to_frame("analytics")
        )
        self.kpi_attendance = self.create_kpi_card(
            kpi_frame, 2, "📅 ATTENDANCE", "0.0%", "↓ 2% this month",
            lambda: self.controller.switch_to_frame("attendance")
        )
        self.kpi_wellness = self.create_kpi_card(
            kpi_frame, 3, "🛡 CYBER WELLNESS", "0.0%", "Healthy overall",
            lambda: self.controller.switch_to_frame("wellness")
        )

    def create_kpi_card(self, parent, col, title, initial_val, trend_text, click_command) -> tuple[ctk.CTkLabel, ctk.CTkLabel]:
        # Elevated card frame
        card = ctk.CTkFrame(parent, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12, height=100)
        card.grid(row=0, column=col, padx=5, pady=5, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        # Bind hover and click interactions to make it look premium
        def on_enter(e): card.configure(fg_color="#212121", border_color="#E50914")
        def on_leave(e): card.configure(fg_color="#1A1A1A", border_color="#2A2A2A")
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        card.bind("<Button-1>", lambda e: click_command())

        title_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(family="Outfit", size=10, weight="bold"), text_color="#AAAAAA")
        title_lbl.grid(row=0, column=0, padx=15, pady=(15, 2), sticky="w")
        title_lbl.bind("<Button-1>", lambda e: click_command())

        val_lbl = ctk.CTkLabel(card, text=initial_val, font=ctk.CTkFont(family="Outfit", size=24, weight="bold"), text_color="#FFFFFF")
        val_lbl.grid(row=1, column=0, padx=15, pady=(2, 2), sticky="w")
        val_lbl.bind("<Button-1>", lambda e: click_command())

        trend_lbl = ctk.CTkLabel(card, text=trend_text, font=ctk.CTkFont(family="Outfit", size=10), text_color="#717171")
        trend_lbl.grid(row=2, column=0, padx=15, pady=(2, 15), sticky="w")
        trend_lbl.bind("<Button-1>", lambda e: click_command())

        return val_lbl, trend_lbl

    def create_row1_section(self):
        row1 = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        row1.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)

        # Left Panel: Needs Attention
        self.needs_attention_panel = ctk.CTkFrame(row1, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12, height=300)
        self.needs_attention_panel.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        self.needs_attention_panel.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self.needs_attention_panel,
            text="⚠ NEEDS ATTENTION",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold"),
            text_color="#FFD600"
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))

        # Alert Counters inside Needs Attention
        self.high_risk_row = self.create_alert_row(self.needs_attention_panel, 1, "🔴 High Risk Students", "0", lambda: self.controller.switch_to_frame("analytics"))
        self.attendance_alert_row = self.create_alert_row(self.needs_attention_panel, 2, "🟠 Low Attendance Alerts", "0", lambda: self.controller.switch_to_frame("attendance"))
        self.wellness_alert_row = self.create_alert_row(self.needs_attention_panel, 3, "🟡 Cyber-Wellness Alerts", "0", lambda: self.controller.switch_to_frame("wellness"))

        view_all_alerts_btn = ctk.CTkButton(
            self.needs_attention_panel,
            text="VIEW ALL ALERTS →",
            command=lambda: self.controller.switch_to_frame("analytics"),
            fg_color="transparent",
            hover_color="#272727",
            text_color="#FF4D4D",
            font=ctk.CTkFont(family="Outfit", size=11, weight="bold")
        )
        view_all_alerts_btn.grid(row=4, column=0, sticky="w", padx=20, pady=(10, 15))

        # Right Panel: Class Performance Trend Chart
        self.chart_panel = ctk.CTkFrame(row1, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12, height=300)
        self.chart_panel.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        self.chart_panel.grid_columnconfigure(0, weight=1)

        chart_title = ctk.CTkLabel(
            self.chart_panel,
            text="📊 CLASS PERFORMANCE TREND",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold"),
            text_color="#FFFFFF"
        )
        chart_title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))

        # Placeholder/Canvas for Matplotlib trend
        self.chart_display_lbl = ctk.CTkLabel(
            self.chart_panel,
            text="Generating progress trends...",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold"),
            text_color="#717171"
        )
        self.chart_display_lbl.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        view_analytics_btn = ctk.CTkButton(
            self.chart_panel,
            text="VIEW FULL ANALYTICS →",
            command=lambda: self.controller.switch_to_frame("analytics"),
            fg_color="transparent",
            hover_color="#272727",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=11, weight="bold")
        )
        view_analytics_btn.grid(row=2, column=0, sticky="w", padx=20, pady=(5, 15))

    def create_alert_row(self, parent, row_idx, label_text, count_val, click_cmd) -> ctk.CTkLabel:
        row_frame = ctk.CTkFrame(parent, fg_color="#212121", height=45, corner_radius=6)
        row_frame.grid(row=row_idx, column=0, padx=20, pady=5, sticky="ew")
        row_frame.grid_columnconfigure(0, weight=1)

        def on_enter(e): row_frame.configure(fg_color="#272727")
        def on_leave(e): row_frame.configure(fg_color="#212121")
        row_frame.bind("<Enter>", on_enter)
        row_frame.bind("<Leave>", on_leave)
        row_frame.bind("<Button-1>", lambda e: click_cmd())

        lbl = ctk.CTkLabel(row_frame, text=label_text, font=ctk.CTkFont(family="Outfit", size=13, weight="bold"), text_color="#FFFFFF")
        lbl.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        lbl.bind("<Button-1>", lambda e: click_cmd())

        cnt = ctk.CTkLabel(row_frame, text=count_val, font=ctk.CTkFont(family="Outfit", size=15, weight="bold"), text_color="#FFFFFF")
        cnt.grid(row=0, column=1, padx=15, pady=8, sticky="e")
        cnt.bind("<Button-1>", lambda e: click_cmd())

        return cnt

    def create_row2_student_row(self, parent, row_idx, student_id, name, risk, lhs, reason):
        row_frame = ctk.CTkFrame(parent, fg_color="#181818", corner_radius=6, height=45)
        row_frame.pack(fill="x", padx=0, pady=4)
        row_frame.grid_columnconfigure(0, weight=1)

        # Color-coded risk badge
        risk_color = "#FF0000" if risk == "HIGH" else ("#FF7A00" if risk == "MEDIUM" else "#34A853")
        risk_icon = "🔴" if risk == "HIGH" else ("🟠" if risk == "MEDIUM" else "🟢")

        # Clicks navigate straight to analytics for this student!
        def open_student_analytics():
            self.controller.target_student_id = student_id
            self.controller.switch_to_frame("analytics")
            # Automatically load it in active frame if it has the loader hook!
            if hasattr(self.controller.active_frame, 'sid_entry') and self.controller.active_frame.sid_entry:
                self.controller.active_frame.sid_entry.delete(0, 'end')
                self.controller.active_frame.sid_entry.insert(0, str(student_id))
                self.controller.active_frame.load_student_analytics()
                self.controller.target_student_id = None

        def on_enter(e): row_frame.configure(fg_color="#212121")
        def on_leave(e): row_frame.configure(fg_color="#181818")
        row_frame.bind("<Enter>", on_enter)
        row_frame.bind("<Leave>", on_leave)
        row_frame.bind("<Button-1>", lambda e: open_student_analytics())

        name_lbl = ctk.CTkLabel(row_frame, text=name, font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#FFFFFF")
        name_lbl.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        name_lbl.bind("<Button-1>", lambda e: open_student_analytics())

        risk_lbl = ctk.CTkLabel(row_frame, text=f"{risk_icon} {risk}", font=ctk.CTkFont(family="Outfit", size=11, weight="bold"), text_color=risk_color)
        risk_lbl.grid(row=0, column=1, padx=10, pady=8, sticky="w")
        risk_lbl.bind("<Button-1>", lambda e: open_student_analytics())

        lhs_lbl = ctk.CTkLabel(row_frame, text=f"LHS: {lhs:.0f}%", font=ctk.CTkFont(family="Outfit", size=11, weight="bold"), text_color="#FFFFFF")
        lhs_lbl.grid(row=0, column=2, padx=10, pady=8, sticky="w")
        lhs_lbl.bind("<Button-1>", lambda e: open_student_analytics())

        reason_lbl = ctk.CTkLabel(row_frame, text=reason, font=ctk.CTkFont(family="Outfit", size=11), text_color="#AAAAAA")
        reason_lbl.grid(row=0, column=3, padx=15, pady=8, sticky="e")
        reason_lbl.bind("<Button-1>", lambda e: open_student_analytics())

    def create_row2_section(self):
        row2 = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        row2.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=1)

        # Left Column: Students Needing Support
        self.support_panel = ctk.CTkFrame(row2, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        self.support_panel.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        self.support_panel.grid_columnconfigure(0, weight=1)

        support_title = ctk.CTkLabel(
            self.support_panel,
            text="👥 STUDENTS NEEDING SUPPORT",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold"),
            text_color="#FFFFFF"
        )
        support_title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))

        self.support_rows_container = ctk.CTkFrame(self.support_panel, fg_color="transparent")
        self.support_rows_container.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        view_all_students_btn = ctk.CTkButton(
            self.support_panel,
            text="VIEW ALL STUDENTS →",
            command=lambda: self.controller.switch_to_frame("students"),
            fg_color="transparent",
            hover_color="#272727",
            text_color="#AAAAAA",
            font=ctk.CTkFont(family="Outfit", size=11, weight="bold")
        )
        view_all_students_btn.grid(row=2, column=0, sticky="w", padx=20, pady=(10, 15))

        # Right Column: Quick Actions
        quick_actions_panel = ctk.CTkFrame(row2, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        quick_actions_panel.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        quick_actions_panel.grid_columnconfigure(0, weight=1)

        qa_title = ctk.CTkLabel(
            quick_actions_panel,
            text="⚡ QUICK ACTIONS",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold"),
            text_color="#FFFFFF"
        )
        qa_title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))

        # Quick Actions button list
        self.create_action_btn(quick_actions_panel, 1, "👤 Register New Student", lambda: self.controller.switch_to_frame("students"))
        self.create_action_btn(quick_actions_panel, 2, "✓ Mark Attendance Registry", lambda: self.controller.switch_to_frame("attendance"))
        self.create_action_btn(quick_actions_panel, 3, "📝 Add Academic Assessment", lambda: self.controller.switch_to_frame("assessments"))
        self.create_action_btn(quick_actions_panel, 4, "🛡 Lodge Cyber Wellness Audit", lambda: self.controller.switch_to_frame("wellness"))
        self.create_action_btn(quick_actions_panel, 5, "🤖 Ask AI Decision Assistant", lambda: self.controller.switch_to_frame("ai_assistant"))

    def create_action_btn(self, parent, idx, text, action_cmd):
        btn = ctk.CTkButton(
            parent,
            text=text,
            command=action_cmd,
            fg_color="#212121",
            hover_color="#272727",
            text_color="#FFFFFF",
            anchor="w",
            height=40,
            border_width=1,
            border_color="#2A2A2A",
            font=ctk.CTkFont(family="Outfit", size=12, weight="bold")
        )
        btn.grid(row=idx, column=0, padx=20, pady=5, sticky="ew")

    def create_row3_section(self):
        row3 = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        row3.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        row3.grid_columnconfigure(0, weight=1)
        row3.grid_columnconfigure(1, weight=1)

        # Left Column: Today's Attendance
        self.attendance_widget = ctk.CTkFrame(row3, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12, height=180)
        self.attendance_widget.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        self.attendance_widget.grid_columnconfigure(0, weight=1)

        att_title = ctk.CTkLabel(
            self.attendance_widget,
            text="📅 TODAY'S ATTENDANCE",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold"),
            text_color="#FFFFFF"
        )
        att_title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))

        # Dynamic inner container for marked vs pending
        self.attendance_details_frame = ctk.CTkFrame(self.attendance_widget, fg_color="transparent")
        self.attendance_details_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.attendance_details_frame.grid_columnconfigure(0, weight=1)

        # Right Column: AI Daily Insight
        ai_insight_panel = ctk.CTkFrame(row3, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12, height=180)
        ai_insight_panel.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nsew")
        ai_insight_panel.grid_columnconfigure(0, weight=1)

        ai_title = ctk.CTkLabel(
            ai_insight_panel,
            text="🤖 AI DAILY INSIGHT",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold"),
            text_color="#FF4D4D"
        )
        ai_title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))

        self.ai_insight_txt = ctk.CTkLabel(
            ai_insight_panel,
            text="Today's Priority: Calculating recommendations...",
            font=ctk.CTkFont(family="Outfit", size=12),
            text_color="#E5E5E5",
            wraplength=350,
            justify="left"
        )
        self.ai_insight_txt.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        ai_actions = ctk.CTkFrame(ai_insight_panel, fg_color="transparent")
        ai_actions.grid(row=2, column=0, sticky="w", padx=20, pady=(5, 15))

        btn_analyze = ctk.CTkButton(
            ai_actions,
            text="ANALYZE CLASS",
            command=lambda: self.controller.switch_to_frame("analytics"),
            fg_color="#272727",
            hover_color="#333333",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=11, weight="bold"),
            width=120
        )
        btn_analyze.pack(side="left", padx=(0, 10))

        btn_ask_ai = ctk.CTkButton(
            ai_actions,
            text="ASK AI ASSISTANT",
            command=lambda: self.controller.switch_to_frame("ai_assistant"),
            fg_color="#E50914",
            hover_color="#CC0000",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=11, weight="bold"),
            width=130
        )
        btn_ask_ai.pack(side="left")

    def create_timeline_section(self):
        timeline_panel = ctk.CTkFrame(self.scroll_container, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        timeline_panel.grid(row=5, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 20))
        timeline_panel.grid_columnconfigure(0, weight=1)

        t_title = ctk.CTkLabel(
            timeline_panel,
            text="🕒 RECENT ACTIVITY TIMELINE",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold"),
            text_color="#FFFFFF"
        )
        t_title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))

        self.timeline_container = ctk.CTkFrame(timeline_panel, fg_color="transparent")
        self.timeline_container.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        self.timeline_container.grid_columnconfigure(0, weight=1)

    def refresh_dashboard(self):
        # Refresh header db status tag
        status = get_db_status()
        self.db_status_lbl.configure(text=f"● {status['display']}")
        color = "#34A853" if status["backend"] == "MySQL" else "#FFD600"
        self.db_status_lbl.configure(text_color=color)

        # Clear scroll frame rows
        for w in self.support_rows_container.winfo_children():
            w.destroy()
        for w in self.attendance_details_frame.winfo_children():
            w.destroy()
        for w in self.timeline_container.winfo_children():
            w.destroy()

        # Load metrics using the shared core dashboard service
        from core.dashboard_service import get_dashboard_summary
        data = get_dashboard_summary()

        stats = data["stats"]
        needs_attention = data["needs_attention"]
        support_list = data["support_list"]
        today_attendance = data["today_attendance"]
        ai_insight = data["ai_insight"]
        activity_timeline = data["activity_timeline"]

        # Update KPIs
        self.kpi_students[0].configure(text=str(stats["total_students"]))
        self.kpi_performance[0].configure(text=f"{stats['avg_academic']:.1f}%")
        self.kpi_attendance[0].configure(text=f"{stats['avg_attendance']:.1f}%")
        
        # Wellness Pending smart empty state
        if stats["avg_wellness"] == 0.0 and stats["total_students"] > 0:
            self.kpi_wellness[0].configure(text="Pending")
            self.kpi_wellness[1].configure(text="Wellness audit pending")
        else:
            self.kpi_wellness[0].configure(text=f"{stats['avg_wellness']:.1f}%")
            self.kpi_wellness[1].configure(text="Healthy overall" if stats["avg_wellness"] >= 70.0 else "Declining safety indices")

        # Update Needs Attention values
        self.high_risk_row.configure(text=str(needs_attention["high_risk"]))
        self.attendance_alert_row.configure(text=str(needs_attention["low_attendance"]))
        self.wellness_alert_row.configure(text=str(needs_attention["wellness_alerts"]))

        # Render Student Support Rows
        if support_list:
            for idx, item in enumerate(support_list):
                self.create_row2_student_row(
                    self.support_rows_container, idx, item["student_id"],
                    item["name"], item["risk"], item["lhs"], item["reason"]
                )
        else:
            lbl = ctk.CTkLabel(self.support_rows_container, text="All students are currently on track! 🟢", text_color="#34A853", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"))
            lbl.pack(pady=15)

        # Render Today's Attendance Widget (Smart Empty State)
        if not today_attendance["marked"]:
            lbl = ctk.CTkLabel(
                self.attendance_details_frame,
                text="⚠ Attendance has not been marked today.",
                font=ctk.CTkFont(family="Outfit", size=12, weight="bold"),
                text_color="#FFD600"
            )
            lbl.pack(anchor="w", pady=(5, 10))

            btn = ctk.CTkButton(
                self.attendance_details_frame,
                text="MARK ATTENDANCE NOW",
                command=lambda: self.controller.switch_to_frame("attendance"),
                fg_color="#E50914",
                hover_color="#CC0000",
                text_color="#FFFFFF",
                font=ctk.CTkFont(family="Outfit", size=11, weight="bold")
            )
            btn.pack(anchor="w")
        else:
            summary_lbl = ctk.CTkLabel(
                self.attendance_details_frame,
                text=f"{today_attendance['present']} Present | {today_attendance['absent']} Absent (Class: XII-A)",
                font=ctk.CTkFont(family="Outfit", size=12, weight="bold"),
                text_color="#FFFFFF"
            )
            summary_lbl.pack(anchor="w", pady=(0, 2))

            rate_lbl = ctk.CTkLabel(
                self.attendance_details_frame,
                text=f"Attendance Rate: {today_attendance['rate']:.1f}%",
                font=ctk.CTkFont(family="Outfit", size=13, weight="bold"),
                text_color="#34A853"
            )
            rate_lbl.pack(anchor="w", pady=(0, 8))

            # Progress bar matching rate
            pbar = ctk.CTkProgressBar(self.attendance_details_frame, fg_color="#212121", progress_color="#34A853", height=10)
            pbar.pack(fill="x", pady=2)
            pbar.set(today_attendance["rate"] / 100.0)

            btn = ctk.CTkButton(
                self.attendance_details_frame,
                text="UPDATE ATTENDANCE",
                command=lambda: self.controller.switch_to_frame("attendance"),
                fg_color="#272727",
                hover_color="#333333",
                text_color="#FFFFFF",
                font=ctk.CTkFont(family="Outfit", size=11, weight="bold"),
                width=150
            )
            btn.pack(anchor="w", pady=(8, 0))

        # Render Trend Chart
        self.load_trend_chart()

        # Set AI Daily Insight
        self.ai_insight_txt.configure(text=ai_insight)

        # Render timeline activity log
        for idx, act in enumerate(activity_timeline):
            row = ctk.CTkFrame(self.timeline_container, fg_color="transparent", height=30)
            row.pack(fill="x", pady=2)
            
            bullet = ctk.CTkLabel(row, text="•", font=ctk.CTkFont(size=16, weight="bold"), text_color="#E50914")
            bullet.pack(side="left", padx=(5, 10))

            desc = ctk.CTkLabel(row, text=act["activity"], font=ctk.CTkFont(family="Outfit", size=12), text_color="#FFFFFF")
            desc.pack(side="left")

            time_lbl = ctk.CTkLabel(row, text=act["activity_time"], font=ctk.CTkFont(family="Outfit", size=11), text_color="#717171")
            time_lbl.pack(side="right", padx=10)

    def load_trend_chart(self):
        try:
            from core import graphs
            # Call trend chart generator
            chart_path = graphs.plot_class_performance_trend()
            if os.path.exists(chart_path):
                img = Image.open(chart_path)
                # Fit inside right panel space
                img_resized = img.resize((380, 200))
                self.chart_img = ctk.CTkImage(light_image=img_resized, dark_image=img_resized, size=(380, 200))
                self.chart_display_lbl.configure(image=self.chart_img, text="")
            else:
                self.chart_display_lbl.configure(text="Not enough data for trend analysis", image=None)
        except Exception as e:
            self.chart_display_lbl.configure(text=f"Not enough data for trend analysis\n({e})", image=None)
