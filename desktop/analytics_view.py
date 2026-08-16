"""PySide6 panel for Explainable Predictive Analytics & Learning Risk Engine.

Version 1.3 — Explainable Predictive Analytics
Features:
- Class-wide risk overview cards (High, Medium, Low, Insufficient) & primary risk factor.
- Class, section, and risk tier filters.
- Student risk score (0-100) and transparent multi-factor contribution breakdown.
- Evidence-based explainability ('Why does this student need attention?').
- Deduplicated early warning indicators.
- Deterministic teacher intervention checklist.
- Transparent linear regression trajectory forecast.
"""

from __future__ import annotations
import os
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QGridLayout, QScrollArea, QCheckBox, QComboBox, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from core import student_service, analytics, recommendation, risk_engine, explainability, constants
from .student_profile_dialog import StudentProfileDialog
from .widgets.animated_card import AnimatedCard
from .widgets.reusable_ui_components import (
    SectionHeader, StatusBadge, AnimatedProgressBar, InfoRow, EmptyState
)


class AnalyticsViewFrame(QWidget):
    """Upgraded PySide6 frame for Version 1.3 Explainable Learning Risk Engine."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.active_student_id = None
        self.student_summary = None
        self.student_risk_profile = None

        # Main Layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(15, 12, 15, 12)
        root_layout.setSpacing(12)

        # -------------------------------------------------------------------
        # 1. Header Section
        # -------------------------------------------------------------------
        header_frame = QFrame(self)
        header_frame.setObjectName("CardFrame")
        header_frame.setFixedHeight(54)
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(16, 0, 16, 0)

        title = QLabel("EXPLAINABLE LEARNING RISK ENGINE", header_frame)
        title.setFont(QFont("Outfit", 17, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        h_layout.addWidget(title)

        subtitle = QLabel("Transparent • Evidence-Based • Educational Decision Support", header_frame)
        subtitle.setFont(QFont("Outfit", 11))
        subtitle.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        h_layout.addWidget(subtitle)
        h_layout.addStretch(1)

        root_layout.addWidget(header_frame)

        # -------------------------------------------------------------------
        # 2. Class Risk Overview KPI Bar
        # -------------------------------------------------------------------
        self.overview_frame = QFrame(self)
        self.overview_frame.setObjectName("CardFrame")
        ov_layout = QHBoxLayout(self.overview_frame)
        ov_layout.setContentsMargins(12, 10, 12, 10)
        ov_layout.setSpacing(12)

        # High Risk Card
        self.high_card = self._create_kpi_mini_card("HIGH RISK", "0", "danger", "🔴")
        ov_layout.addWidget(self.high_card)

        # Medium Risk Card
        self.med_card = self._create_kpi_mini_card("MEDIUM RISK", "0", "warning", "🟡")
        ov_layout.addWidget(self.med_card)

        # Low Risk Card
        self.low_card = self._create_kpi_mini_card("LOW RISK", "0", "success", "🟢")
        ov_layout.addWidget(self.low_card)

        # Insufficient Data Card
        self.insuf_card = self._create_kpi_mini_card("INSUFFICIENT", "0", "muted", "⚪")
        ov_layout.addWidget(self.insuf_card)

        # Most Common Concern Pill
        self.common_concern_box = QFrame(self.overview_frame)
        self.common_concern_box.setObjectName("InnerCardFrame")
        cc_layout = QVBoxLayout(self.common_concern_box)
        cc_layout.setContentsMargins(12, 6, 12, 6)
        cc_layout.setSpacing(2)

        cc_title = QLabel("PRIMARY COHORT CONCERN", self.common_concern_box)
        cc_title.setFont(QFont("Outfit", 9, QFont.Bold))
        cc_title.setStyleSheet("color: #8D96A8; letter-spacing: 0.5px;")
        cc_layout.addWidget(cc_title)

        self.common_concern_lbl = QLabel("Loading...", self.common_concern_box)
        self.common_concern_lbl.setFont(QFont("Outfit", 11, QFont.Bold))
        self.common_concern_lbl.setStyleSheet("color: #7C5CFF;")
        cc_layout.addWidget(self.common_concern_lbl)

        ov_layout.addWidget(self.common_concern_box, 1)
        root_layout.addWidget(self.overview_frame)

        # -------------------------------------------------------------------
        # 3. Filter & Selection Control Panel
        # -------------------------------------------------------------------
        lookup_frame = QFrame(self)
        lookup_frame.setObjectName("CardFrame")
        lf_layout = QHBoxLayout(lookup_frame)
        lf_layout.setContentsMargins(16, 8, 16, 8)
        lf_layout.setSpacing(10)

        # Class Filter
        lf_layout.addWidget(QLabel("Class:", lookup_frame))
        self.class_filter = QComboBox(lookup_frame)
        self.class_filter.addItems(["All", "XII", "XI", "X"])
        self.class_filter.currentTextChanged.connect(self.on_filter_changed)
        lf_layout.addWidget(self.class_filter)

        # Section Filter
        lf_layout.addWidget(QLabel("Section:", lookup_frame))
        self.sec_filter = QComboBox(lookup_frame)
        self.sec_filter.addItems(["All", "A", "B", "C"])
        self.sec_filter.currentTextChanged.connect(self.on_filter_changed)
        lf_layout.addWidget(self.sec_filter)

        # Risk Filter
        lf_layout.addWidget(QLabel("Risk Tier:", lookup_frame))
        self.risk_filter = QComboBox(lookup_frame)
        self.risk_filter.addItems(["All", "HIGH", "MEDIUM", "LOW", "INSUFFICIENT DATA"])
        self.risk_filter.currentTextChanged.connect(self.on_filter_changed)
        lf_layout.addWidget(self.risk_filter)

        lf_layout.addSpacing(10)
        lf_layout.addWidget(QLabel("Student ID:", lookup_frame))

        self.sid_entry = QLineEdit(lookup_frame)
        self.sid_entry.setPlaceholderText("e.g. 1")
        self.sid_entry.setFixedWidth(80)
        self.sid_entry.returnPressed.connect(self.load_student_analytics)
        lf_layout.addWidget(self.sid_entry)

        search_btn = QPushButton("Analyze", lookup_frame)
        search_btn.setFont(QFont("Outfit", 11, QFont.Bold))
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.clicked.connect(self.load_student_analytics)
        lf_layout.addWidget(search_btn)

        self.profile_btn = QPushButton("✦ Open 360° Profile", lookup_frame)
        self.profile_btn.setFont(QFont("Outfit", 11, QFont.Bold))
        self.profile_btn.setStyleSheet(
            "QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7C5CFF, stop:1 #4D8DFF);"
            " color: #FFFFFF; border-radius: 6px; padding: 5px 12px; font-weight: bold; }"
            "QPushButton:hover { opacity: 0.9; }"
        )
        self.profile_btn.setCursor(Qt.PointingHandCursor)
        self.profile_btn.clicked.connect(self.open_360_profile_dialog)
        self.profile_btn.setEnabled(False)
        lf_layout.addWidget(self.profile_btn)

        self.student_info_lbl = QLabel("No student selected.", lookup_frame)
        self.student_info_lbl.setFont(QFont("Outfit", 12, QFont.Bold))
        self.student_info_lbl.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        lf_layout.addWidget(self.student_info_lbl)

        lf_layout.addStretch(1)
        root_layout.addWidget(lookup_frame)

        # -------------------------------------------------------------------
        # 4. Split Layout for Student Explainability Details
        # -------------------------------------------------------------------
        split_widget = QWidget(self)
        split_layout = QHBoxLayout(split_widget)
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(12)

        # Left Column: Risk Score, Contributing Factors, Predictive Trajectory
        self.left_scroll = QScrollArea(split_widget)
        self.left_scroll.setObjectName("CardFrame")
        self.left_scroll.setWidgetResizable(True)
        self.left_content = QWidget()
        self.left_layout = QVBoxLayout(self.left_content)
        self.left_layout.setContentsMargins(12, 12, 12, 12)
        self.left_layout.setSpacing(12)
        self.left_layout.setAlignment(Qt.AlignTop)
        self.left_scroll.setWidget(self.left_content)
        split_layout.addWidget(self.left_scroll, 3)

        # Right Column: "Why?" Narrative, Early Warnings, Recommended Actions
        self.right_scroll = QScrollArea(split_widget)
        self.right_scroll.setObjectName("CardFrame")
        self.right_scroll.setWidgetResizable(True)
        self.right_content = QWidget()
        self.right_layout = QVBoxLayout(self.right_content)
        self.right_layout.setContentsMargins(12, 12, 12, 12)
        self.right_layout.setSpacing(12)
        self.right_layout.setAlignment(Qt.AlignTop)
        self.right_scroll.setWidget(self.right_content)
        split_layout.addWidget(self.right_scroll, 3)

        root_layout.addWidget(split_widget, 1)

        # Initialize Data & Draw Placeholders
        self.refresh_class_overview()
        self.draw_instruction_placeholders()

    def _create_kpi_mini_card(self, title: str, count: str, variant: str, icon: str) -> QFrame:
        card = QFrame(self.overview_frame)
        card.setObjectName("InnerCardFrame")
        card.setFixedWidth(130)
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(10, 6, 10, 6)
        c_layout.setSpacing(2)

        t_lbl = QLabel(f"{icon} {title}", card)
        t_lbl.setFont(QFont("Outfit", 9, QFont.Bold))
        t_lbl.setStyleSheet("color: #8D96A8;")
        c_layout.addWidget(t_lbl)

        val_lbl = QLabel(count, card)
        val_lbl.setObjectName(f"val_{title.replace(' ', '_')}")
        val_lbl.setFont(QFont("Outfit", 16, QFont.Bold))
        color = "#E5484D" if variant == "danger" else ("#FFB224" if variant == "warning" else ("#30A46C" if variant == "success" else "#8D96A8"))
        val_lbl.setStyleSheet(f"color: {color};")
        c_layout.addWidget(val_lbl)

        return card

    def refresh_class_overview(self):
        """Loads aggregate class-wide risk distribution metrics."""
        c_filter = self.class_filter.currentText()
        s_filter = self.sec_filter.currentText()
        r_filter = self.risk_filter.currentText()

        overview = risk_engine.get_class_risk_overview(c_filter, s_filter, r_filter)
        
        # Update counts
        for card, val in [
            (self.high_card, overview["total_high"]),
            (self.med_card, overview["total_medium"]),
            (self.low_card, overview["total_low"]),
            (self.insuf_card, overview["total_insufficient"])
        ]:
            val_lbl = card.findChild(QLabel, f"val_{card.findChildren(QLabel)[0].text().split(' ')[1]}")
            if val_lbl:
                val_lbl.setText(str(val))

        self.common_concern_lbl.setText(overview["most_common_risk_factor"])

    def on_filter_changed(self):
        self.refresh_class_overview()

    def draw_instruction_placeholders(self):
        while self.left_layout.count() > 0:
            item = self.left_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        while self.right_layout.count() > 0:
            item = self.right_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        empty_left = EmptyState(
            icon="🧠",
            title="Explainable Learning Risk Engine",
            description="Enter a Student ID above and click 'Analyze' to compute transparent multi-factor risk scores, contributing factor evidence, and trajectory forecasts.",
            parent=self.left_content
        )
        self.left_layout.addWidget(empty_left)

        empty_right = EmptyState(
            icon="💡",
            title="Evidence & Intervention Plan",
            description="Clear 'Why?' narratives and deterministic teacher action checksheets will populate here.",
            parent=self.right_content
        )
        self.right_layout.addWidget(empty_right)

    def load_student_analytics(self):
        sid_raw = self.sid_entry.text().strip()
        if not sid_raw:
            self.draw_instruction_placeholders()
            return

        try:
            sid = int(sid_raw)
        except ValueError:
            self.draw_instruction_placeholders()
            return

        # Fetch complete explainable risk profile
        profile = risk_engine.compute_student_risk_profile(sid)
        if not profile:
            self.student_info_lbl.setText(f"Student ID #{sid} not found in database.")
            self.student_info_lbl.setStyleSheet("color: #E5484D; background: transparent; border: none;")
            self.profile_btn.setEnabled(False)
            self.draw_instruction_placeholders()
            return

        self.active_student_id = sid
        self.student_risk_profile = profile
        self.profile_btn.setEnabled(True)

        s = profile["student"]
        self.student_info_lbl.setText(f"Active: {s['name']} ({s['class_section']})")
        self.student_info_lbl.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")

        # Clear containers
        while self.left_layout.count() > 0:
            item = self.left_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        while self.right_layout.count() > 0:
            item = self.right_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # ===================================================================
        # LEFT PANEL: RISK SCORE + CONTRIBUTING FACTORS + PREDICTION
        # ===================================================================

        # 1. Composite Risk Score Card
        risk_score = profile["risk_score"]
        risk_level = profile["risk_level"]
        r_card = AnimatedCard(self.left_content)
        rc_layout = QVBoxLayout(r_card)
        rc_layout.setContentsMargins(16, 14, 16, 14)
        rc_layout.setSpacing(10)

        badge_variant = "danger" if risk_level == "HIGH" else ("warning" if risk_level == "MEDIUM" else ("success" if risk_level == "LOW" else "muted"))
        rc_header = SectionHeader("TRANSPARENT RISK SCORE", subtitle="0 = Minimal Risk, 100 = Critical Multi-Factor Deficit", badge_text=f"{risk_level} RISK", badge_variant=badge_variant, parent=r_card)
        rc_layout.addWidget(rc_header)

        score_row = QWidget(r_card)
        score_row.setStyleSheet("background: transparent;")
        sr_layout = QHBoxLayout(score_row)
        sr_layout.setContentsMargins(0, 0, 0, 0)
        
        score_val_str = f"{risk_score}/100" if risk_score is not None else "N/A"
        score_lbl = QLabel(score_val_str, score_row)
        score_lbl.setFont(QFont("Outfit", 26, QFont.Bold))
        score_lbl.setStyleSheet("color: #FFFFFF;")
        sr_layout.addWidget(score_lbl)
        sr_layout.addStretch(1)

        level_pill = StatusBadge(f"Tier: {risk_level}", variant=badge_variant, parent=score_row)
        sr_layout.addWidget(level_pill)
        rc_layout.addWidget(score_row)

        score_bar = AnimatedProgressBar(
            value=float(risk_score) if risk_score is not None else 0.0,
            variant="danger" if risk_level == "HIGH" else ("warning" if risk_level == "MEDIUM" else "success"),
            bar_height=8,
            animate=True,
            parent=r_card
        )
        rc_layout.addWidget(score_bar)
        self.left_layout.addWidget(r_card)

        # 2. Contributing Risk Factors Table / Breakdown Card
        factors_card = AnimatedCard(self.left_content)
        fc_layout = QVBoxLayout(factors_card)
        fc_layout.setContentsMargins(16, 14, 16, 14)
        fc_layout.setSpacing(10)

        fc_header = SectionHeader("CONTRIBUTING RISK FACTORS", subtitle="Evidence-based points contribution breakdown", parent=factors_card)
        fc_layout.addWidget(fc_header)

        factors = profile.get("factors", [])
        if factors:
            for f in factors:
                f_frame = QFrame(factors_card)
                f_frame.setObjectName("InnerCardFrame")
                f_frame.setStyleSheet("background-color: #10131D; border-radius: 8px; padding: 6px;")
                ff_layout = QHBoxLayout(f_frame)
                ff_layout.setContentsMargins(10, 8, 10, 8)
                ff_layout.setSpacing(10)

                pts_str = f"+{f['points_contributed']:.0f} pts"
                pts_badge = StatusBadge(pts_str, variant="danger" if f["impact"] == "high" else ("warning" if f["impact"] == "medium" else "blue"), parent=f_frame)
                ff_layout.addWidget(pts_badge)

                f_info = QWidget(f_frame)
                f_info.setStyleSheet("background: transparent;")
                fi_l = QVBoxLayout(f_info)
                fi_l.setContentsMargins(0, 0, 0, 0)
                fi_l.setSpacing(2)

                fname_lbl = QLabel(f["name"], f_info)
                fname_lbl.setFont(QFont("Outfit", 11, QFont.Bold))
                fname_lbl.setStyleSheet("color: #F5F7FA;")
                fi_l.addWidget(fname_lbl)

                fev_lbl = QLabel(f["evidence"], f_info)
                fev_lbl.setFont(QFont("Outfit", 10))
                fev_lbl.setStyleSheet("color: #8D96A8;")
                fev_lbl.setWordWrap(True)
                fi_l.addWidget(fev_lbl)

                ff_layout.addWidget(f_info, 1)
                fc_layout.addWidget(f_frame)
        else:
            fc_layout.addWidget(QLabel("No active negative risk factors detected.", factors_card))

        self.left_layout.addWidget(factors_card)

        # 3. Data-Driven Trajectory & Prediction Card
        pred_card = AnimatedCard(self.left_content)
        pc_layout = QVBoxLayout(pred_card)
        pc_layout.setContentsMargins(16, 14, 16, 14)
        pc_layout.setSpacing(10)

        pred_header = SectionHeader("PREDICTIVE TRAJECTORY INDICATOR", subtitle="Data-driven linear regression analysis", parent=pred_card)
        pc_layout.addWidget(pred_header)

        pred_info = profile.get("prediction", {})
        if pred_info.get("status") == "VALID":
            curr_s = pred_info.get("current_score")
            pred_s = pred_info.get("predicted_score")
            slope = profile.get("slope", 0.0)
            trend = profile.get("trend", "Stable")

            pc_layout.addWidget(InfoRow("Recent Progress Score:", f"{curr_s:.1f}%" if curr_s is not None else "N/A", parent=pred_card))
            pc_layout.addWidget(InfoRow("Forecasted Next Score:", f"{pred_s:.1f}%" if pred_s is not None else "N/A", parent=pred_card))
            pc_layout.addWidget(InfoRow("Performance Trajectory:", trend, parent=pred_card))
            pc_layout.addWidget(InfoRow("Regression Slope:", f"{slope:.3f} pts/week", parent=pred_card))

            disclaimer = QLabel("Notice: Statistical predictive indicator derived from historical scores. Not a guaranteed forecast.", pred_card)
            disclaimer.setFont(QFont("Outfit", 9))
            disclaimer.setStyleSheet("color: #8D96A8; font-style: italic; margin-top: 4px;")
            disclaimer.setWordWrap(True)
            pc_layout.addWidget(disclaimer)
        else:
            pc_layout.addWidget(EmptyState(icon="📈", title="Insufficient Progression Data", description="Requires at least 2 weekly progress observations to model trajectory.", parent=pred_card))

        self.left_layout.addWidget(pred_card)

        # ===================================================================
        # RIGHT PANEL: "WHY?" NARRATIVE + ALERTS + ACTIONS
        # ===================================================================

        # 1. "Why Does This Student Require Attention?" Card
        why_card = AnimatedCard(self.right_content)
        wc_layout = QVBoxLayout(why_card)
        wc_layout.setContentsMargins(16, 14, 16, 14)
        wc_layout.setSpacing(10)

        wc_header = SectionHeader("EXPLAINABLE INTELLIGENCE", subtitle="Why does this student require attention?", parent=why_card)
        wc_layout.addWidget(wc_header)

        why_bullets = profile.get("why_explanation", [])
        if why_bullets:
            for b_text in why_bullets:
                row = QWidget(why_card)
                row.setStyleSheet("background: transparent;")
                rl = QHBoxLayout(row)
                rl.setContentsMargins(0, 2, 0, 2)
                rl.setSpacing(8)

                bullet = QLabel("•", row)
                bullet.setFont(QFont("Outfit", 13, QFont.Bold))
                bullet.setStyleSheet("color: #7C5CFF;")
                rl.addWidget(bullet)

                txt = QLabel(b_text, row)
                txt.setFont(QFont("Outfit", 11))
                txt.setStyleSheet("color: #F5F7FA; line-height: 1.4;")
                txt.setWordWrap(True)
                rl.addWidget(txt, 1)

                wc_layout.addWidget(row)
        else:
            wc_layout.addWidget(QLabel("No critical concerns flagged for this profile.", why_card))

        self.right_layout.addWidget(why_card)

        # 2. Early Warnings Card
        warnings = profile.get("early_warnings", [])
        if warnings:
            warn_card = AnimatedCard(self.right_content)
            wrc_layout = QVBoxLayout(warn_card)
            wrc_layout.setContentsMargins(16, 14, 16, 14)
            wrc_layout.setSpacing(10)

            wrc_header = SectionHeader("EARLY WARNING SYSTEM", subtitle="Proactive threshold violation alerts", parent=warn_card)
            wrc_layout.addWidget(wrc_header)

            for w in warnings:
                w_frame = QFrame(warn_card)
                w_frame.setObjectName("InnerCardFrame")
                w_frame.setStyleSheet("background-color: rgba(229, 72, 77, 0.08); border: 1px solid rgba(229, 72, 77, 0.3); border-radius: 8px; padding: 6px;")
                wf_layout = QHBoxLayout(w_frame)
                wf_layout.setContentsMargins(10, 6, 10, 6)
                wf_layout.setSpacing(8)

                icon_lbl = QLabel("⚠️" if w["severity"] == "CRITICAL" else "🔔", w_frame)
                icon_lbl.setFont(QFont("Segoe UI Emoji", 12))
                wf_layout.addWidget(icon_lbl)

                w_text_box = QWidget(w_frame)
                w_text_box.setStyleSheet("background: transparent;")
                wt_l = QVBoxLayout(w_text_box)
                wt_l.setContentsMargins(0, 0, 0, 0)
                wt_l.setSpacing(2)

                wt_lbl = QLabel(w["title"], w_text_box)
                wt_lbl.setFont(QFont("Outfit", 11, QFont.Bold))
                wt_lbl.setStyleSheet("color: #FF7B7B;")
                wt_l.addWidget(wt_lbl)

                wm_lbl = QLabel(w["message"], w_text_box)
                wm_lbl.setFont(QFont("Outfit", 10))
                wm_lbl.setStyleSheet("color: #8D96A8;")
                wm_lbl.setWordWrap(True)
                wt_l.addWidget(wm_lbl)

                wf_layout.addWidget(w_text_box, 1)
                wrc_layout.addWidget(w_frame)

            self.right_layout.addWidget(warn_card)

        # 3. Deterministic Intervention Action Plan
        act_card = AnimatedCard(self.right_content)
        ac_layout = QVBoxLayout(act_card)
        ac_layout.setContentsMargins(16, 14, 16, 14)
        ac_layout.setSpacing(10)

        ac_header = SectionHeader("RECOMMENDED INTERVENTION ACTION PLAN", subtitle="Targeted pedagogical checklist", parent=act_card)
        ac_layout.addWidget(ac_header)

        actions = profile.get("recommended_actions", [])
        if actions:
            for act in actions:
                a_frame = QFrame(act_card)
                a_frame.setObjectName("InnerCardFrame")
                a_frame.setStyleSheet("background-color: #10131D; border-radius: 8px; padding: 6px;")
                af_layout = QHBoxLayout(a_frame)
                af_layout.setContentsMargins(10, 8, 10, 8)
                af_layout.setSpacing(10)

                cb = QCheckBox(a_frame)
                cb.setCursor(Qt.PointingHandCursor)
                af_layout.addWidget(cb)

                a_box = QWidget(a_frame)
                a_box.setStyleSheet("background: transparent;")
                ab_l = QVBoxLayout(a_box)
                ab_l.setContentsMargins(0, 0, 0, 0)
                ab_l.setSpacing(2)

                at_lbl = QLabel(act["title"], a_box)
                at_lbl.setFont(QFont("Outfit", 11, QFont.Bold))
                at_lbl.setStyleSheet("color: #F5F7FA;")
                ab_l.addWidget(at_lbl)

                ad_lbl = QLabel(act["description"], a_box)
                ad_lbl.setFont(QFont("Outfit", 10))
                ad_lbl.setStyleSheet("color: #8D96A8;")
                ad_lbl.setWordWrap(True)
                ab_l.addWidget(ad_lbl)

                af_layout.addWidget(a_box, 1)

                prio_badge = StatusBadge(
                    f"{act['priority']}",
                    variant="danger" if act["priority"] == "HIGH" else ("warning" if act["priority"] == "MEDIUM" else "success"),
                    parent=a_frame
                )
                af_layout.addWidget(prio_badge)
                ac_layout.addWidget(a_frame)
        else:
            ac_layout.addWidget(QLabel("No immediate teacher interventions required.", act_card))

        self.right_layout.addWidget(act_card)

    def open_360_profile_dialog(self):
        """Opens the complete Student 360° Profile dialog for the active student."""
        if not self.active_student_id:
            return
        dialog = StudentProfileDialog(self, self.active_student_id)
        dialog.exec()
