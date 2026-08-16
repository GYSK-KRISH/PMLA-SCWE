"""PySide6 panel for student registration, search, and CRUD administration."""

from __future__ import annotations
import datetime
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QGridLayout, QScrollArea, QDialog, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from core import student_service
from .student_profile_dialog import StudentProfileDialog


class StudentRowWidget(QFrame):
    def __init__(self, parent, student, edit_cmd, delete_cmd, profile_cmd):
        super().__init__(parent)
        self.setObjectName("InnerCardFrame")
        self.setFixedHeight(48)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        
        sid = student["student_id"]
        name = f"{student['first_name']} {student['last_name']}"
        class_sec = student["class_section"]
        email = student["email"] or "N/A"
        phone = student["phone"] or "N/A"
        
        sid_lbl = QLabel(str(sid), self)
        sid_lbl.setFixedWidth(50)
        layout.addWidget(sid_lbl)
        
        name_lbl = QLabel(name, self)
        name_lbl.setStyleSheet("font-weight: bold; color: #F5F7FA; background: transparent; border: none;")
        layout.addWidget(name_lbl, 3)
        
        class_lbl = QLabel(class_sec, self)
        class_lbl.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(class_lbl, 2)
        
        email_lbl = QLabel(email, self)
        email_lbl.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        layout.addWidget(email_lbl, 3)
        
        phone_lbl = QLabel(phone, self)
        phone_lbl.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        layout.addWidget(phone_lbl, 2)
        
        # Actions Sub-widget
        actions_widget = QWidget(self)
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)
        actions_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        profile_btn = QPushButton("360° Profile", actions_widget)
        profile_btn.setStyleSheet(
            "QPushButton { background-color: rgba(124, 92, 255, 0.15); color: #A084FF;"
            " border: 1px solid rgba(124, 92, 255, 0.35); border-radius: 6px; font-weight: bold; padding: 4px 10px; font-size: 11px; }"
            "QPushButton:hover { background-color: rgba(124, 92, 255, 0.30); color: #C0AAFF; }"
        )
        profile_btn.setCursor(Qt.PointingHandCursor)
        profile_btn.clicked.connect(lambda: profile_cmd(sid))
        actions_layout.addWidget(profile_btn)

        edit_btn = QPushButton("Edit", actions_widget)
        edit_btn.setStyleSheet(
            "QPushButton { background-color: #151925; color: #F5F7FA;"
            " border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 6px; font-weight: 500; padding: 4px 12px; font-size: 11px; }"
            "QPushButton:hover { background-color: #202637; border-color: rgba(255, 255, 255, 0.25); }"
        )
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(lambda: edit_cmd(student))
        actions_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete", actions_widget)
        delete_btn.setStyleSheet(
            "QPushButton { color: #E5484D; border: 1px solid rgba(229, 72, 77, 0.35); background-color: rgba(229, 72, 77, 0.10); border-radius: 6px; font-weight: 500; padding: 4px 12px; font-size: 11px; }"
            "QPushButton:hover { background-color: rgba(229, 72, 77, 0.22); border-color: #E5484D; }"
        )
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(lambda: delete_cmd(sid))
        actions_layout.addWidget(delete_btn)
        
        layout.addWidget(actions_widget, 3)



