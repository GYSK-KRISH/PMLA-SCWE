"""PySide6 panel for adding student diagnostic marks and displaying test history logs."""

from __future__ import annotations
import datetime
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QGridLayout, QScrollArea, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from core import student_service, assessment_service
from core.database import get_db_status


class AssessmentsFrame(QWidget):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.active_student_id = None
        self.topics = [
            "Pandas Basics", "SQL SELECT", "SQL JOIN", "Data Visualization",
            "Cyber Safety", "Python Functions", "Digital Wellness",
            "Spreadsheet Skills", "AI Literacy", "Ethics in Technology"
        ]

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
        
        title = QLabel("ACADEMIC ASSESSMENTS & GRADES", header_frame)
        title.setFont(QFont("Outfit", 20, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        h_layout.addWidget(title)
        
        self.db_label = QLabel("", header_frame)
        self.db_label.setFont(QFont("Outfit", 12))
        self.db_label.setStyleSheet("color: #AAAAAA; background: transparent; border: none;")
        h_layout.addWidget(self.db_label, 0, Qt.AlignRight)
        
        layout.addWidget(header_frame)
        self.update_db_status()

        # Selection Panel (Lookup Student)
        lookup_frame = QFrame(self)
        lookup_frame.setObjectName("CardFrame")
        lf_layout = QHBoxLayout(lookup_frame)
        lf_layout.setContentsMargins(20, 10, 20, 10)
        
        lf_layout.addWidget(QLabel("Enter Student ID:", lookup_frame))

        self.sid_entry = QLineEdit(lookup_frame)
        self.sid_entry.setPlaceholderText("e.g. 1")
        self.sid_entry.setFixedWidth(120)
        self.sid_entry.returnPressed.connect(self.load_student_assessment_history)
        lf_layout.addWidget(self.sid_entry)

        search_btn = QPushButton("Load Records", lookup_frame)
        search_btn.setFont(QFont("Outfit", 12, QFont.Bold))
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.clicked.connect(self.load_student_assessment_history)
        lf_layout.addWidget(search_btn)
        
        self.student_info_lbl = QLabel("No student selected.", lookup_frame)
        self.student_info_lbl.setFont(QFont("Outfit", 13, QFont.Bold))
        self.student_info_lbl.setStyleSheet("color: #AAAAAA; background: transparent; border: none;")
        lf_layout.addWidget(self.student_info_lbl)
        
        lf_layout.addStretch(1)
        layout.addWidget(lookup_frame)

        # Content Split Layout (Left: History log list, Right: Add new entry form)
        split_widget = QWidget(self)
        split_layout = QHBoxLayout(split_widget)
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(10)

        # Left Frame: Assessment History List
        self.history_scroll = QScrollArea(split_widget)
        self.history_scroll.setObjectName("CardFrame")
        self.history_scroll.setWidgetResizable(True)
        self.history_content = QWidget()
        self.history_layout = QVBoxLayout(self.history_content)
        self.history_layout.setContentsMargins(15, 15, 15, 15)
        self.history_layout.setSpacing(6)
        self.history_layout.setAlignment(Qt.AlignTop)
        self.history_scroll.setWidget(self.history_content)
        split_layout.addWidget(self.history_scroll, 3)

        # Right Frame: Register New Grade Form
        self.form_panel = QFrame(split_widget)
        self.form_panel.setObjectName("CardFrame")
        self.form_panel.setFixedWidth(340)
        form_layout = QVBoxLayout(self.form_panel)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(10)
        form_layout.setAlignment(Qt.AlignTop)

        form_title = QLabel("ADD NEW ASSESSMENT ENTRY", self.form_panel)
        form_title.setFont(QFont("Outfit", 14, QFont.Bold))
        form_title.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        form_title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(form_title)
        
        form_layout.addWidget(QLabel("Objective / Topic:", self.form_panel))
        self.topic_combo = QComboBox(self.form_panel)
        self.topic_combo.addItems(self.topics)
        form_layout.addWidget(self.topic_combo)

        form_layout.addWidget(QLabel("Score Obtained*:", self.form_panel))
        self.score_entry = QLineEdit(self.form_panel)
        self.score_entry.setPlaceholderText("e.g. 85.5")
        form_layout.addWidget(self.score_entry)

        form_layout.addWidget(QLabel("Maximum Score:", self.form_panel))
        self.max_entry = QLineEdit(self.form_panel)
        self.max_entry.setPlaceholderText("Default 100")
        form_layout.addWidget(self.max_entry)

        form_layout.addWidget(QLabel("Test Date (YYYY-MM-DD)*:", self.form_panel))
        self.date_entry = QLineEdit(self.form_panel)
        self.date_entry.setPlaceholderText("YYYY-MM-DD")
        self.date_entry.setText(datetime.date.today().isoformat())
        form_layout.addWidget(self.date_entry)

        self.form_status_lbl = QLabel("", self.form_panel)
        self.form_status_lbl.setFont(QFont("Outfit", 12))
        self.form_status_lbl.setAlignment(Qt.AlignCenter)
        self.form_status_lbl.setWordWrap(True)
        form_layout.addWidget(self.form_status_lbl)

        save_btn = QPushButton("SUBMIT GRADE", self.form_panel)
        save_btn.setObjectName("PrimaryButton")
        save_btn.setFixedHeight(40)
        save_btn.setFont(QFont("Outfit", 13, QFont.Bold))
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.submit_grade)
        form_layout.addWidget(save_btn)

        split_layout.addWidget(self.form_panel, 2)
        layout.addWidget(split_widget, 1)

        # Setup dynamic placeholder inside logs area
        self.draw_history_placeholder("Enter a Student ID above to fetch academic grades logs.")

    def update_db_status(self):
        status = get_db_status()
        self.db_label.setText(status["display"])
        color = "#34A853" if status["backend"] == "MySQL" else "#FFD600"
        self.db_label.setStyleSheet(f"color: {color}; background: transparent; border: none;")

    def draw_history_placeholder(self, text: str):
        while self.history_layout.count() > 0:
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        lbl = QLabel(text, self.history_content)
        lbl.setStyleSheet("color: #AAAAAA; font-size: 13px;")
        lbl.setAlignment(Qt.AlignCenter)
        self.history_layout.addWidget(lbl)

    def load_student_assessment_history(self):
        self.update_db_status()
        self.active_student_id = None
        self.student_info_lbl.setText("No student selected.")
        self.student_info_lbl.setStyleSheet("color: #AAAAAA; background: transparent; border: none;")

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
        self.student_info_lbl.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")

        # Fetch logs
        logs = assessment_service.get_assessment_history(sid)

        # Clear existing logs
        while self.history_layout.count() > 0:
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not logs:
            no_logs_lbl = QLabel("No academic grade records found for this student.", self.history_content)
            no_logs_lbl.setStyleSheet("color: #AAAAAA; font-size: 13px;")
            no_logs_lbl.setAlignment(Qt.AlignCenter)
            self.history_layout.addWidget(no_logs_lbl)
            return

        # Headers
        headers_widget = QWidget(self.history_content)
        headers_layout = QHBoxLayout(headers_widget)
        headers_layout.setContentsMargins(15, 5, 15, 5)
        
        lbl_date = QLabel("Test Date", headers_widget)
        lbl_date.setFont(QFont("Outfit", 12, QFont.Bold))
        lbl_date.setStyleSheet("color: #AAAAAA; background: transparent; border: none;")
        headers_layout.addWidget(lbl_date, 2)

        lbl_desc = QLabel("Objective ID / Description", headers_widget)
        lbl_desc.setFont(QFont("Outfit", 12, QFont.Bold))
        lbl_desc.setStyleSheet("color: #AAAAAA; background: transparent; border: none;")
        headers_layout.addWidget(lbl_desc, 4)

        lbl_score = QLabel("Score", headers_widget)
        lbl_score.setFont(QFont("Outfit", 12, QFont.Bold))
        lbl_score.setStyleSheet("color: #AAAAAA; background: transparent; border: none;")
        headers_layout.addWidget(lbl_score, 2)

        self.history_layout.addWidget(headers_widget)

        # Roster list rows
        for idx, log in enumerate(logs):
            row = QFrame(self.history_content)
            row.setObjectName("InnerCardFrame")
            row.setFixedHeight(40)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(15, 0, 15, 0)

            date_lbl = QLabel(str(log["test_date"]), row)
            date_lbl.setFont(QFont("Outfit", 12))
            date_lbl.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
            row_layout.addWidget(date_lbl, 2)

            topic_id = log["objective_id"]
            topic_name = self.topics[(topic_id - 1) % len(self.topics)] if topic_id else "General Topic"
            desc_lbl = QLabel(f"ID {topic_id or 0} - {topic_name}", row)
            desc_lbl.setFont(QFont("Outfit", 12, QFont.Bold))
            desc_lbl.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
            row_layout.addWidget(desc_lbl, 4)

            score_str = f"{log['score_obtained']:.1f} / {log['max_score']:.1f}"
            score_lbl = QLabel(score_str, row)
            score_lbl.setFont(QFont("Outfit", 12, QFont.Bold))
            score_lbl.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
            row_layout.addWidget(score_lbl, 2)

            self.history_layout.addWidget(row)

    def submit_grade(self):
        self.update_db_status()
        
        if not self.active_student_id:
            self.show_form_message("Load a valid student profile first.", is_error=True)
            return

        topic = self.topic_combo.currentText()
        objective_id = self.topics.index(topic) + 1

        score_raw = self.score_entry.text().strip()
        max_raw = self.max_entry.text().strip() or "100"
        date_raw = self.date_entry.text().strip()

        if not score_raw or not date_raw:
            self.show_form_message("Score and Date fields are mandatory.", is_error=True)
            return

        try:
            score = float(score_raw)
            max_score = float(max_raw)
        except ValueError:
            self.show_form_message("Scores must be numerical decimal inputs.", is_error=True)
            return

        if score < 0 or max_score <= 0:
            self.show_form_message("Invalid score values supplied.", is_error=True)
            return

        if score > max_score:
            self.show_form_message("Score cannot exceed maximum value.", is_error=True)
            return

        # Validate Date format
        try:
            datetime.datetime.strptime(date_raw, "%Y-%m-%d")
        except ValueError:
            self.show_form_message("Invalid date format. Use YYYY-MM-DD.", is_error=True)
            return

        payload = {
            "student_id": self.active_student_id,
            "objective_id": objective_id,
            "score_obtained": score,
            "max_score": max_score,
            "test_date": date_raw
        }

        try:
            if assessment_service.add_assessment(payload):
                from core.database import log_activity
                log_activity(f"Assessment score added for Student ID {self.active_student_id}")
                self.show_form_message("Grade saved successfully!", is_error=False)
                self.score_entry.clear()
                self.max_entry.clear()
                # Reload list
                self.load_student_assessment_history()
            else:
                self.show_form_message("Database failed to record grade.", is_error=True)
        except Exception as e:
            self.show_form_message(f"Database error: {e}", is_error=True)

    def show_form_message(self, text: str, is_error: bool = False):
        color = "#e74c3c" if is_error else "#2ecc71"
        self.form_status_lbl.setText(text)
        self.form_status_lbl.setStyleSheet(f"color: {color};")
        QTimer.singleShot(4000, lambda: self.form_status_lbl.clear())
