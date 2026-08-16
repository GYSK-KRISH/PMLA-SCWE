"""PySide6 panel for marking and saving bulk student attendance."""

from __future__ import annotations
import datetime
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QScrollArea, QComboBox, QButtonGroup
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from core import attendance_service
from core.database import get_db_status


class AttendanceFrame(QWidget):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.student_rows = []
        self.attendance_groups = {}  # student_id -> QButtonGroup

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
        
        title = QLabel("ATTENDANCE REGISTRY", header_frame)
        title.setFont(QFont("Outfit", 20, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        h_layout.addWidget(title)
        
        self.db_label = QLabel("", header_frame)
        self.db_label.setFont(QFont("Outfit", 12))
        self.db_label.setStyleSheet("color: #AAAAAA; background: transparent; border: none;")
        h_layout.addWidget(self.db_label, 0, Qt.AlignRight)
        
        layout.addWidget(header_frame)
        self.update_db_status()

        # Filters controls panel
        controls_frame = QFrame(self)
        controls_frame.setObjectName("CardFrame")
        cf_layout = QHBoxLayout(controls_frame)
        cf_layout.setContentsMargins(20, 10, 20, 10)
        
        cf_layout.addWidget(QLabel("Select Class:", controls_frame))
        
        self.classes = ["XII-A", "XII-B", "XI-A", "XI-B", "X-A", "X-B"]
        self.class_selector = QComboBox(controls_frame)
        self.class_selector.addItems(self.classes)
        self.class_selector.currentIndexChanged.connect(self.load_class_roster)
        cf_layout.addWidget(self.class_selector)
        
        cf_layout.addSpacing(20)
        cf_layout.addWidget(QLabel("Date (YYYY-MM-DD):", controls_frame))

        self.date_entry = QLineEdit(controls_frame)
        self.date_entry.setFixedWidth(140)
        self.date_entry.setText(datetime.date.today().isoformat())
        self.date_entry.returnPressed.connect(self.load_class_roster)
        cf_layout.addWidget(self.date_entry)

        load_btn = QPushButton("Load Cohort", controls_frame)
        load_btn.setFont(QFont("Outfit", 12, QFont.Bold))
        load_btn.setCursor(Qt.PointingHandCursor)
        load_btn.clicked.connect(self.load_class_roster)
        cf_layout.addWidget(load_btn)
        
        cf_layout.addStretch(1)
        layout.addWidget(controls_frame)

        # Student attendance roster table frame
        self.roster_scroll = QScrollArea(self)
        self.roster_scroll.setObjectName("CardFrame")
        self.roster_scroll.setWidgetResizable(True)
        self.roster_content = QWidget()
        self.roster_layout = QVBoxLayout(self.roster_content)
        self.roster_layout.setContentsMargins(15, 15, 15, 15)
        self.roster_layout.setSpacing(6)
        self.roster_layout.setAlignment(Qt.AlignTop)
        self.roster_scroll.setWidget(self.roster_content)
        layout.addWidget(self.roster_scroll, 1)

        # Bottom actions
        actions_frame = QWidget(self)
        af_layout = QHBoxLayout(actions_frame)
        af_layout.setContentsMargins(10, 10, 10, 10)
        
        self.status_msg = QLabel("", actions_frame)
        self.status_msg.setFont(QFont("Outfit", 14))
        af_layout.addWidget(self.status_msg)
        
        af_layout.addStretch(1)

        self.save_btn = QPushButton("SAVE ALL ATTENDANCE", actions_frame)
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.setFixedHeight(40)
        self.save_btn.setFixedWidth(200)
        self.save_btn.setFont(QFont("Outfit", 13, QFont.Bold))
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_all_attendance)
        af_layout.addWidget(self.save_btn)

        layout.addWidget(actions_frame)

        # Initial load
        self.load_class_roster()

    def update_db_status(self):
        status = get_db_status()
        self.db_label.setText(status["display"])
        color = "#34A853" if status["backend"] == "MySQL" else "#FFD600"
        self.db_label.setStyleSheet(f"color: {color}; background: transparent; border: none;")

    def load_class_roster(self, *args):
        self.update_db_status()

        # Clear existing roster entries
        while self.roster_layout.count() > 0:
            item = self.roster_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.attendance_groups.clear()
        self.student_rows.clear()

        # Retrieve values
        selected_class = self.class_selector.currentText()
        date_str = self.date_entry.text().strip()

        # Validate date string
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            self.show_message("Invalid date format. Use YYYY-MM-DD.", is_error=True)
            return

        # Fetch students and existing records
        students = attendance_service.get_students_by_class(selected_class)
        existing_attendance = attendance_service.get_attendance_for_date_and_class(date_str, selected_class)

        if not students:
            no_students_lbl = QLabel("No students found in this class section.", self.roster_content)
            no_students_lbl.setStyleSheet("color: #95a5a6; font-size: 14px;")
            no_students_lbl.setAlignment(Qt.AlignCenter)
            self.roster_layout.addWidget(no_students_lbl)
            return

        # Draw Table Headers
        headers_widget = QWidget(self.roster_content)
        headers_layout = QHBoxLayout(headers_widget)
        headers_layout.setContentsMargins(15, 5, 15, 5)
        
        lbl_name = QLabel("Student Name", headers_widget)
        lbl_name.setFont(QFont("Outfit", 12, QFont.Bold))
        lbl_name.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        headers_layout.addWidget(lbl_name, 2)
        
        lbl_roll = QLabel("Roll Number / Info", headers_widget)
        lbl_roll.setFont(QFont("Outfit", 12, QFont.Bold))
        lbl_roll.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        headers_layout.addWidget(lbl_roll, 1)
        
        lbl_status = QLabel("Attendance Status", headers_widget)
        lbl_status.setFont(QFont("Outfit", 12, QFont.Bold))
        lbl_status.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        headers_layout.addWidget(lbl_status, 1)
        
        self.roster_layout.addWidget(headers_widget)

        # Populate student rows
        for idx, student in enumerate(students, start=1):
            student_id = student["student_id"]
            full_name = f"{student['first_name']} {student['last_name']}"
            roll_number = f"ID: {student_id}"

            row_frame = QFrame(self.roster_content)
            row_frame.setObjectName("InnerCardFrame")
            row_frame.setFixedHeight(45)
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(15, 0, 15, 0)

            # Name Label
            name_lbl = QLabel(full_name, row_frame)
            name_lbl.setFont(QFont("Outfit", 13, QFont.Bold))
            name_lbl.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
            row_layout.addWidget(name_lbl, 2)

            # Info Label
            info_lbl = QLabel(roll_number, row_frame)
            info_lbl.setFont(QFont("Outfit", 12))
            info_lbl.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
            row_layout.addWidget(info_lbl, 1)

            # Segmented Present/Absent Buttons using checkable QPushButton + QButtonGroup
            btn_container = QWidget(row_frame)
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(2)
            
            present_btn = QPushButton("Present", btn_container)
            present_btn.setCheckable(True)
            present_btn.setFixedSize(65, 26)
            present_btn.setCursor(Qt.PointingHandCursor)
            present_btn.setStyleSheet(
                "QPushButton { background-color: #10131D; color: #8D96A8; border: 1px solid rgba(255,255,255,0.08); border-radius: 4px; }"
                "QPushButton:checked { background-color: #30C48D; border-color: #30C48D; color: white; font-weight: bold; }"
            )
            
            absent_btn = QPushButton("Absent", btn_container)
            absent_btn.setCheckable(True)
            absent_btn.setFixedSize(65, 26)
            absent_btn.setCursor(Qt.PointingHandCursor)
            absent_btn.setStyleSheet(
                "QPushButton { background-color: #10131D; color: #8D96A8; border: 1px solid rgba(255,255,255,0.08); border-radius: 4px; }"
                "QPushButton:checked { background-color: #E5484D; border-color: #E5484D; color: white; font-weight: bold; }"
            )
            
            btn_layout.addWidget(present_btn)
            btn_layout.addWidget(absent_btn)
            
            group = QButtonGroup(row_frame)
            group.addButton(present_btn)
            group.addButton(absent_btn)
            group.setExclusive(True)
            
            # Select current status
            status_val = existing_attendance.get(student_id, "Present")
            if status_val == "Present":
                present_btn.setChecked(True)
            else:
                absent_btn.setChecked(True)
            
            row_layout.addWidget(btn_container, 1)
            self.attendance_groups[student_id] = group
            self.roster_layout.addWidget(row_frame)

        self.show_message(f"Roster loaded for Class {selected_class} on date {date_str}.")

    def save_all_attendance(self):
        self.update_db_status()

        date_str = self.date_entry.text().strip()
        selected_class = self.class_selector.currentText()

        # Validate date string
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            self.show_message("Invalid date format. Cannot save.", is_error=True)
            return

        if not self.attendance_groups:
            self.show_message("No student records available to save.", is_error=True)
            return

        # Extract values
        records = {}
        for student_id, group in self.attendance_groups.items():
            btn = group.checkedButton()
            status = btn.text() if btn else "Present"
            records[student_id] = status

        try:
            ok = attendance_service.save_attendance(date_str, selected_class, records)
            if ok:
                from core.database import log_activity
                log_activity(f"Attendance marked for {selected_class}")
                self.show_message(f"Successfully saved attendance for {len(records)} students!", is_error=False)
            else:
                self.show_message("Service failed to save attendance records.", is_error=True)
        except Exception as e:
            self.show_message(f"Error during saving: {e}", is_error=True)

    def show_message(self, message: str, is_error: bool = False):
        color = "#e74c3c" if is_error else "#2ecc71"
        self.status_msg.setText(message)
        self.status_msg.setStyleSheet(f"color: {color};")
        QTimer.singleShot(4000, lambda: self.status_msg.clear())
