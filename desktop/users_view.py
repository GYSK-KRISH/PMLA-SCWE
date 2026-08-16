"""PySide6 panel for administrative user accounts CRUD management."""

from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QGridLayout, QScrollArea, QDialog, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from core import user_service
from core.database import get_db_status


class UserRowWidget(QFrame):
    def __init__(self, parent, user, edit_cmd, delete_cmd):
        super().__init__(parent)
        self.setObjectName("InnerCardFrame")
        self.setFixedHeight(45)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        
        uid = user["user_id"]
        username = user["username"]
        fullname = user["full_name"]
        role = user["role"]
        status = user["status"]
        
        name_lbl = QLabel(f"{fullname} (@{username})", self)
        name_lbl.setStyleSheet("font-weight: bold; color: #F5F7FA; background: transparent; border: none;")
        layout.addWidget(name_lbl, 2)
        
        role_lbl = QLabel(role, self)
        role_lbl.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        layout.addWidget(role_lbl, 1)
        
        status_color = "#30C48D" if status == "Active" else "#E5484D"
        status_lbl = QLabel(f"● {status}", self)
        status_lbl.setStyleSheet(f"color: {status_color}; font-weight: bold; background: transparent; border: none;")
        layout.addWidget(status_lbl, 1)
        
        # Actions Sub-widget
        actions_widget = QWidget(self)
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(5)
        
        edit_btn = QPushButton("Edit", actions_widget)
        edit_btn.setFixedSize(50, 26)
        edit_btn.clicked.connect(lambda: edit_cmd(user))
        actions_layout.addWidget(edit_btn)
        
        if username != "admin":
            delete_btn = QPushButton("Delete", actions_widget)
            delete_btn.setStyleSheet("color: #E5484D; border: 1px solid rgba(229, 72, 77, 0.25); background-color: rgba(229, 72, 77, 0.08);")
            delete_btn.setFixedSize(55, 26)
            delete_btn.clicked.connect(lambda: delete_cmd(uid))
            actions_layout.addWidget(delete_btn)
            
        layout.addWidget(actions_widget, 1)


class UserFormDialog(QDialog):
    def __init__(self, parent, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.is_edit = user_data is not None
        self.setWindowTitle("Edit User Settings" if self.is_edit else "Register System User")
        self.setFixedSize(450, 420)
        self.setStyleSheet(parent.styleSheet())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        
        title_lbl = QLabel(self.windowTitle().upper(), self)
        title_lbl.setFont(QFont("Outfit", 16, QFont.Bold))
        title_lbl.setStyleSheet("color: #F5F7FA;")
        title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_lbl)
        
        form = QWidget(self)
        form_layout = QGridLayout(form)
        form_layout.setContentsMargins(0, 10, 0, 10)
        
        # Fields mapping
        self.inputs = {}
        
        # 1. Username
        form_layout.addWidget(QLabel("Username (unique):", form), 0, 0)
        self.inputs["username"] = QLineEdit(form)
        form_layout.addWidget(self.inputs["username"], 0, 1)
        if self.is_edit:
            self.inputs["username"].setEnabled(False) # Cannot rename username
            
        # 2. Full Name
        form_layout.addWidget(QLabel("Full Name:", form), 1, 0)
        self.inputs["full_name"] = QLineEdit(form)
        form_layout.addWidget(self.inputs["full_name"], 1, 1)
        
        # 3. Privilege Role
        form_layout.addWidget(QLabel("Privilege Role:", form), 2, 0)
        self.role_combo = QComboBox(form)
        self.role_combo.addItems(["Admin", "Teacher", "Viewer"])
        form_layout.addWidget(self.role_combo, 2, 1)
        
        # 4. Account Status
        form_layout.addWidget(QLabel("Account Status:", form), 3, 0)
        self.status_combo = QComboBox(form)
        self.status_combo.addItems(["Active", "Inactive"])
        form_layout.addWidget(self.status_combo, 3, 1)
        
        # 5. Password
        if not self.is_edit:
            form_layout.addWidget(QLabel("Initial Password:", form), 4, 0)
            self.inputs["password"] = QLineEdit(form)
            self.inputs["password"].setEchoMode(QLineEdit.Password)
            form_layout.addWidget(self.inputs["password"], 4, 1)
            
        layout.addWidget(form)
        
        # Status feedback label
        self.status_lbl = QLabel("", self)
        self.status_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_lbl)
        
        # Buttons
        btn_box = QHBoxLayout()
        save_btn = QPushButton("SAVE USER", self)
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self.save)
        btn_box.addWidget(save_btn)
        
        cancel_btn = QPushButton("CANCEL", self)
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)
        
        layout.addLayout(btn_box)
        
        if self.is_edit:
            self.load_user_data()

    def load_user_data(self):
        ud = self.user_data
        self.inputs["username"].setText(ud["username"])
        self.inputs["full_name"].setText(ud["full_name"])
        self.role_combo.setCurrentText(ud.get("role", "Teacher"))
        self.status_combo.setCurrentText(ud.get("status", "Active"))

    def save(self):
        uname = self.inputs["username"].text().strip().lower()
        fname = self.inputs["full_name"].text().strip()
        role_val = self.role_combo.currentText()
        stat_val = self.status_combo.currentText()

        if not fname:
            self.status_lbl.setText("Full Name is mandatory.")
            self.status_lbl.setStyleSheet("color: #e74c3c;")
            self.inputs["full_name"].setFocus()
            return

        try:
            if self.is_edit:
                if user_service.update_user(self.user_data["user_id"], self.user_data["username"], fname, role_val, stat_val):
                    self.status_lbl.setText("User settings updated successfully!")
                    self.status_lbl.setStyleSheet("color: #2ecc71;")
                    QTimer.singleShot(1000, self.accept)
                else:
                    self.status_lbl.setText("Failed to save changes.")
                    self.status_lbl.setStyleSheet("color: #e74c3c;")
            else:
                passwd = self.inputs["password"].text()
                if not uname or not passwd:
                    self.status_lbl.setText("Username and Password are mandatory.")
                    self.status_lbl.setStyleSheet("color: #e74c3c;")
                    return
                if user_service.create_user(uname, fname, passwd, role_val, stat_val):
                    self.status_lbl.setText("User registered successfully!")
                    self.status_lbl.setStyleSheet("color: #2ecc71;")
                    QTimer.singleShot(1000, self.accept)
                else:
                    self.status_lbl.setText("Username already exists or database error.")
                    self.status_lbl.setStyleSheet("color: #e74c3c;")
        except Exception as e:
            self.status_lbl.setText(f"Error: {e}")
            self.status_lbl.setStyleSheet("color: #e74c3c;")


