"""PySide6 panel for Professional Report Generation Engine.

Version 1.5 — Professional Report Generation Engine
Features:
- 6 Report Types (Individual Student, Class Performance, At-Risk, Attendance, Progress, Interventions).
- Background worker QThread for non-blocking PDF/CSV generation.
- Section customization toggles.
- Live report preview panel.
- File save location selection via QFileDialog.
- Success notifications and direct file opening support.
"""

from __future__ import annotations
import os
import subprocess
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QGridLayout, QScrollArea, QCheckBox, QComboBox,
    QFileDialog, QMessageBox, QTextEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont

from core import report_service, student_service
from core.database import get_db_status
from desktop.widgets.reusable_ui_components import (
    SectionHeader, StatusBadge, InfoRow
)
from desktop.widgets.loading_indicator import LoadingIndicator


class ReportWorker(QThread):
    finished = Signal(dict)

    def __init__(self, mode: str, params: dict):
        super().__init__()
        self.mode = mode  # 'pdf', 'csv', 'preview'
        self.params = params

    def run(self):
        try:
            rtype = self.params.get("report_type", report_service.REPORT_TYPE_STUDENT_INTELLIGENCE)
            sid = self.params.get("student_id")
            c_name = self.params.get("class_name", "All")
            sec = self.params.get("section", "All")
            out_path = self.params.get("output_path")
            opts = self.params.get("options", {})

            if self.mode == "preview":
                text = report_service.generate_report_preview_text(
                    report_type=rtype,
                    student_id=sid,
                    class_name=c_name,
                    section=sec,
                    options=opts
                )
                self.finished.emit({"success": True, "mode": "preview", "text": text})

            elif self.mode == "pdf":
                if rtype == report_service.REPORT_TYPE_STUDENT_INTELLIGENCE and sid:
                    path = report_service.generate_student_pdf_report(
                        student_id=sid,
                        output_path=out_path,
                        options=opts
                    )
                else:
                    path = report_service.generate_class_pdf_report(
                        class_name=c_name,
                        section=sec,
                        output_path=out_path,
                        options=opts
                    )
                self.finished.emit({"success": True, "mode": "pdf", "path": path})

            elif self.mode == "csv":
                path = report_service.export_report_csv(
                    report_type=rtype,
                    class_name=c_name,
                    section=sec,
                    student_id=sid,
                    output_path=out_path
                )
                self.finished.emit({"success": True, "mode": "csv", "path": path})

        except Exception as exc:
            self.finished.emit({"success": False, "mode": self.mode, "error": str(exc)})