class StudentFormDialog(QDialog):
    def __init__(self, parent, student_data=None):
        super().__init__(parent)
        self.student_data = student_data
        self.is_edit = student_data is not None
        self.setWindowTitle("Edit Student Profile" if self.is_edit else "Register New Student")
        self.setFixedSize(450, 480)
        self.setStyleSheet(parent.styleSheet())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        
        title_lbl = QLabel(self.windowTitle().upper(), self)
        title_lbl.setFont(QFont("Outfit", 18, QFont.Bold))
        title_lbl.setStyleSheet("color: #F5F7FA;")
        title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_lbl)
        
        form = QWidget(self)
        form_layout = QGridLayout(form)
        form_layout.setContentsMargins(0, 10, 0, 10)
        
        # Inputs mapping
        self.inputs = {}
        
        # 1. First Name
        form_layout.addWidget(QLabel("First Name*:", form), 0, 0)
        self.inputs["first_name"] = QLineEdit(form)
        form_layout.addWidget(self.inputs["first_name"], 0, 1)
        
        # 2. Last Name
        form_layout.addWidget(QLabel("Last Name*:", form), 1, 0)
        self.inputs["last_name"] = QLineEdit(form)
        form_layout.addWidget(self.inputs["last_name"], 1, 1)
        
        # 3. Class Section
        form_layout.addWidget(QLabel("Class/Section* (e.g. XII-A):", form), 2, 0)
        self.inputs["class_section"] = QLineEdit(form)
        form_layout.addWidget(self.inputs["class_section"], 2, 1)
        
        # 4. DOB
        form_layout.addWidget(QLabel("Date of Birth (YYYY-MM-DD):", form), 3, 0)
        self.inputs["dob"] = QLineEdit(form)
        self.inputs["dob"].setPlaceholderText("YYYY-MM-DD")
        form_layout.addWidget(self.inputs["dob"], 3, 1)
        
        # 5. Gender
        form_layout.addWidget(QLabel("Gender (M/F/O):", form), 4, 0)
        self.gender_combo = QComboBox(form)
        self.gender_combo.addItems(["M", "F", "O"])
        self.gender_combo.setCurrentText("O")
        form_layout.addWidget(self.gender_combo, 4, 1)
        
        # 6. Email
        form_layout.addWidget(QLabel("Email Address:", form), 5, 0)
        self.inputs["email"] = QLineEdit(form)
        form_layout.addWidget(self.inputs["email"], 5, 1)
        
        # 7. Phone
        form_layout.addWidget(QLabel("Phone Number:", form), 6, 0)
        self.inputs["phone"] = QLineEdit(form)
        form_layout.addWidget(self.inputs["phone"], 6, 1)
        
        layout.addWidget(form)
        
        # Status Label
        self.status_lbl = QLabel("", self)
        self.status_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_lbl)
        
        # Buttons
        btn_box = QHBoxLayout()
        save_btn = QPushButton("SAVE PROFILE", self)
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self.save)
        btn_box.addWidget(save_btn)
        
        cancel_btn = QPushButton("CANCEL", self)
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)
        
        layout.addLayout(btn_box)
        
        if self.is_edit:
            self.load_student_data()

    def load_student_data(self):
        sd = self.student_data
        self.inputs["first_name"].setText(sd["first_name"])
        self.inputs["last_name"].setText(sd["last_name"])
        self.inputs["class_section"].setText(sd["class_section"])
        if sd.get("dob"):
            self.inputs["dob"].setText(str(sd["dob"]))
        self.gender_combo.setCurrentText(sd.get("gender", "O"))
        if sd.get("email"):
            self.inputs["email"].setText(sd["email"])
        if sd.get("phone"):
            self.inputs["phone"].setText(sd["phone"])

    def save(self):
        first = self.inputs["first_name"].text().strip()
        last = self.inputs["last_name"].text().strip()
        cls = self.inputs["class_section"].text().strip()
        dob_val = self.inputs["dob"].text().strip() or None
        gender_val = self.gender_combo.currentText()
        email_val = self.inputs["email"].text().strip() or None
        phone_val = self.inputs["phone"].text().strip() or None

        if not first or not last or not cls:
            self.status_lbl.setText("First, Last Name and Class are mandatory.")
            self.status_lbl.setStyleSheet("color: #e74c3c;")
            self.inputs["first_name"].setFocus()
            return

        if dob_val:
            try:
                datetime.datetime.strptime(dob_val, "%Y-%m-%d")
            except ValueError:
                self.status_lbl.setText("Invalid date format. Use YYYY-MM-DD.")
                self.status_lbl.setStyleSheet("color: #e74c3c;")
                self.inputs["dob"].setFocus()
                return

        payload = {
            "first_name": first,
            "last_name": last,
            "class_section": cls,
            "dob": dob_val,
            "gender": gender_val,
            "email": email_val,
            "phone": phone_val,
        }

        try:
            if self.is_edit:
                sid = self.student_data["student_id"]
                if student_service.update_student(sid, payload):
                    self.status_lbl.setText("Student profile updated successfully!")
                    self.status_lbl.setStyleSheet("color: #2ecc71;")
                    QTimer.singleShot(1000, self.accept)
                else:
                    self.status_lbl.setText("Failed to update database record.")
                    self.status_lbl.setStyleSheet("color: #e74c3c;")
            else:
                if student_service.add_student(payload):
                    self.status_lbl.setText("Student registered successfully!")
                    self.status_lbl.setStyleSheet("color: #2ecc71;")
                    QTimer.singleShot(1000, self.accept)
                else:
                    self.status_lbl.setText("Failed to insert database record.")
                    self.status_lbl.setStyleSheet("color: #e74c3c;")
        except Exception as e:
            self.status_lbl.setText(f"Error: {e}")
            self.status_lbl.setStyleSheet("color: #e74c3c;")