class UsersFrame(QWidget):
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
        
        title = QLabel("USER ACCOUNTS MANAGEMENT", header_frame)
        title.setFont(QFont("Outfit", 18, QFont.Bold))
        title.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
        h_layout.addWidget(title)
        
        layout.addWidget(header_frame)

        # Controls panel
        search_frame = QFrame(self)
        search_frame.setObjectName("CardFrame")
        sf_layout = QHBoxLayout(search_frame)
        sf_layout.setContentsMargins(20, 10, 20, 10)
        
        add_btn = QPushButton("+ ADD SYSTEM USER", search_frame)
        add_btn.setObjectName("PrimaryButton")
        add_btn.setFont(QFont("Outfit", 12, QFont.Bold))
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.open_add_user_dialog)
        sf_layout.addWidget(add_btn)
        
        sf_layout.addStretch(1)
        layout.addWidget(search_frame)

        # Table Display ScrollFrame
        self.table_scroll = QScrollArea(self)
        self.table_scroll.setObjectName("CardFrame")
        self.table_scroll.setWidgetResizable(True)
        self.table_content = QWidget()
        self.table_layout = QVBoxLayout(self.table_content)
        self.table_layout.setContentsMargins(15, 15, 15, 15)
        self.table_layout.setSpacing(6)
        self.table_layout.setAlignment(Qt.AlignTop)
        self.table_scroll.setWidget(self.table_content)
        layout.addWidget(self.table_scroll, 1)

        # Status Bar
        self.status_msg = QLabel("", self)
        self.status_msg.setFont(QFont("Outfit", 12))
        self.status_msg.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_msg)

        # Load initial user list
        self.load_users()

    def load_users(self):
        # Clear existing roster entries
        while self.table_layout.count() > 0:
            item = self.table_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        users = user_service.list_users()

        # Headers
        headers_widget = QWidget(self.table_content)
        headers_layout = QHBoxLayout(headers_widget)
        headers_layout.setContentsMargins(15, 5, 15, 5)
        
        lbl_acc = QLabel("User Account", headers_widget)
        lbl_acc.setFont(QFont("Outfit", 12, QFont.Bold))
        lbl_acc.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        headers_layout.addWidget(lbl_acc, 2)
        
        lbl_role = QLabel("Role", headers_widget)
        lbl_role.setFont(QFont("Outfit", 12, QFont.Bold))
        lbl_role.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        headers_layout.addWidget(lbl_role, 1)
        
        lbl_status = QLabel("Status", headers_widget)
        lbl_status.setFont(QFont("Outfit", 12, QFont.Bold))
        lbl_status.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        headers_layout.addWidget(lbl_status, 1)
        
        lbl_actions = QLabel("Actions", headers_widget)
        lbl_actions.setFont(QFont("Outfit", 12, QFont.Bold))
        lbl_actions.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        lbl_actions.setAlignment(Qt.AlignRight)
        headers_layout.addWidget(lbl_actions, 1)
        
        self.table_layout.addWidget(headers_widget)

        if not users:
            no_users = QLabel("No users registered in system.", self.table_content)
            no_users.setStyleSheet("color: #8D96A8;")
            no_users.setAlignment(Qt.AlignCenter)
            self.table_layout.addWidget(no_users)
            return

        for u in users:
            row = UserRowWidget(self.table_content, u, self.open_edit_user_dialog, self.confirm_delete_user)
            self.table_layout.addWidget(row)

    def show_status(self, text: str, is_error: bool = False):
        color = "#e74c3c" if is_error else "#2ecc71"
        self.status_msg.setText(text)
        self.status_msg.setStyleSheet(f"color: {color};")
        QTimer.singleShot(4000, lambda: self.status_msg.clear())

    def confirm_delete_user(self, user_id: int):
        reply = QMessageBox.question(
            self, "Delete Account",
            f"Are you sure you want to permanently delete User ID {user_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if user_service.delete_user(user_id):
                self.show_status("User account deleted.")
                self.load_users()
            else:
                self.show_status("Action failed.", is_error=True)

    def open_add_user_dialog(self):
        dialog = UserFormDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_users()

    def open_edit_user_dialog(self, user: dict):
        dialog = UserFormDialog(self, user)
        if dialog.exec() == QDialog.Accepted:
            self.load_users()