class ReportsFrame(QWidget):
    """PySide6 frame for Version 1.5 Professional Report Generation Engine."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.active_workers = []
        self.latest_generated_path = None

        # Main Layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(15, 12, 15, 12)
        root_layout.setSpacing(10)

        # -------------------------------------------------------------------
        # 1. Header Section
        # -------------------------------------------------------------------
        header_frame = QFrame(self)
        header_frame.setObjectName("CardFrame")
        header_frame.setFixedHeight(54)
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(16, 0, 16, 0)

        title = QLabel("PROFESSIONAL REPORT GENERATION ENGINE", header_frame)
        title.setFont(QFont("Outfit", 17, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        h_layout.addWidget(title)

        subtitle = QLabel("Student Intelligence • Class Performance • PDF & CSV Export", header_frame)
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

        # -------------------------------------------------------------------
        # 2. Split Layout: Left Form Config vs. Right Live Preview
        # -------------------------------------------------------------------
        split_widget = QWidget(self)
        split_layout = QHBoxLayout(split_widget)
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(12)

        # Left Column: Configuration & Options
        self.config_panel = QFrame(split_widget)
        self.config_panel.setObjectName("CardFrame")
        self.config_panel.setFixedWidth(380)
        cp_layout = QVBoxLayout(self.config_panel)
        cp_layout.setContentsMargins(16, 14, 16, 14)
        cp_layout.setSpacing(12)
        cp_layout.setAlignment(Qt.AlignTop)

        cp_hdr = SectionHeader("REPORT CONFIGURATION", subtitle="Select report type and scope", parent=self.config_panel)
        cp_layout.addWidget(cp_hdr)

        # Report Type Selector
        cp_layout.addWidget(QLabel("Select Report Type:", self.config_panel))
        self.type_combo = QComboBox(self.config_panel)
        for r_code, r_name in report_service.REPORT_TYPES:
            self.type_combo.addItem(r_name, r_code)
        self.type_combo.currentIndexChanged.connect(self.on_report_type_changed)
        cp_layout.addWidget(self.type_combo)

        # Target Student Selector
        self.student_box = QWidget(self.config_panel)
        sb_layout = QHBoxLayout(self.student_box)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.addWidget(QLabel("Target Student ID:", self.student_box))
        self.sid_entry = QLineEdit(self.student_box)
        self.sid_entry.setPlaceholderText("e.g. 1")
        self.sid_entry.setFixedWidth(80)
        self.sid_entry.textChanged.connect(self.trigger_live_preview)
        sb_layout.addWidget(self.sid_entry)
        sb_layout.addStretch(1)
        cp_layout.addWidget(self.student_box)

        # Class & Section Filters
        self.class_box = QWidget(self.config_panel)
        cb_layout = QHBoxLayout(self.class_box)
        cb_layout.setContentsMargins(0, 0, 0, 0)
        cb_layout.addWidget(QLabel("Class:", self.class_box))
        self.class_combo = QComboBox(self.class_box)
        self.class_combo.addItems(["All", "XII", "XI", "X"])
        self.class_combo.currentTextChanged.connect(self.trigger_live_preview)
        cb_layout.addWidget(self.class_combo)

        cb_layout.addWidget(QLabel("Section:", self.class_box))
        self.sec_combo = QComboBox(self.class_box)
        self.sec_combo.addItems(["All", "A", "B", "C"])
        self.sec_combo.currentTextChanged.connect(self.trigger_live_preview)
        cb_layout.addWidget(self.sec_combo)
        cp_layout.addWidget(self.class_box)

        # Section Customization Toggles
        cp_layout.addSpacing(4)
        sec_hdr = SectionHeader("INCLUDE SECTIONS", subtitle="Customize document structure", parent=self.config_panel)
        cp_layout.addWidget(sec_hdr)

        self.cb_metrics = QCheckBox("Academic & Attendance Performance", self.config_panel)
        self.cb_metrics.setChecked(True)
        cp_layout.addWidget(self.cb_metrics)

        self.cb_charts = QCheckBox("Visual Charts & Graphical Breakdown", self.config_panel)
        self.cb_charts.setChecked(True)
        cp_layout.addWidget(self.cb_charts)

        self.cb_risk = QCheckBox("Explainable Risk Factors & Evidence", self.config_panel)
        self.cb_risk.setChecked(True)
        cp_layout.addWidget(self.cb_risk)

        self.cb_interventions = QCheckBox("Recommended Teacher Actions", self.config_panel)
        self.cb_interventions.setChecked(True)
        cp_layout.addWidget(self.cb_interventions)

        self.cb_ai_summary = QCheckBox("AI-Grounded Executive Briefing", self.config_panel)
        self.cb_ai_summary.setChecked(True)
        cp_layout.addWidget(self.cb_ai_summary)

        cp_layout.addSpacing(10)

        # Action Buttons
        btn_box = QWidget(self.config_panel)
        bb_layout = QVBoxLayout(btn_box)
        bb_layout.setContentsMargins(0, 0, 0, 0)
        bb_layout.setSpacing(8)

        self.btn_gen_pdf = QPushButton("📄 Generate PDF Document", btn_box)
        self.btn_gen_pdf.setObjectName("PrimaryButton")
        self.btn_gen_pdf.setFont(QFont("Outfit", 11, QFont.Bold))
        self.btn_gen_pdf.setCursor(Qt.PointingHandCursor)
        self.btn_gen_pdf.clicked.connect(self.generate_pdf_report)
        bb_layout.addWidget(self.btn_gen_pdf)

        self.btn_export_csv = QPushButton("📊 Export Spreadsheet (CSV)", btn_box)
        self.btn_export_csv.setFont(QFont("Outfit", 10, QFont.Bold))
        self.btn_export_csv.setStyleSheet("background: #151925; color: #F5F7FA; border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 7px;")
        self.btn_export_csv.setCursor(Qt.PointingHandCursor)
        self.btn_export_csv.clicked.connect(self.export_csv_report)
        bb_layout.addWidget(self.btn_export_csv)

        self.btn_open_file = QPushButton("📂 Open Generated File", btn_box)
        self.btn_open_file.setFont(QFont("Outfit", 10, QFont.Bold))
        self.btn_open_file.setStyleSheet("background: #30A46C; color: #FFFFFF; border-radius: 6px; padding: 7px;")
        self.btn_open_file.setCursor(Qt.PointingHandCursor)
        self.btn_open_file.clicked.connect(self.open_generated_file)
        self.btn_open_file.setVisible(False)
        bb_layout.addWidget(self.btn_open_file)

        cp_layout.addWidget(btn_box)
        cp_layout.addStretch(1)
        split_layout.addWidget(self.config_panel)

        # Right Column: Live Report Preview & Generation Feedback
        self.preview_panel = QFrame(split_widget)
        self.preview_panel.setObjectName("CardFrame")
        pp_layout = QVBoxLayout(self.preview_panel)
        pp_layout.setContentsMargins(16, 14, 16, 14)
        pp_layout.setSpacing(10)

        pp_hdr = SectionHeader("DOCUMENT PREVIEW & VALIDATION", subtitle="Structured preview of generated content", parent=self.preview_panel)
        pp_layout.addWidget(pp_hdr)

        self.preview_text = QTextEdit(self.preview_panel)
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Consolas", 10))
        self.preview_text.setStyleSheet(
            "QTextEdit { background-color: #10131D; color: #F5F7FA; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 10px; }"
        )
        pp_layout.addWidget(self.preview_text)

        self.status_bar_box = QWidget(self.preview_panel)
        sb_l = QHBoxLayout(self.status_bar_box)
        sb_l.setContentsMargins(0, 0, 0, 0)
        self.status_lbl = QLabel("Ready to generate reports.", self.status_bar_box)
        self.status_lbl.setFont(QFont("Outfit", 10))
        self.status_lbl.setStyleSheet("color: #8D96A8;")
        sb_l.addWidget(self.status_lbl)
        sb_l.addStretch(1)
        pp_layout.addWidget(self.status_bar_box)

        split_layout.addWidget(self.preview_panel, 1)
        root_layout.addWidget(split_widget, 1)

        # Trigger initial preview
        self.on_report_type_changed()

    def update_db_status(self):
        st = get_db_status()
        t = st.get("type", "SQL")
        self.db_label.setText(f"Connected: {t}")

    def on_report_type_changed(self):
        cur_code = self.type_combo.currentData()
        is_individual = (cur_code == report_service.REPORT_TYPE_STUDENT_INTELLIGENCE)
        self.student_box.setVisible(is_individual)
        if is_individual and not self.sid_entry.text().strip():
            self.sid_entry.setText("1")
        self.trigger_live_preview()

    def get_selected_options(self) -> dict[str, Any]:
        return {
            "include_metrics": self.cb_metrics.isChecked(),
            "include_charts": self.cb_charts.isChecked(),
            "include_risk_factors": self.cb_risk.isChecked(),
            "include_interventions": self.cb_interventions.isChecked(),
            "include_ai_summary": self.cb_ai_summary.isChecked()
        }

    def trigger_live_preview(self):
        rtype = self.type_combo.currentData() or report_service.REPORT_TYPE_STUDENT_INTELLIGENCE
        sid_raw = self.sid_entry.text().strip()
        sid = int(sid_raw) if sid_raw.isdigit() else None
        c_name = self.class_combo.currentText()
        sec = self.sec_combo.currentText()

        params = {
            "report_type": rtype,
            "student_id": sid,
            "class_name": c_name,
            "section": sec,
            "options": self.get_selected_options()
        }

        worker = ReportWorker("preview", params)
        worker.finished.connect(self.on_preview_finished)
        self.active_workers.append(worker)
        worker.start()

    def on_preview_finished(self, res: dict):
        if res.get("success"):
            self.preview_text.setPlainText(res.get("text", ""))
            self.status_lbl.setText("Preview refreshed.")
            self.status_lbl.setStyleSheet("color: #8D96A8;")

    def generate_pdf_report(self):
        rtype = self.type_combo.currentData()
        sid_raw = self.sid_entry.text().strip()
        sid = int(sid_raw) if sid_raw.isdigit() else None

        if rtype == report_service.REPORT_TYPE_STUDENT_INTELLIGENCE and not sid:
            QMessageBox.warning(self, "Missing Student ID", "Please specify a Target Student ID for individual intelligence reports.")
            return

        default_filename = f"Student_Report_{sid}.pdf" if sid else f"Class_Report_{self.class_combo.currentText()}_{self.sec_combo.currentText()}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", default_filename, "PDF Documents (*.pdf)")

        if not file_path:
            return

        self.btn_gen_pdf.setEnabled(False)
        self.btn_gen_pdf.setText("Generating PDF...")
        self.status_lbl.setText("Rendering high-resolution vector PDF...")
        self.status_lbl.setStyleSheet("color: #7C5CFF;")

        params = {
            "report_type": rtype,
            "student_id": sid,
            "class_name": self.class_combo.currentText(),
            "section": self.sec_combo.currentText(),
            "output_path": file_path,
            "options": self.get_selected_options()
        }

        worker = ReportWorker("pdf", params)
        worker.finished.connect(self.on_export_finished)
        self.active_workers.append(worker)
        worker.start()

    def export_csv_report(self):
        rtype = self.type_combo.currentData()
        sid_raw = self.sid_entry.text().strip()
        sid = int(sid_raw) if sid_raw.isdigit() else None

        default_filename = f"student_{sid}_data.csv" if sid else f"class_{self.class_combo.currentText()}_{self.sec_combo.currentText()}_data.csv"
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Spreadsheet", default_filename, "CSV Files (*.csv)")

        if not file_path:
            return

        self.btn_export_csv.setEnabled(False)
        params = {
            "report_type": rtype,
            "student_id": sid,
            "class_name": self.class_combo.currentText(),
            "section": self.sec_combo.currentText(),
            "output_path": file_path,
            "options": self.get_selected_options()
        }

        worker = ReportWorker("csv", params)
        worker.finished.connect(self.on_export_finished)
        self.active_workers.append(worker)
        worker.start()

    def on_export_finished(self, res: dict):
        self.btn_gen_pdf.setEnabled(True)
        self.btn_gen_pdf.setText("📄 Generate PDF Document")
        self.btn_export_csv.setEnabled(True)

        if res.get("success"):
            p = res.get("path")
            self.latest_generated_path = p
            self.status_lbl.setText(f"✓ Successfully generated: {os.path.basename(p)}")
            self.status_lbl.setStyleSheet("color: #30A46C; font-weight: bold;")
            self.btn_open_file.setVisible(True)
            QMessageBox.information(self, "Export Successful", f"Document successfully generated and saved to:\n\n{p}")
        else:
            err = res.get("error", "Unknown error")
            self.status_lbl.setText(f"⚠️ Generation failed: {err}")
            self.status_lbl.setStyleSheet("color: #E5484D;")
            QMessageBox.critical(self, "Generation Error", f"Failed to generate document:\n\n{err}")

    def open_generated_file(self):
        if self.latest_generated_path and os.path.exists(self.latest_generated_path):
            try:
                os.startfile(self.latest_generated_path)
            except Exception as e:
                QMessageBox.warning(self, "Open Error", f"Could not launch file viewer: {e}")

    def closeEvent(self, event):
        for worker in self.active_workers:
            if worker.isRunning():
                worker.terminate()
                worker.wait()
        super().closeEvent(event)
