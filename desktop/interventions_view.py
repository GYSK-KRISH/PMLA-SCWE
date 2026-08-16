"""PySide6 panel for Teacher Intervention Tracking & Outcome Intelligence.

Version 1.6 — Intervention Tracking & Outcome Intelligence
Features:
- Creation of structured pedagogical interventions with automatic baseline snapshot.
- Active case tracking and status transitions (PENDING, IN_PROGRESS, COMPLETED, ESCALATED).
- Outcome evaluation modal displaying Before vs. After Deltas and 0-100 Effectiveness Ratings.
- Classroom cohort resolution KPI metrics.
"""

from __future__ import annotations
import os
from datetime import datetime, date
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QGridLayout, QScrollArea, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QTextEdit, QDialog,
    QDialogButtonBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from core import intervention_service, intervention_analytics, student_profile_service
from core.database import get_db_status
from desktop.widgets.reusable_ui_components import (
    SectionHeader, StatusBadge, InfoRow
)


class OutcomeEvaluationDialog(QDialog):
    """Dialog for evaluating intervention outcomes and computing Before vs After Deltas."""

    def __init__(self, parent, intervention_data: dict):
        super().__init__(parent)
        self.setWindowTitle(f"Evaluate Outcome — Intervention #{intervention_data['intervention_id']}")
        self.setMinimumSize(560, 480)
        self.setStyleSheet("background-color: #10131D; color: #F5F7FA;")
        self.intervention = intervention_data

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        # Title
        hdr = SectionHeader(
            f"OUTCOME EVALUATION: {intervention_data['title']}",
            subtitle=f"Student: #{intervention_data['student_id']} {intervention_data.get('student_name', '')}",
            parent=self
        )
        layout.addWidget(hdr)

        # Baseline Snapshot Card
        pre_frame = QFrame(self)
        pre_frame.setObjectName("CardFrame")
        pre_layout = QVBoxLayout(pre_frame)
        pre_layout.setContentsMargins(14, 10, 14, 10)

        pre_title = QLabel("BASELINE METRIC SNAPSHOT (AT CREATION)", pre_frame)
        pre_title.setFont(QFont("Outfit", 10, QFont.Bold))
        pre_title.setStyleSheet("color: #8D96A8;")
        pre_layout.addWidget(pre_title)

        grid = QGridLayout()
        grid.addWidget(QLabel("Baseline Risk Score:"), 0, 0)
        grid.addWidget(QLabel(f"<b>{intervention_data.get('pre_risk_score') or 'N/A'}/100</b>"), 0, 1)

        grid.addWidget(QLabel("Baseline Academic Score:"), 0, 2)
        grid.addWidget(QLabel(f"<b>{intervention_data.get('pre_academic_score') or 'N/A'}%</b>"), 0, 3)

        grid.addWidget(QLabel("Baseline Attendance Rate:"), 1, 0)
        grid.addWidget(QLabel(f"<b>{intervention_data.get('pre_attendance_rate') or 'N/A'}%</b>"), 1, 1)

        grid.addWidget(QLabel("Baseline Learning Health:"), 1, 2)
        grid.addWidget(QLabel(f"<b>{intervention_data.get('pre_lhs_score') or 'N/A'}/100</b>"), 1, 3)
        pre_layout.addLayout(grid)
        layout.addWidget(pre_frame)

        # Post Metrics Form (Pre-populated with student's current live analytics)
        post_frame = QFrame(self)
        post_frame.setObjectName("CardFrame")
        pf_layout = QVBoxLayout(post_frame)
        pf_layout.setContentsMargins(14, 10, 14, 10)

        post_title = QLabel("OUTCOME METRICS (POST-INTERVENTION)", post_frame)
        post_title.setFont(QFont("Outfit", 10, QFont.Bold))
        post_title.setStyleSheet("color: #7C5CFF;")
        pf_layout.addWidget(post_title)

        profile = student_profile_service.get_student_360_profile(intervention_data["student_id"])
        current_risk = profile.get("risk_engine", {}).get("risk_score") if profile else None
        current_acad = profile["academic"].get("average_score") if profile else None
        current_att = profile["attendance"].get("percentage") if profile else None
        current_lhs = profile["learning_health"].get("score") if profile else None

        pf_grid = QGridLayout()
        pf_grid.addWidget(QLabel("Post Risk Score (0-100):"), 0, 0)
        self.entry_post_risk = QLineEdit(str(current_risk if current_risk is not None else 30))
        pf_grid.addWidget(self.entry_post_risk, 0, 1)

        pf_grid.addWidget(QLabel("Post Academic Score (%):"), 0, 2)
        self.entry_post_acad = QLineEdit(str(round(current_acad, 1) if current_acad is not None else 65.0))
        pf_grid.addWidget(self.entry_post_acad, 0, 3)

        pf_grid.addWidget(QLabel("Post Attendance (%):"), 1, 0)
        self.entry_post_att = QLineEdit(str(round(current_att, 1) if current_att is not None else 82.0))
        pf_grid.addWidget(self.entry_post_att, 1, 1)

        pf_grid.addWidget(QLabel("Post LHS (0-100):"), 1, 2)
        self.entry_post_lhs = QLineEdit(str(round(current_lhs, 1) if current_lhs is not None else 72.0))
        pf_grid.addWidget(self.entry_post_lhs, 1, 3)
        pf_layout.addLayout(pf_grid)
        layout.addWidget(post_frame)

        # Teacher Evaluation Notes
        layout.addWidget(QLabel("Teacher Evaluation Summary & Notes:", self))
        self.notes_text = QTextEdit(self)
        self.notes_text.setPlaceholderText("Enter observation notes and next pedagogical recommendations...")
        self.notes_text.setFixedHeight(70)
        layout.addWidget(self.notes_text)

        # Action Buttons
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        btn_box.button(QDialogButtonBox.Ok).setText("⚡ Calculate Effectiveness & Complete")
        btn_box.button(QDialogButtonBox.Ok).setObjectName("PrimaryButton")
        btn_box.accepted.connect(self.save_evaluation)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def save_evaluation(self):
        try:
            post_r = float(self.entry_post_risk.text())
            post_a = float(self.entry_post_acad.text())
            post_att = float(self.entry_post_att.text())
            post_lhs = float(self.entry_post_lhs.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Inputs", "Please enter valid numeric values for all outcome metrics.")
            return

        overrides = {
            "risk_score": post_r,
            "academic_score": post_a,
            "attendance_rate": post_att,
            "lhs_score": post_lhs
        }

        res = intervention_service.evaluate_intervention_outcome(
            intervention_id=self.intervention["intervention_id"],
            teacher_notes=self.notes_text.toPlainText(),
            post_metrics_override=overrides
        )

        if res.get("success"):
            deltas = res["deltas"]
            msg = (
                f"Intervention Successfully Evaluated!\n\n"
                f"• Outcome Rating: {res['effectiveness_tier']} ({res['effectiveness_score']}/100)\n"
                f"• Risk Mitigation: -{deltas['risk']} pts\n"
                f"• Academic Gain: +{deltas['academic']}%\n"
                f"• Attendance Gain: +{deltas['attendance']}%\n\n"
                f"{res['narrative']}"
            )
            QMessageBox.information(self, "Outcome Evaluation Complete", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Evaluation Error", "Could not complete evaluation.")


class InterventionsFrame(QWidget):
    """Main PySide6 view for Version 1.6 Intervention Tracking & Outcome Intelligence."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Main Layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(15, 12, 15, 12)
        root_layout.setSpacing(10)

        # 1. Header Section
        header_frame = QFrame(self)
        header_frame.setObjectName("CardFrame")
        header_frame.setFixedHeight(54)
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(16, 0, 16, 0)

        title = QLabel("INTERVENTION TRACKING & OUTCOME INTELLIGENCE", header_frame)
        title.setFont(QFont("Outfit", 17, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        h_layout.addWidget(title)

        subtitle = QLabel("Targeted Actions • Baseline Snapshots • Outcome Deltas", header_frame)
        subtitle.setFont(QFont("Outfit", 11))
        subtitle.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        h_layout.addWidget(subtitle)
        h_layout.addStretch(1)

        self.db_label = QLabel("", header_frame)
        self.db_label.setFont(QFont("Outfit", 11))
        self.db_label.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        h_layout.addWidget(self.db_label)
        root_layout.addWidget(header_frame)
        self.update_db_status()

        # 2. KPI Summary Cards Row
        kpi_row = QWidget(self)
        kpi_l = QHBoxLayout(kpi_row)
        kpi_l.setContentsMargins(0, 0, 0, 0)
        kpi_l.setSpacing(10)

        self.card_total = self._make_kpi_card(kpi_row, "TOTAL CASES", "0", "#7C5CFF")
        self.card_active = self._make_kpi_card(kpi_row, "ACTIVE IN PROGRESS", "0", "#FFB224")
        self.card_completed = self._make_kpi_card(kpi_row, "COMPLETED & EVALUATED", "0", "#30A46C")
        self.card_rate = self._make_kpi_card(kpi_row, "RESOLUTION RATE", "0.0%", "#00B4D8")

        kpi_l.addWidget(self.card_total)
        kpi_l.addWidget(self.card_active)
        kpi_l.addWidget(self.card_completed)
        kpi_l.addWidget(self.card_rate)
        root_layout.addWidget(kpi_row)

        # 3. Main Workspace Split: Form on Left vs Active Pipeline on Right
        split = QWidget(self)
        split_layout = QHBoxLayout(split)
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(12)

        # Left Column: Create Intervention Form
        form_panel = QFrame(split)
        form_panel.setObjectName("CardFrame")
        form_panel.setFixedWidth(340)
        fp_layout = QVBoxLayout(form_panel)
        fp_layout.setContentsMargins(14, 12, 14, 12)
        fp_layout.setSpacing(8)
        fp_layout.setAlignment(Qt.AlignTop)

        fp_hdr = SectionHeader("CREATE INTERVENTION", subtitle="Snapshot baseline metrics", parent=form_panel)
        fp_layout.addWidget(fp_hdr)

        fp_layout.addWidget(QLabel("Target Student ID:", form_panel))
        self.sid_entry = QLineEdit(form_panel)
        self.sid_entry.setPlaceholderText("e.g. 1")
        fp_layout.addWidget(self.sid_entry)

        fp_layout.addWidget(QLabel("Intervention Title:", form_panel))
        self.title_entry = QLineEdit(form_panel)
        self.title_entry.setPlaceholderText("e.g. 1-on-1 Algebra Revision")
        fp_layout.addWidget(self.title_entry)

        fp_layout.addWidget(QLabel("Primary Risk Factor:", form_panel))
        self.risk_factor_entry = QLineEdit(form_panel)
        self.risk_factor_entry.setPlaceholderText("e.g. Low Mathematics Diagnostic")
        fp_layout.addWidget(self.risk_factor_entry)

        fp_layout.addWidget(QLabel("Action Category:", form_panel))
        self.action_combo = QComboBox(form_panel)
        self.action_combo.addItems(intervention_service.ACTION_TYPES)
        fp_layout.addWidget(self.action_combo)

        fp_layout.addWidget(QLabel("Priority Level:", form_panel))
        self.priority_combo = QComboBox(form_panel)
        self.priority_combo.addItems(intervention_service.PRIORITY_LEVELS)
        fp_layout.addWidget(self.priority_combo)

        fp_layout.addWidget(QLabel("Target Review Date (YYYY-MM-DD):", form_panel))
        self.target_date_entry = QLineEdit(form_panel)
        self.target_date_entry.setText(date.today().isoformat())
        fp_layout.addWidget(self.target_date_entry)

        fp_layout.addWidget(QLabel("Initial Pedagogical Notes:", form_panel))
        self.init_notes = QTextEdit(form_panel)
        self.init_notes.setPlaceholderText("Describe planned remedial strategy...")
        self.init_notes.setFixedHeight(50)
        fp_layout.addWidget(self.init_notes)

        self.btn_create = QPushButton("➕ Create & Snapshot Baseline", form_panel)
        self.btn_create.setObjectName("PrimaryButton")
        self.btn_create.setFont(QFont("Outfit", 10, QFont.Bold))
        self.btn_create.clicked.connect(self.create_intervention_action)
        fp_layout.addWidget(self.btn_create)

        split_layout.addWidget(form_panel)

        # Right Column: Interventions Table & Action Controls
        table_panel = QFrame(split)
        table_panel.setObjectName("CardFrame")
        tp_layout = QVBoxLayout(table_panel)
        tp_layout.setContentsMargins(14, 12, 14, 12)
        tp_layout.setSpacing(8)

        tp_hdr = SectionHeader("ACTIVE INTERVENTIONS PIPELINE", subtitle="Monitor and evaluate pedagogical outcomes", parent=table_panel)
        tp_layout.addWidget(tp_hdr)

        # Filter Bar
        f_bar = QWidget(table_panel)
        fb_l = QHBoxLayout(f_bar)
        fb_l.setContentsMargins(0, 0, 0, 0)
        fb_l.addWidget(QLabel("Filter Status:"))
        self.filter_status = QComboBox(f_bar)
        self.filter_status.addItems(["All", "PENDING", "IN_PROGRESS", "COMPLETED", "ESCALATED"])
        self.filter_status.currentTextChanged.connect(self.load_interventions)
        fb_l.addWidget(self.filter_status)

        fb_l.addWidget(QLabel("Priority:"))
        self.filter_prio = QComboBox(f_bar)
        self.filter_prio.addItems(["All", "HIGH", "MEDIUM", "LOW"])
        self.filter_prio.currentTextChanged.connect(self.load_interventions)
        fb_l.addWidget(self.filter_prio)
        fb_l.addStretch(1)

        self.btn_refresh = QPushButton("🔄 Refresh", f_bar)
        self.btn_refresh.clicked.connect(self.load_interventions)
        fb_l.addWidget(self.btn_refresh)
        tp_layout.addWidget(f_bar)

        # Table
        self.table = QTableWidget(table_panel)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Student", "Title & Strategy", "Priority", "Status", "Outcome / Effectiveness", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        tp_layout.addWidget(self.table)

        split_layout.addWidget(table_panel, 1)
        root_layout.addWidget(split, 1)

        self.load_interventions()

    def _make_kpi_card(self, parent: QWidget, label: str, val: str, color_hex: str) -> QFrame:
        card = QFrame(parent)
        card.setObjectName("InnerCardFrame")
        card.setFixedHeight(58)
        l = QVBoxLayout(card)
        l.setContentsMargins(12, 6, 12, 6)
        l.setSpacing(1)

        lbl = QLabel(label, card)
        lbl.setFont(QFont("Outfit", 9, QFont.Bold))
        lbl.setStyleSheet("color: #8D96A8;")
        l.addWidget(lbl)

        val_lbl = QLabel(val, card)
        val_lbl.setObjectName("kpi_val")
        val_lbl.setFont(QFont("Outfit", 14, QFont.Bold))
        val_lbl.setStyleSheet(f"color: {color_hex};")
        l.addWidget(val_lbl)
        return card

    def update_db_status(self):
        st = get_db_status()
        t = st.get("type", "SQL")
        self.db_label.setText(f"Connected: {t}")

    def create_intervention_action(self):
        sid_raw = self.sid_entry.text().strip()
        title = self.title_entry.text().strip()
        risk_f = self.risk_factor_entry.text().strip()
        atype = self.action_combo.currentText()
        prio = self.priority_combo.currentText()
        t_date = self.target_date_entry.text().strip()
        notes = self.init_notes.toPlainText().strip()

        if not sid_raw.isdigit():
            QMessageBox.warning(self, "Invalid Student ID", "Please enter a valid numeric Student ID.")
            return
        if not title:
            QMessageBox.warning(self, "Missing Title", "Please provide a descriptive intervention title.")
            return

        try:
            res = intervention_service.create_intervention(
                student_id=int(sid_raw),
                title=title,
                risk_factor=risk_f or "General Academic & Wellbeing Review",
                action_type=atype,
                priority=prio,
                target_date=t_date,
                teacher_notes=notes
            )
            if res.get("success"):
                QMessageBox.information(
                    self, "Intervention Created",
                    f"Intervention #{res['intervention_id']} successfully registered with baseline snapshot captured!"
                )
                self.title_entry.clear()
                self.risk_factor_entry.clear()
                self.init_notes.clear()
                self.load_interventions()
        except Exception as exc:
            QMessageBox.critical(self, "Creation Error", str(exc))

    def load_interventions(self):
        st = self.filter_status.currentText()
        pr = self.filter_prio.currentText()
        items = intervention_service.get_all_interventions(status=st, priority=pr)

        # Update KPI Summary Cards
        all_items = intervention_service.get_all_interventions()
        agg = intervention_analytics.aggregate_cohort_intervention_metrics(all_items)

        self.card_total.findChild(QLabel, "kpi_val").setText(str(agg["total_interventions"]))
        self.card_active.findChild(QLabel, "kpi_val").setText(str(agg["active_count"]))
        self.card_completed.findChild(QLabel, "kpi_val").setText(str(agg["completed_count"]))
        self.card_rate.findChild(QLabel, "kpi_val").setText(f"{agg['resolution_rate']}%")

        self.table.setRowCount(len(items))
        for row, iv in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(f"#{iv['intervention_id']}"))
            self.table.setItem(row, 1, QTableWidgetItem(f"#{iv['student_id']} {iv.get('student_name', '')} ({iv.get('class_section', '')})"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{iv['title']}\n[{iv.get('action_type', '')}]"))
            self.table.setItem(row, 3, QTableWidgetItem(iv.get("priority", "MEDIUM")))
            self.table.setItem(row, 4, QTableWidgetItem(iv.get("status", "PENDING")))

            eff = iv.get("effectiveness_score")
            eff_tier = iv.get("effectiveness_tier") or "Pending Evaluation"
            eff_text = f"{eff_tier} ({eff:.1f}/100)" if eff is not None else eff_tier
            self.table.setItem(row, 5, QTableWidgetItem(eff_text))

            # Action Buttons cell widget
            action_cell = QWidget()
            ac_l = QHBoxLayout(action_cell)
            ac_l.setContentsMargins(4, 2, 4, 2)
            ac_l.setSpacing(4)

            if iv.get("status") == "PENDING":
                btn_start = QPushButton("▶️ Start")
                btn_start.setStyleSheet("background: #7C5CFF; color: #fff; padding: 3px 6px; font-size: 10px; border-radius: 4px;")
                btn_start.clicked.connect(lambda _, id=iv["intervention_id"]: self.change_status(id, "IN_PROGRESS"))
                ac_l.addWidget(btn_start)

            if iv.get("status") in ("PENDING", "IN_PROGRESS"):
                btn_eval = QPushButton("⚡ Evaluate")
                btn_eval.setStyleSheet("background: #30A46C; color: #fff; padding: 3px 6px; font-size: 10px; border-radius: 4px;")
                btn_eval.clicked.connect(lambda _, item=iv: self.open_evaluation_dialog(item))
                ac_l.addWidget(btn_eval)

                btn_esc = QPushButton("⚠️ Escalate")
                btn_esc.setStyleSheet("background: #E5484D; color: #fff; padding: 3px 6px; font-size: 10px; border-radius: 4px;")
                btn_esc.clicked.connect(lambda _, id=iv["intervention_id"]: self.change_status(id, "ESCALATED"))
                ac_l.addWidget(btn_esc)

            self.table.setCellWidget(row, 6, action_cell)

    def change_status(self, intervention_id: int, new_status: str):
        intervention_service.update_intervention_status(intervention_id, new_status)
        self.load_interventions()

    def open_evaluation_dialog(self, intervention_data: dict):
        dlg = OutcomeEvaluationDialog(self, intervention_data)
        if dlg.exec():
            self.load_interventions()
