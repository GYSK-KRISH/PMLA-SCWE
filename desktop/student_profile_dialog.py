"""PySide6 dialog for the Student 360° Intelligence Profile.

Version 1.2 — Student 360° Intelligence Profile
Presents comprehensive academic, attendance, progress, wellness, predictive,
explainable insights, deterministic interventions, and chronological timeline.
"""

from __future__ import annotations
from typing import Any
from PySide6.QtWidgets import (
    QDialog, QWidget, QFrame, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QScrollArea, QCheckBox, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from core.student_profile_service import get_student_360_profile
from desktop.widgets.animated_card import AnimatedCard
from desktop.widgets.reusable_ui_components import (
    SectionHeader, StatusBadge, AnimatedProgressBar, InfoRow, EmptyState
)


class StudentProfileDialog(QDialog):
    """Scrollable modal dialog rendering the complete Student 360° Profile."""

    def __init__(self, parent: QWidget | None, student_id: int):
        super().__init__(parent)
        self.student_id = student_id
        self.setWindowTitle(f"Student 360° Intelligence Profile — #{student_id}")
        self.resize(920, 720)
        self.setMinimumSize(850, 600)
        self.setStyleSheet(
            "QDialog { background-color: #080A12; color: #F5F7FA; }"
            "QLabel { color: #F5F7FA; background: transparent; }"
            "QScrollArea { border: none; background: transparent; }"
        )

        # Main vertical layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(12)

        # Top Action Bar
        top_bar = QWidget(self)
        top_bar.setStyleSheet("background: transparent;")
        tb_layout = QHBoxLayout(top_bar)
        tb_layout.setContentsMargins(0, 0, 0, 0)

        back_btn = QPushButton("← Close Profile", top_bar)
        back_btn.setFont(QFont("Outfit", 11, QFont.Bold))
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.clicked.connect(self.accept)
        tb_layout.addWidget(back_btn)

        title_lbl = QLabel("STUDENT 360° INTELLIGENCE PROFILE", top_bar)
        title_lbl.setFont(QFont("Outfit", 12, QFont.Bold))
        title_lbl.setStyleSheet("color: #8D96A8; letter-spacing: 1px;")
        tb_layout.addWidget(title_lbl)
        tb_layout.addStretch(1)

        root_layout.addWidget(top_bar)

        # Scroll Area for the Profile
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setObjectName("CardFrame")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        self.content_layout.setSpacing(16)
        scroll.setWidget(self.content_widget)

        root_layout.addWidget(scroll, 1)

        # Load Profile Data
        self.load_profile()

    def load_profile(self) -> None:
        profile = get_student_360_profile(self.student_id)
        if not profile:
            empty = EmptyState(
                icon="⚠️",
                title="Student Profile Not Found",
                description=f"No database records could be located for Student ID #{self.student_id}.",
                action_text="Close",
                action_callback=self.accept,
                parent=self.content_widget
            )
            self.content_layout.addWidget(empty)
            return

        s = profile["student"]
        status = profile["profile_status"]
        lh = profile["learning_health"]
        acad = profile["academic"]
        att = profile["attendance"]
        prog = profile["weekly_progress"]
        well = profile["wellness"]
        pred = profile["prediction"]
        insights = profile["insights"]
        interventions = profile["interventions"]
        timeline = profile["timeline"]

        # -------------------------------------------------------------------
        # 1. Profile Header Card
        # -------------------------------------------------------------------
        header_card = QFrame(self.content_widget)
        header_card.setObjectName("CardFrame")
        header_card.setStyleSheet(
            "QFrame#CardFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #151925, stop:1 #1A1F30);"
            " border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; }"
        )
        hc_layout = QHBoxLayout(header_card)
        hc_layout.setContentsMargins(20, 16, 20, 16)
        hc_layout.setSpacing(16)

        # Avatar circle
        initials = (s["first_name"][:1] + s["last_name"][:1]).upper() or "S"
        avatar = QLabel(initials, header_card)
        avatar.setFixedSize(56, 56)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFont(QFont("Outfit", 18, QFont.Bold))
        avatar.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7C5CFF, stop:1 #4D8DFF);"
            "color: #FFFFFF; border-radius: 28px;"
        )
        hc_layout.addWidget(avatar)

        # Name & Demographics
        name_box = QWidget(header_card)
        name_box.setStyleSheet("background: transparent;")
        nb_layout = QVBoxLayout(name_box)
        nb_layout.setContentsMargins(0, 0, 0, 0)
        nb_layout.setSpacing(3)

        name_lbl = QLabel(s["name"], name_box)
        name_lbl.setFont(QFont("Outfit", 18, QFont.Bold))
        name_lbl.setStyleSheet("color: #FFFFFF; font-weight: 800;")
        nb_layout.addWidget(name_lbl)

        demo_text = f"ID: {s['id']}  •  Class {s['class_section']}  •  Enrolled: {s['enrollment_date'] or 'N/A'}"
        demo_lbl = QLabel(demo_text, name_box)
        demo_lbl.setFont(QFont("Outfit", 11))
        demo_lbl.setStyleSheet("color: #8D96A8;")
        nb_layout.addWidget(demo_lbl)

        hc_layout.addWidget(name_box)
        hc_layout.addStretch(1)

        # Risk & LHS Badges
        badges_box = QWidget(header_card)
        badges_box.setStyleSheet("background: transparent;")
        bb_layout = QVBoxLayout(badges_box)
        bb_layout.setContentsMargins(0, 0, 0, 0)
        bb_layout.setSpacing(6)
        bb_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        risk_val = lh.get("risk_level", "PENDING")
        risk_variant = "danger" if risk_val == "HIGH" else ("warning" if risk_val == "MEDIUM" else ("success" if risk_val == "LOW" else "muted"))
        risk_badge = StatusBadge(f"● {risk_val} RISK", variant=risk_variant, parent=badges_box)
        bb_layout.addWidget(risk_badge, alignment=Qt.AlignRight)

        lhs_text = f"LHS: {lh.get('display', 'N/A')}"
        lhs_badge = StatusBadge(lhs_text, variant="purple" if lh.get("has_data") else "muted", parent=badges_box)
        bb_layout.addWidget(lhs_badge, alignment=Qt.AlignRight)

        hc_layout.addWidget(badges_box)
        self.content_layout.addWidget(header_card)

        # -------------------------------------------------------------------
        # 2. Data Intelligence / Completeness Banner
        # -------------------------------------------------------------------
        data_comp = status.get("data_completeness", 0)
        conf_level = status.get("confidence_level", "Insufficient Data")
        
        comp_frame = QFrame(self.content_widget)
        comp_frame.setObjectName("InnerCardFrame")
        cf_layout = QHBoxLayout(comp_frame)
        cf_layout.setContentsMargins(16, 10, 16, 10)
        cf_layout.setSpacing(12)

        comp_icon = QLabel("📊", comp_frame)
        comp_icon.setFont(QFont("Segoe UI Emoji", 14))
        cf_layout.addWidget(comp_icon)

        comp_txt = QLabel(f"Data Completeness: <b>{data_comp}%</b> ({conf_level})", comp_frame)
        comp_txt.setFont(QFont("Outfit", 11))
        comp_txt.setStyleSheet("color: #8D96A8;")
        cf_layout.addWidget(comp_txt)

        cf_layout.addSpacing(10)
        
        comp_bar = AnimatedProgressBar(value=float(data_comp), variant="purple", bar_height=6, animate=True, parent=comp_frame)
        cf_layout.addWidget(comp_bar, 1)

        self.content_layout.addWidget(comp_frame)

        # -------------------------------------------------------------------
        # 3. Learning Health Score Breakdown Card
        # -------------------------------------------------------------------
        lhs_card = AnimatedCard(self.content_widget)
        lhs_layout = QVBoxLayout(lhs_card)
        lhs_layout.setContentsMargins(20, 16, 20, 16)
        lhs_layout.setSpacing(12)

        lhs_header = SectionHeader(
            "LEARNING HEALTH SCORE BREAKDOWN",
            subtitle=f"{lh.get('display', 'N/A')} — {lh.get('label', '')}",
            badge_text=f"{lh.get('score', '0')}%" if lh.get("has_data") else "Pending",
            badge_variant="purple" if lh.get("has_data") else "muted",
            parent=lhs_card
        )
        lhs_layout.addWidget(lhs_header)

        # Breakdown bars grid
        comps = lh.get("components", {})
        grid_widget = QWidget(lhs_card)
        grid_widget.setStyleSheet("background: transparent;")
        gw_layout = QGridLayout(grid_widget)
        gw_layout.setContentsMargins(0, 4, 0, 4)
        gw_layout.setHorizontalSpacing(20)
        gw_layout.setVerticalSpacing(10)

        row_idx = 0
        comp_meta = [
            ("academic", "Academic Performance (40%)", "purple"),
            ("progress", "Weekly Progress Trend (25%)", "blue"),
            ("attendance", "Attendance Consistency (20%)", "success"),
            ("wellness", "Cyber-Wellbeing Index (15%)", "warning"),
        ]

        for key, label, variant in comp_meta:
            c = comps.get(key, {})
            has_d = c.get("has_data", False)
            score_val = c.get("score")
            
            lbl = QLabel(label, grid_widget)
            lbl.setFont(QFont("Outfit", 11, QFont.Bold))
            lbl.setStyleSheet("color: #F5F7FA;")
            gw_layout.addWidget(lbl, row_idx, 0)

            score_txt = QLabel(c.get("display", "N/A"), grid_widget)
            score_txt.setFont(QFont("Outfit", 11, QFont.Bold))
            score_txt.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            score_txt.setStyleSheet("color: #8D96A8;" if not has_d else "color: #F5F7FA;")
            gw_layout.addWidget(score_txt, row_idx, 1)

            pbar = AnimatedProgressBar(
                value=float(score_val) if has_d and score_val is not None else 0.0,
                variant=variant if has_d else "red",
                bar_height=6,
                animate=has_d,
                parent=grid_widget
            )
            gw_layout.addWidget(pbar, row_idx + 1, 0, 1, 2)
            row_idx += 2

        lhs_layout.addWidget(grid_widget)
        self.content_layout.addWidget(lhs_card)

        # -------------------------------------------------------------------
        # 4. Split Row: Academic & Attendance
        # -------------------------------------------------------------------
        split_1 = QWidget(self.content_widget)
        split_1.setStyleSheet("background: transparent;")
        s1_layout = QHBoxLayout(split_1)
        s1_layout.setContentsMargins(0, 0, 0, 0)
        s1_layout.setSpacing(14)

        # Academic Card
        acad_card = AnimatedCard(split_1)
        ac_layout = QVBoxLayout(acad_card)
        ac_layout.setContentsMargins(16, 14, 16, 14)
        ac_layout.setSpacing(10)

        ac_header = SectionHeader("ACADEMIC PERFORMANCE", badge_text=acad.get("status", "N/A"), badge_variant="purple", parent=acad_card)
        ac_layout.addWidget(ac_header)

        if acad.get("has_data"):
            ac_layout.addWidget(InfoRow("Avg Score:", acad.get("display", "N/A"), parent=acad_card))
            ac_layout.addWidget(InfoRow("Total Tests:", str(acad.get("total_assessments", 0)), parent=acad_card))
            ac_layout.addWidget(InfoRow("Best Score:", str(acad.get("best_subject", "N/A")), parent=acad_card))
            ac_layout.addWidget(InfoRow("Needs Review:", str(acad.get("weakest_subject", "N/A")), parent=acad_card))
        else:
            ac_layout.addWidget(EmptyState(icon="📝", title="No Diagnostic Logs", description="No test records logged for this student yet.", parent=acad_card))

        s1_layout.addWidget(acad_card, 1)

        # Attendance Card
        att_card = AnimatedCard(split_1)
        at_layout = QVBoxLayout(att_card)
        at_layout.setContentsMargins(16, 14, 16, 14)
        at_layout.setSpacing(10)

        att_header = SectionHeader("ATTENDANCE REGISTRY", badge_text=att.get("status", "N/A"), badge_variant="success" if att.get("percentage", 0) and att["percentage"] >= 85 else "danger", parent=att_card)
        at_layout.addWidget(att_header)

        if att.get("has_data"):
            at_layout.addWidget(InfoRow("Rate:", att.get("display", "N/A"), parent=att_card))
            at_layout.addWidget(InfoRow("Present Days:", str(att.get("present_count", 0)), parent=att_card))
            at_layout.addWidget(InfoRow("Absent Days:", str(att.get("absent_count", 0)), parent=att_card))
            at_layout.addWidget(InfoRow("Total Marked:", f"{att.get('total_days', 0)} sessions", parent=att_card))
        else:
            at_layout.addWidget(EmptyState(icon="📅", title="No Attendance Logs", description="No attendance records recorded yet.", parent=att_card))

        s1_layout.addWidget(att_card, 1)
        self.content_layout.addWidget(split_1)

        # -------------------------------------------------------------------
        # 5. Split Row: Cyber-Wellbeing & Predictive Forecast
        # -------------------------------------------------------------------
        split_2 = QWidget(self.content_widget)
        split_2.setStyleSheet("background: transparent;")
        s2_layout = QHBoxLayout(split_2)
        s2_layout.setContentsMargins(0, 0, 0, 0)
        s2_layout.setSpacing(14)

        # Wellness Card
        well_card = AnimatedCard(split_2)
        wc_layout = QVBoxLayout(well_card)
        wc_layout.setContentsMargins(16, 14, 16, 14)
        wc_layout.setSpacing(10)

        well_header = SectionHeader("CYBER-WELLBEING AUDIT", badge_text=well.get("status_label", "N/A"), badge_variant="warning" if well.get("status") == "Concern" else "success", parent=well_card)
        wc_layout.addWidget(well_header)

        if well.get("has_data"):
            wc_layout.addWidget(InfoRow("Wellness Index:", well.get("display", "N/A"), parent=well_card))
            wc_layout.addWidget(InfoRow("Daily Screen:", f"{well.get('daily_screen_time', 0):.1f} hrs/day", parent=well_card))
            wc_layout.addWidget(InfoRow("Study Screen:", f"{well.get('study_screen_time', 0):.1f} hrs", parent=well_card))
            wc_layout.addWidget(InfoRow("Sleep Duration:", f"{well.get('sleep_duration', 0):.1f} hrs", parent=well_card))
        else:
            wc_layout.addWidget(EmptyState(icon="🛡️", title="Audit Pending", description="No cyber-wellness audits recorded for this student.", parent=well_card))

        s2_layout.addWidget(well_card, 1)

        # Prediction Card
        pred_card = AnimatedCard(split_2)
        pc_layout = QVBoxLayout(pred_card)
        pc_layout.setContentsMargins(16, 14, 16, 14)
        pc_layout.setSpacing(10)

        pred_header = SectionHeader("PREDICTIVE FORECAST", badge_text=pred.get("trend_direction", "Stable"), badge_variant="blue" if pred.get("trend_direction") == "Improving" else "warning", parent=pred_card)
        pc_layout.addWidget(pred_header)

        if pred.get("has_data"):
            pc_layout.addWidget(InfoRow("Forecast Score:", pred.get("display", "N/A"), parent=pred_card))
            pc_layout.addWidget(InfoRow("Recent Score:", f"{pred.get('current_score', 0):.1f}%", parent=pred_card))
            pc_layout.addWidget(InfoRow("Trend Trajectory:", pred.get("trend_direction", "Stable"), parent=pred_card))
            
            conf_lbl = QLabel(pred.get("confidence_text", ""), pred_card)
            conf_lbl.setFont(QFont("Outfit", 10))
            conf_lbl.setStyleSheet("color: #8D96A8; font-style: italic;")
            conf_lbl.setWordWrap(True)
            pc_layout.addWidget(conf_lbl)
        else:
            pc_layout.addWidget(EmptyState(icon="📈", title="Insufficient Trend Data", description="Requires at least 2 weekly progress entries.", parent=pred_card))

        s2_layout.addWidget(pred_card, 1)
        self.content_layout.addWidget(split_2)

        # -------------------------------------------------------------------
        # 6. Explainable Insights ("Why does this student need attention?")
        # -------------------------------------------------------------------
        insights_card = AnimatedCard(self.content_widget)
        ic_layout = QVBoxLayout(insights_card)
        ic_layout.setContentsMargins(20, 16, 20, 16)
        ic_layout.setSpacing(10)

        ic_header = SectionHeader("EXPLAINABLE INTELLIGENCE INSIGHTS", subtitle="Why does this student require attention?", parent=insights_card)
        ic_layout.addWidget(ic_header)

        if insights:
            for item in insights:
                row = QWidget(insights_card)
                row.setStyleSheet("background: transparent;")
                rl = QHBoxLayout(row)
                rl.setContentsMargins(0, 2, 0, 2)
                rl.setSpacing(8)

                bullet = QLabel("•", row)
                bullet.setFont(QFont("Outfit", 14, QFont.Bold))
                bullet.setStyleSheet("color: #7C5CFF;")
                rl.addWidget(bullet)

                txt = QLabel(item, row)
                txt.setFont(QFont("Outfit", 12))
                txt.setStyleSheet("color: #F5F7FA;")
                txt.setWordWrap(True)
                rl.addWidget(txt, 1)

                ic_layout.addWidget(row)
        else:
            ic_layout.addWidget(QLabel("No critical concerns flagged for this profile.", insights_card))

        self.content_layout.addWidget(insights_card)

        # -------------------------------------------------------------------
        # 7. Recommended Teacher Interventions Checklist
        # -------------------------------------------------------------------
        action_card = AnimatedCard(self.content_widget)
        ac_layout = QVBoxLayout(action_card)
        ac_layout.setContentsMargins(20, 16, 20, 16)
        ac_layout.setSpacing(12)

        ac_header = SectionHeader("RECOMMENDED INTERVENTION ACTION PLAN", subtitle="Deterministic teacher follow-up checklist", parent=action_card)
        ac_layout.addWidget(ac_header)

        if interventions:
            for iv in interventions:
                row_frame = QFrame(action_card)
                row_frame.setObjectName("InnerCardFrame")
                row_frame.setStyleSheet("background-color: #10131D; border-radius: 8px; padding: 6px;")
                rf_layout = QHBoxLayout(row_frame)
                rf_layout.setContentsMargins(10, 8, 10, 8)
                rf_layout.setSpacing(12)

                cb = QCheckBox(row_frame)
                cb.setCursor(Qt.PointingHandCursor)
                rf_layout.addWidget(cb)

                txt_box = QWidget(row_frame)
                txt_box.setStyleSheet("background: transparent;")
                tb_l = QVBoxLayout(txt_box)
                tb_l.setContentsMargins(0, 0, 0, 0)
                tb_l.setSpacing(2)

                t_lbl = QLabel(iv["title"], txt_box)
                t_lbl.setFont(QFont("Outfit", 12, QFont.Bold))
                t_lbl.setStyleSheet("color: #F5F7FA;")
                tb_l.addWidget(t_lbl)

                d_lbl = QLabel(iv["description"], txt_box)
                d_lbl.setFont(QFont("Outfit", 11))
                d_lbl.setStyleSheet("color: #8D96A8;")
                d_lbl.setWordWrap(True)
                tb_l.addWidget(d_lbl)

                rf_layout.addWidget(txt_box, 1)

                prio_badge = StatusBadge(
                    f"{iv['priority']}",
                    variant="danger" if iv["priority"] == "HIGH" else ("warning" if iv["priority"] == "MEDIUM" else "success"),
                    parent=row_frame
                )
                rf_layout.addWidget(prio_badge)

                ac_layout.addWidget(row_frame)
        else:
            ac_layout.addWidget(QLabel("No active intervention required.", action_card))

        self.content_layout.addWidget(action_card)

        # -------------------------------------------------------------------
        # 8. Unified Chronological Activity Timeline
        # -------------------------------------------------------------------
        timeline_card = AnimatedCard(self.content_widget)
        tc_layout = QVBoxLayout(timeline_card)
        tc_layout.setContentsMargins(20, 16, 20, 16)
        tc_layout.setSpacing(10)

        tc_header = SectionHeader("CHRONOLOGICAL LEARNING TIMELINE", subtitle=f"Showing latest {min(len(timeline), 20)} events", parent=timeline_card)
        tc_layout.addWidget(tc_header)

        if timeline:
            for ev in timeline[:20]:
                t_row = QWidget(timeline_card)
                t_row.setStyleSheet("background: transparent;")
                tr_layout = QHBoxLayout(t_row)
                tr_layout.setContentsMargins(0, 4, 0, 4)
                tr_layout.setSpacing(10)

                icon_lbl = QLabel(ev.get("icon", "•"), t_row)
                icon_lbl.setFont(QFont("Segoe UI Emoji", 13))
                tr_layout.addWidget(icon_lbl)

                date_lbl = QLabel(ev.get("date", ""), t_row)
                date_lbl.setFont(QFont("Outfit", 11, QFont.Bold))
                date_lbl.setStyleSheet("color: #7C5CFF;")
                date_lbl.setFixedWidth(85)
                tr_layout.addWidget(date_lbl)

                desc_lbl = QLabel(f"<b>{ev.get('title')}</b> — {ev.get('description')}", t_row)
                desc_lbl.setFont(QFont("Outfit", 11))
                desc_lbl.setStyleSheet("color: #F5F7FA;")
                desc_lbl.setWordWrap(True)
                tr_layout.addWidget(desc_lbl, 1)

                tc_layout.addWidget(t_row)
        else:
            tc_layout.addWidget(EmptyState(icon="🕒", title="Timeline Empty", description="No logged activities or milestones found for this student.", parent=timeline_card))

        self.content_layout.addWidget(timeline_card)