class StudentsFrame(QWidget):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

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
        
        title = QLabel("STUDENT DIRECTORY", header_frame)
        title.setFont(QFont("Outfit", 20, QFont.Bold))
        title.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
        h_layout.addWidget(title)
        
        layout.addWidget(header_frame)

        # Controls & Search Panel
        search_frame = QFrame(self)
        search_frame.setObjectName("CardFrame")
        sf_layout = QHBoxLayout(search_frame)
        sf_layout.setContentsMargins(20, 10, 20, 10)
        
        add_btn = QPushButton("+ REGISTER NEW STUDENT", search_frame)
        add_btn.setObjectName("PrimaryButton")
        add_btn.setFont(QFont("Outfit", 12, QFont.Bold))
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.open_add_student_dialog)
        sf_layout.addWidget(add_btn)
        
        sf_layout.addStretch(1)
        
        search_lbl = QLabel("Search:", search_frame)
        search_lbl.setFont(QFont("Outfit", 13, QFont.Bold))
        search_lbl.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        sf_layout.addWidget(search_lbl)

        self.search_entry = QLineEdit(search_frame)
        self.search_entry.setPlaceholderText("Enter Name, Class or ID...")
        self.search_entry.setFixedWidth(220)
        self.search_entry.returnPressed.connect(self.perform_search)
        sf_layout.addWidget(self.search_entry)

        search_action_btn = QPushButton("Search", search_frame)
        search_action_btn.setFont(QFont("Outfit", 12, QFont.Bold))
        search_action_btn.setCursor(Qt.PointingHandCursor)
        search_action_btn.clicked.connect(self.perform_search)
        sf_layout.addWidget(search_action_btn)

        clear_action_btn = QPushButton("Clear", search_frame)
        clear_action_btn.setCursor(Qt.PointingHandCursor)
        clear_action_btn.clicked.connect(self.clear_search)
        sf_layout.addWidget(clear_action_btn)

        layout.addWidget(search_frame)

        # Scroll Roster Area
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

        # Status Message Box
        self.status_msg = QLabel("", self)
        self.status_msg.setFont(QFont("Outfit", 13))
        self.status_msg.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_msg)

        # Initial Load
        self.load_students()

    def load_students(self, query: str | None = None):
        # Clear existing roster entries
        while self.roster_layout.count() > 0:
            item = self.roster_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if query:
            students = student_service.search_students(query)
        else:
            students = student_service.get_all_students()

        if not students:
            no_lbl = QLabel("No student records found.", self.roster_content)
            no_lbl.setStyleSheet("color: #95a5a6; font-size: 14px;")
            no_lbl.setAlignment(Qt.AlignCenter)
            self.roster_layout.addWidget(no_lbl)
            return

        # Headers widget
        headers_widget = QWidget(self.roster_content)
        headers_layout = QHBoxLayout(headers_widget)
        headers_layout.setContentsMargins(15, 5, 15, 5)
        
        lbls = [("ID", 50), ("Student Name", 3), ("Class/Section", 2), ("Email Address", 3), ("Phone Number", 2), ("Manage Actions", 3)]
        for text, stretch in lbls:
            lbl = QLabel(text, headers_widget)
            lbl.setFont(QFont("Outfit", 12, QFont.Bold))
            lbl.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
            if text == "ID":
                lbl.setFixedWidth(stretch)
                headers_layout.addWidget(lbl)
            elif text == "Manage Actions":
                lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                headers_layout.addWidget(lbl, stretch)
            else:
                headers_layout.addWidget(lbl, stretch)
        self.roster_layout.addWidget(headers_widget)

        # Populate student rows
        for s in students:
            row = StudentRowWidget(
                self.roster_content, s,
                self.open_edit_student_dialog,
                self.confirm_delete_student,
                self.open_student_profile
            )
            self.roster_layout.addWidget(row)

    def open_student_profile(self, student_id: int):
        """Open the complete 360° intelligence profile modal for this student."""
        dialog = StudentProfileDialog(self, student_id)
        dialog.exec()

    def perform_search(self):
        q = self.search_entry.text().strip()
        if not q:
            self.load_students()
            return
        self.load_students(q)
        self.show_status(f"Search results loaded for '{q}'.")

    def clear_search(self):
        self.search_entry.clear()
        self.load_students()
        self.show_status("Cleared search query.")

    def show_status(self, text: str, is_error: bool = False):
        color = "#e74c3c" if is_error else "#2ecc71"
        self.status_msg.setText(text)
        self.status_msg.setStyleSheet(f"color: {color};")
        QTimer.singleShot(4000, lambda: self.status_msg.clear())

    def confirm_delete_student(self, student_id: int):
        reply = QMessageBox.question(
            self, "Delete Student Confirmation",
            f"Are you sure you want to permanently delete Student ID {student_id}?\n\nThis will remove all associated logs and audits.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                if student_service.delete_student(student_id):
                    self.show_status(f"Successfully deleted student ID {student_id}.")
                    self.load_students()
                else:
                    self.show_status("Failed to delete student.", is_error=True)
            except Exception as e:
                self.show_status(f"Database error: {e}", is_error=True)

    def open_add_student_dialog(self):
        dialog = StudentFormDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_students()

    def open_edit_student_dialog(self, student: dict):
        dialog = StudentFormDialog(self, student)
        if dialog.exec() == QDialog.Accepted:
            self.load_students()

