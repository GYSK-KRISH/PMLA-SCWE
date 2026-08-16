"""PySide6 panel for lodging cyber audits and showing digital distraction/screen logs."""

from __future__ import annotations
import datetime
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QGridLayout, QScrollArea, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from core import student_service, wellness_service
from core.database import get_db_status


class WellnessFrame(QWidget):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.active_student_id = None

        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Header Section
        header_frame = QFrame(self)
        header_frame.setObjectName("CardFrame")
        header_frame.setFixedHeight(60)
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("STUDENT CYBER WELLNESS AUDIT", header_frame)
        title.setFont(QFont("Outfit", 20, QFont.Bold))
        title.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
        h_layout.addWidget(title)
        
        self.db_label = QLabel("", header_frame)
        self.db_label.setFont(QFont("Outfit", 12))
        self.db_label.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        h_layout.addWidget(self.db_label, 0, Qt.AlignRight)
        
        layout.addWidget(header_frame)
        self.update_db_status()

        # Selection Control Panel
        lookup_frame = QFrame(self)
        lookup_frame.setObjectName("CardFrame")
        lf_layout = QHBoxLayout(lookup_frame)
        lf_layout.setContentsMargins(20, 10, 20, 10)
        
        lf_layout.addWidget(QLabel("Enter Student ID:", lookup_frame))

        self.sid_entry = QLineEdit(lookup_frame)
        self.sid_entry.setPlaceholderText("e.g. 1")
        self.sid_entry.setFixedWidth(120)
        self.sid_entry.returnPressed.connect(self.load_student_wellness_history)
        lf_layout.addWidget(self.sid_entry)

        search_btn = QPushButton("Load Records", lookup_frame)
        search_btn.setFont(QFont("Outfit", 12, QFont.Bold))
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.clicked.connect(self.load_student_wellness_history)
        lf_layout.addWidget(search_btn)
        
        self.student_info_lbl = QLabel("No student selected.", lookup_frame)
        self.student_info_lbl.setFont(QFont("Outfit", 13, QFont.Bold))
        self.student_info_lbl.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        lf_layout.addWidget(self.student_info_lbl)
        
        lf_layout.addStretch(1)
        layout.addWidget(lookup_frame)

        # Split Layout
        split_widget = QWidget(self)
        split_layout = QHBoxLayout(split_widget)
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(10)

        # Left Frame: Audit History Logs
        self.history_scroll = QScrollArea(split_widget)
        self.history_scroll.setObjectName("CardFrame")
        self.history_scroll.setWidgetResizable(True)
        self.history_content = QWidget()
        self.history_layout = QVBoxLayout(self.history_content)
        self.history_layout.setContentsMargins(15, 15, 15, 15)
        self.history_layout.setSpacing(8)
        self.history_layout.setAlignment(Qt.AlignTop)
        self.history_scroll.setWidget(self.history_content)
        split_layout.addWidget(self.history_scroll, 3)

        # Right Frame: New Audit Form Panel
        self.form_panel = QFrame(split_widget)
        self.form_panel.setObjectName("CardFrame")
        self.form_panel.setFixedWidth(340)
        form_layout = QVBoxLayout(self.form_panel)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(6)
        form_layout.setAlignment(Qt.AlignTop)

        form_title = QLabel("SUBMIT NEW CYBER AUDIT", self.form_panel)
        form_title.setFont(QFont("Outfit", 14, QFont.Bold))
        form_title.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
        form_title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(form_title)
        
        form_scroll = QScrollArea(self.form_panel)
        form_scroll.setWidgetResizable(True)
        form_scroll_content = QWidget()
        form_scroll_layout = QVBoxLayout(form_scroll_content)
        form_scroll_layout.setContentsMargins(0, 5, 0, 5)
        form_scroll_layout.setSpacing(10)
        
        # 1. Screen Times
        form_scroll_layout.addWidget(QLabel("Daily Screen Time (hrs)*:", form_scroll_content))
        self.daily_entry = QLineEdit(form_scroll_content)
        self.daily_entry.setPlaceholderText("Study + Rec")
        form_scroll_layout.addWidget(self.daily_entry)

        form_scroll_layout.addWidget(QLabel("Study Screen Time (hrs)*:", form_scroll_content))
        self.study_entry = QLineEdit(form_scroll_content)
        self.study_entry.setPlaceholderText("e.g. 3.5")
        form_scroll_layout.addWidget(self.study_entry)

        form_scroll_layout.addWidget(QLabel("Recreational Screen (hrs)*:", form_scroll_content))
        self.rec_entry = QLineEdit(form_scroll_content)
        self.rec_entry.setPlaceholderText("e.g. 1.5")
        form_scroll_layout.addWidget(self.rec_entry)

        # 2. Sleep
        form_scroll_layout.addWidget(QLabel("Sleep Duration (hrs)*:", form_scroll_content))
        self.sleep_entry = QLineEdit(form_scroll_content)
        self.sleep_entry.setPlaceholderText("e.g. 8.0")
        form_scroll_layout.addWidget(self.sleep_entry)

        # 3. Distraction (1-5)
        form_scroll_layout.addWidget(QLabel("Digital Distraction (1-5)*:", form_scroll_content))
        self.distract_combo = QComboBox(form_scroll_content)
        self.distract_combo.addItems(["1", "2", "3", "4", "5"])
        self.distract_combo.setCurrentText("1")
        form_scroll_layout.addWidget(self.distract_combo)

        # 4. Safety (1-5)
        form_scroll_layout.addWidget(QLabel("Cyber Safety (1-5)*:", form_scroll_content))
        self.safety_combo = QComboBox(form_scroll_content)
        self.safety_combo.addItems(["1", "2", "3", "4", "5"])
        self.safety_combo.setCurrentText("5")
        form_scroll_layout.addWidget(self.safety_combo)

        # 5. Remarks & Date
        form_scroll_layout.addWidget(QLabel("Remarks:", form_scroll_content))
        self.remarks_entry = QLineEdit(form_scroll_content)
        self.remarks_entry.setPlaceholderText("e.g. Balanced logs")
        form_scroll_layout.addWidget(self.remarks_entry)

        form_scroll_layout.addWidget(QLabel("Audit Date (YYYY-MM-DD):", form_scroll_content))
        self.date_entry = QLineEdit(form_scroll_content)
        self.date_entry.setPlaceholderText("YYYY-MM-DD")
        self.date_entry.setText(datetime.date.today().isoformat())
        form_scroll_layout.addWidget(self.date_entry)

        form_scroll.setWidget(form_scroll_content)
        form_layout.addWidget(form_scroll, 1)

        self.form_status_lbl = QLabel("", self.form_panel)
        self.form_status_lbl.setFont(QFont("Outfit", 12))
        self.form_status_lbl.setAlignment(Qt.AlignCenter)
        self.form_status_lbl.setWordWrap(True)
        form_layout.addWidget(self.form_status_lbl)

        save_btn = QPushButton("SUBMIT AUDIT", self.form_panel)
        save_btn.setObjectName("PrimaryButton")
        save_btn.setFixedHeight(38)
        save_btn.setFont(QFont("Outfit", 13, QFont.Bold))
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.submit_cyber_audit)
        form_layout.addWidget(save_btn)

        split_layout.addWidget(self.form_panel, 2)
        layout.addWidget(split_widget, 1)

        # Setup dynamic placeholder inside logs area
        self.draw_history_placeholder("Enter a Student ID above to load cyber wellness history.")

    def update_db_status(self):
        status = get_db_status()
        self.db_label.setText(status["display"])
        color = "#30C48D" if status["backend"] == "MySQL" else "#F5A524"
        self.db_label.setStyleSheet(f"color: {color}; background: transparent; border: none;")

    def draw_history_placeholder(self, text: str):
        while self.history_layout.count() > 0:
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        lbl = QLabel(text, self.history_content)
        lbl.setStyleSheet("color: #8D96A8; font-size: 13px;")
        lbl.setAlignment(Qt.AlignCenter)
        self.history_layout.addWidget(lbl)

    def load_student_wellness_history(self):
        self.update_db_status()
        self.active_student_id = None
        self.student_info_lbl.setText("No student selected.")
        self.student_info_lbl.setStyleSheet("color: #8D96A8; background: transparent; border: none;")

        sid_raw = self.sid_entry.text().strip()
        if not sid_raw:
            self.draw_history_placeholder("Please enter a Student ID.")
            return

        try:
            sid = int(sid_raw)
        except ValueError:
            self.draw_history_placeholder("Student ID must be a numeric value.")
            return

        res = student_service.search_students(str(sid))
        if not res:
            self.draw_history_placeholder(f"Student ID {sid} does not exist.")
            return

        student = res[0]
        self.active_student_id = sid
        self.student_info_lbl.setText(f"Active: {student['first_name']} {student['last_name']} ({student['class_section']})")
        self.student_info_lbl.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")

        # Fetch audits
        history = wellness_service.get_student_audits(sid)

        # Clear existing entries
        while self.history_layout.count() > 0:
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not history:
            no_logs = QLabel("No cyber wellness audits lodged for this student.", self.history_content)
            no_logs.setStyleSheet("color: #8D96A8; font-size: 13px;")
            no_logs.setAlignment(Qt.AlignCenter)
            self.history_layout.addWidget(no_logs)
            return

        for audit in history:
            card = QFrame(self.history_content)
            card.setObjectName("InnerCardFrame")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 10, 15, 10)
            card_layout.setSpacing(6)

            top_line = QWidget(card)
            top_layout = QHBoxLayout(top_line)
            top_layout.setContentsMargins(0, 0, 0, 0)
            
            date_lbl = QLabel(f"Date: {audit['audit_date']}", top_line)
            date_lbl.setFont(QFont("Outfit", 12, QFont.Bold))
            date_lbl.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
            top_layout.addWidget(date_lbl)

            score_lbl = QLabel(f"Wellness Index: {audit['wellness_score'] or 0.0:.1f}%", top_line)
            score_lbl.setFont(QFont("Outfit", 12, QFont.Bold))
            score_lbl.setStyleSheet("color: #30C48D; background: transparent; border: none;")
            top_layout.addWidget(score_lbl, 0, Qt.AlignRight)

            card_layout.addWidget(top_line)

            metrics_lbl = QLabel(
                f"Screen: {audit['daily_screen_time']:.1f}h (Study: {audit['study_screen_time']:.1f}h / Rec: {audit['recreational_screen_time']:.1f}h)  |  Sleep: {audit['sleep_duration']:.1f}h\n"
                f"Distraction: {audit['digital_distraction_level']}/5  |  Safety Awareness: {audit['cyber_safety_awareness']}/5",
                card
            )
            metrics_lbl.setFont(QFont("Outfit", 11))
            metrics_lbl.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
            card_layout.addWidget(metrics_lbl)

            if audit.get("remarks"):
                rem_lbl = QLabel(f"Remarks: {audit['remarks']}", card)
                rem_lbl.setFont(QFont("Outfit", 11))
                rem_lbl.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
                card_layout.addWidget(rem_lbl)

            self.history_layout.addWidget(card)

    def submit_cyber_audit(self):
        self.update_db_status()
        
        if not self.active_student_id:
            self.show_form_message("Load a student profile first.", is_error=True)
            return

        daily_raw = self.daily_entry.text().strip()
        study_raw = self.study_entry.text().strip()
        rec_raw = self.rec_entry.text().strip()
        sleep_raw = self.sleep_entry.text().strip()
        distract_raw = self.distract_combo.currentText()
        safety_raw = self.safety_combo.currentText()
        remarks_val = self.remarks_entry.text().strip() or None
        date_raw = self.date_entry.text().strip()

        if not daily_raw or not study_raw or not rec_raw or not sleep_raw or not date_raw:
            self.show_form_message("Please fill in all mandatory fields.", is_error=True)
            return

        try:
            daily = float(daily_raw)
            study = float(study_raw)
            rec = float(rec_raw)
            sleep = float(sleep_raw)
            distract = int(distract_raw)
            safety = int(safety_raw)
        except ValueError:
            self.show_form_message("Check numeric fields for invalid input formats.", is_error=True)
            return

        # Prepare payload
        payload = {
            "student_id": self.active_student_id,
            "daily_screen_time": daily,
            "study_screen_time": study,
            "recreational_screen_time": rec,
            "sleep_duration": sleep,
            "digital_distraction_level": distract,
            "cyber_safety_awareness": safety,
            "remarks": remarks_val,
            "audit_date": date_raw
        }

        # Run validations
        errors = wellness_service.validate_audit_data(payload)
        if errors:
            self.show_form_message(errors[0], is_error=True)
            return

        try:
            if wellness_service.add_cyber_audit(payload):
                from core.database import log_activity
                log_activity(f"Cyber wellness audit completed for Student ID {self.active_student_id}")
                self.show_form_message("Wellness audit saved successfully!", is_error=False)
                # Clear fields
                self.daily_entry.clear()
                self.study_entry.clear()
                self.rec_entry.clear()
                self.sleep_entry.clear()
                self.remarks_entry.clear()
                # Reload list
                self.load_student_wellness_history()
            else:
                self.show_form_message("Database failed to insert audit record.", is_error=True)
        except Exception as e:
            self.show_form_message(f"Database error: {e}", is_error=True)

    def show_form_message(self, text: str, is_error: bool = False):
        color = "#E5484D" if is_error else "#30C48D"
        self.form_status_lbl.setText(text)
        self.form_status_lbl.setStyleSheet(f"color: {color};")
        QTimer.singleShot(4000, lambda: self.form_status_lbl.clear())
