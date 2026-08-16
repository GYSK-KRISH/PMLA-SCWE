"""PySide6 application controller managing panels and authentication states."""

from __future__ import annotations
import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget, QDialog,
    QMessageBox, QLineEdit, QScrollArea, QMenu
)
from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QFont, QIcon, QAction

# Import Views (These will be migrated to PySide6 in subsequent phases)
from .login import LoginFrame
from .dashboard import DashboardFrame
from .students import StudentsFrame
from .attendance import AttendanceFrame
from .assessments import AssessmentsFrame
from .wellness import WellnessFrame
from .analytics_view import AnalyticsViewFrame
from .reports_view import ReportsFrame
from .ai_assistant_view import AIAssistantFrame
from .users_view import UsersFrame
from .interventions_view import InterventionsFrame


# Premium Dark CSS Stylesheet
from .theme import GLOBAL_STYLESHEET, NAV_ITEMS

class NotificationsDialog(QDialog):
    """Upgraded Version 1.6 Decision-Support Notification Center for PySide6."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Smart Decision-Support Notification Center")
        self.setMinimumSize(560, 520)
        self.setStyleSheet(GLOBAL_STYLESHEET)
        self.filter_priority = "All"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        # Header
        top_h = QHBoxLayout()
        title_lbl = QLabel("🔔 SMART NOTIFICATION & DECISION CENTER", self)
        title_lbl.setFont(QFont("Outfit", 13, QFont.Bold))
        title_lbl.setStyleSheet("color: #FFFFFF;")
        top_h.addWidget(title_lbl)
        top_h.addStretch(1)

        btn_mark_all = QPushButton("Mark All Read", self)
        btn_mark_all.setStyleSheet("background: #151925; color: #F5F7FA; border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; padding: 4px 10px; font-size: 11px;")
        btn_mark_all.clicked.connect(self.mark_all_read_action)
        top_h.addWidget(btn_mark_all)
        layout.addLayout(top_h)

        # Filter Bar
        f_bar = QHBoxLayout()
        f_bar.addWidget(QLabel("Filter Priority:"))
        self.prio_combo = QComboBox(self)
        self.prio_combo.addItems(["All", "HIGH", "MEDIUM", "SUCCESS", "INFO"])
        self.prio_combo.currentTextChanged.connect(self.on_filter_changed)
        f_bar.addWidget(self.prio_combo)
        f_bar.addStretch(1)
        layout.addLayout(f_bar)

        # Scrollable Notifications Feed
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(4, 4, 4, 4)
        self.scroll_layout.setSpacing(8)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

        self.refresh_list()

        close_btn = QPushButton("CLOSE NOTIFICATION CENTER", self)
        close_btn.setObjectName("PrimaryButton")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def on_filter_changed(self, text: str):
        self.filter_priority = text
        self.refresh_list()

    def mark_all_read_action(self):
        from core.notification_service import mark_all_notifications_as_read
        mark_all_notifications_as_read()
        if hasattr(self.parent(), "refresh_top_bar_counts"):
            self.parent().refresh_top_bar_counts()
        self.refresh_list()

    def refresh_list(self):
        while self.scroll_layout.count() > 0:
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            from core.notification_service import get_notifications, mark_notification_as_read, update_notification_action_status, scan_and_generate_smart_alerts
            scan_and_generate_smart_alerts()
            notifs = get_notifications(priority=self.filter_priority if self.filter_priority != "All" else None)
        except Exception:
            notifs = []

        if not notifs:
            lbl = QLabel("No active notifications in this category.", self.scroll_content)
            lbl.setStyleSheet("color: #8D96A8; padding: 20px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(lbl)
            return

        for n in notifs:
            prio = n.get("priority", "INFO")
            prio_col = "#EF4444" if prio == "HIGH" else ("#F59E0B" if prio == "MEDIUM" else ("#10B981" if prio == "SUCCESS" else "#3B82F6"))
            is_unread = (n.get("is_read") == 0)

            card = QFrame(self.scroll_content)
            card.setObjectName("InnerCardFrame")
            card.setStyleSheet(
                f"background-color: {'#151925' if is_unread else '#0F121C'}; "
                f"border-left: 3px solid {prio_col}; border-radius: 6px; padding: 10px;"
            )
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(10, 8, 10, 8)
            c_layout.setSpacing(6)

            # Top row: priority badge + time
            top_r = QHBoxLayout()
            p_badge = QLabel(f"● {prio} PRIORITY" if prio != "SUCCESS" else "🌟 MILESTONE ACHIEVED")
            p_badge.setFont(QFont("Outfit", 9, QFont.Bold))
            p_badge.setStyleSheet(f"color: {prio_col};")
            top_r.addWidget(p_badge)

            if n.get("action_status"):
                st_lbl = QLabel(f"[{n['action_status']}]")
                st_lbl.setFont(QFont("Outfit", 9))
                st_lbl.setStyleSheet("color: #8D96A8;")
                top_r.addWidget(st_lbl)

            top_r.addStretch(1)

            t_str = str(n.get("created_at") or "")[:16]
            time_lbl = QLabel(t_str)
            time_lbl.setFont(QFont("Outfit", 9))
            time_lbl.setStyleSheet("color: #8D96A8;")
            top_r.addWidget(time_lbl)
            c_layout.addLayout(top_r)

            # Title & Message
            t_lbl = QLabel(n.get("title", ""))
            t_lbl.setFont(QFont("Outfit", 11, QFont.Bold))
            t_lbl.setStyleSheet("color: #F5F7FA;")
            c_layout.addWidget(t_lbl)

            m_lbl = QLabel(n.get("message", ""))
            m_lbl.setFont(QFont("Outfit", 10))
            m_lbl.setStyleSheet("color: #CBD5E1;")
            m_lbl.setWordWrap(True)
            c_layout.addWidget(m_lbl)

            # Action Buttons Row
            act_r = QHBoxLayout()
            sid = n.get("student_id")
            if sid:
                btn_prof = QPushButton("👤 Student 360°", card)
                btn_prof.setStyleSheet("background: #1B2030; color: #4D8DFF; font-size: 10px; padding: 3px 8px; border-radius: 4px;")
                def make_open_profile(s_id=sid):
                    def handler():
                        from desktop.student_profile_dialog import StudentProfileDialog
                        dlg = StudentProfileDialog(self.parent(), s_id)
                        dlg.exec()
                    return handler
                btn_prof.clicked.connect(make_open_profile())
                act_r.addWidget(btn_prof)

                btn_iv = QPushButton("🛠️ Intervene", card)
                btn_iv.setStyleSheet("background: #1B2030; color: #30C48D; font-size: 10px; padding: 3px 8px; border-radius: 4px;")
                def make_open_iv():
                    def handler():
                        self.accept()
                        if hasattr(self.parent(), "switch_to_frame"):
                            self.parent().switch_to_frame("interventions")
                    return handler
                btn_iv.clicked.connect(make_open_iv())
                act_r.addWidget(btn_iv)

            act_r.addStretch(1)

            if is_unread:
                btn_read = QPushButton("✓ Mark Read", card)
                btn_read.setStyleSheet("background: #151925; color: #8D96A8; font-size: 10px; padding: 3px 8px; border: 1px solid rgba(255,255,255,0.1); border-radius: 4px;")
                def make_mark_read(nid=n["notification_id"]):
                    def handler():
                        mark_notification_as_read(nid)
                        if hasattr(self.parent(), "refresh_top_bar_counts"):
                            self.parent().refresh_top_bar_counts()
                        self.refresh_list()
                    return handler
                btn_read.clicked.connect(make_mark_read())
                act_r.addWidget(btn_read)

            c_layout.addLayout(act_r)
            self.scroll_layout.addWidget(card)


class MyProfileDialog(QDialog):

    def __init__(self, parent, user):
        super().__init__(parent)
        self.setWindowTitle("My Profile Details")
        self.setFixedSize(380, 220)
        self.setStyleSheet(GLOBAL_STYLESHEET)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("👤 MY ACCOUNT PROFILE", self)
        title.setFont(QFont("Outfit", 14, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        info_widget = QWidget(self)
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 10, 0, 10)
        
        username_lbl = QLabel(f"Username:  @{user['username']}", info_widget)
        username_lbl.setFont(QFont("Outfit", 12))
        info_layout.addWidget(username_lbl)
        
        fullname_lbl = QLabel(f"Full Name:  {user['full_name']}", info_widget)
        fullname_lbl.setFont(QFont("Outfit", 12))
        info_layout.addWidget(fullname_lbl)
        
        role_lbl = QLabel(f"Access Role:  {user['role']}", info_widget)
        role_lbl.setFont(QFont("Outfit", 12))
        info_layout.addWidget(role_lbl)
        
        status_lbl = QLabel(f"Status:  ● {user['status']}", info_widget)
        status_lbl.setFont(QFont("Outfit", 12, QFont.Bold))
        status_lbl.setStyleSheet("color: #34A853;")
        info_layout.addWidget(status_lbl)
        
        layout.addWidget(info_widget)
        
        close_btn = QPushButton("CLOSE", self)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class ChangePasswordDialog(QDialog):
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Change Password")
        self.setFixedSize(400, 320)
        self.setStyleSheet(GLOBAL_STYLESHEET)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        
        title = QLabel("🔒 UPDATE ACCOUNT PASSWORD", self)
        title.setFont(QFont("Outfit", 14, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        form = QWidget(self)
        form_layout = QGridLayout(form)
        form_layout.setContentsMargins(0, 10, 0, 10)
        
        old_lbl = QLabel("Current Password:", form)
        old_lbl.setFont(QFont("Outfit", 11, QFont.Bold))
        old_lbl.setStyleSheet("color: #AAAAAA;")
        form_layout.addWidget(old_lbl, 0, 0)
        
        self.old_entry = QLineEdit(form)
        self.old_entry.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.old_entry, 0, 1)
        
        new_lbl = QLabel("New Password:", form)
        new_lbl.setFont(QFont("Outfit", 11, QFont.Bold))
        new_lbl.setStyleSheet("color: #AAAAAA;")
        form_layout.addWidget(new_lbl, 1, 0)
        
        self.new_entry = QLineEdit(form)
        self.new_entry.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.new_entry, 1, 1)
        
        confirm_lbl = QLabel("Confirm Password:", form)
        confirm_lbl.setFont(QFont("Outfit", 11, QFont.Bold))
        confirm_lbl.setStyleSheet("color: #AAAAAA;")
        form_layout.addWidget(confirm_lbl, 2, 0)
        
        self.confirm_entry = QLineEdit(form)
        self.confirm_entry.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.confirm_entry, 2, 1)
        
        layout.addWidget(form)
        
        self.status_lbl = QLabel("", self)
        self.status_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_lbl)
        
        btn_box = QHBoxLayout()
        update_btn = QPushButton("UPDATE PASSWORD", self)
        update_btn.setObjectName("PrimaryButton")
        update_btn.clicked.connect(self.proceed)
        btn_box.addWidget(update_btn)
        
        cancel_btn = QPushButton("CANCEL", self)
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)
        
        layout.addLayout(btn_box)

    def proceed(self):
        old_val = self.old_entry.text()
        new_val = self.new_entry.text()
        conf_val = self.confirm_entry.text()

        if not old_val or not new_val:
            self.status_lbl.setText("Fields cannot remain empty.")
            self.status_lbl.setStyleSheet("color: #e74c3c;")
            return
        if new_val != conf_val:
            self.status_lbl.setText("Passwords do not match.")
            self.status_lbl.setStyleSheet("color: #e74c3c;")
            return
        
        from core.user_service import change_user_password
        if change_user_password(self.user_id, old_val, new_val):
            self.status_lbl.setText("Password updated successfully!")
            self.status_lbl.setStyleSheet("color: #2ecc71;")
            self.old_entry.setEnabled(False)
            self.new_entry.setEnabled(False)
            self.confirm_entry.setEnabled(False)
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1500, self.accept)
        else:
            self.status_lbl.setText("Incorrect current password.")
            self.status_lbl.setStyleSheet("color: #e74c3c;")


class WorkspaceWidget(QWidget):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 1. Sidebar Frame
        self.sidebar = QFrame(self)
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 25, 15, 20)
        sidebar_layout.setAlignment(Qt.AlignTop)
        
        brand_lbl = QLabel("PMLA-SCWE", self.sidebar)
        brand_lbl.setFont(QFont("Outfit", 20, QFont.Bold))
        brand_lbl.setStyleSheet(
            "color: #F5F7FA; border: none;"
            "font-weight: 800; letter-spacing: 0.5px;"
        )
        sidebar_layout.addWidget(brand_lbl)

        v_lbl = QLabel("v1.1 — Premium Edition", self.sidebar)
        v_lbl.setFont(QFont("Outfit", 10))
        v_lbl.setStyleSheet("color: #4A5260; border: none;")
        sidebar_layout.addWidget(v_lbl)
        sidebar_layout.addSpacing(25)

        # Thin separator
        sep = QFrame(self.sidebar)
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: rgba(255,255,255,0.05); border: none;")
        sidebar_layout.addWidget(sep)
        sidebar_layout.addSpacing(15)
        
        self.nav_buttons = {}

        for title, name in NAV_ITEMS:
            btn = QPushButton(title, self.sidebar)
            btn.setObjectName("NavButton")
            btn.setCursor(Qt.PointingHandCursor)

            def make_switch(n=name):
                return lambda: self.controller.switch_to_frame(n)

            btn.clicked.connect(make_switch())
            sidebar_layout.addWidget(btn)
            self.nav_buttons[name] = btn
            
        sidebar_layout.addStretch(1)
        
        logout_btn = QPushButton("LOGOUT USER", self.sidebar)
        logout_btn.setObjectName("NavButton")
        logout_btn.setStyleSheet("color: #FF4D4D; border: 1px solid #3A1A1A; background-color: #181818; text-align: center;")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.controller.perform_logout)
        sidebar_layout.addWidget(logout_btn)

        layout.addWidget(self.sidebar)

        # 2. Right Pane: Header + Content Stack
        self.right_pane = QWidget(self)
        right_layout = QVBoxLayout(self.right_pane)
        right_layout.setContentsMargins(20, 0, 20, 20)
        right_layout.setSpacing(0)

        # Top Bar Frame
        self.top_bar = QFrame(self.right_pane)
        self.top_bar.setObjectName("TopBar")
        self.top_bar.setFixedHeight(56)
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)

        brand_text = QLabel("Student Analytics Command Center", self.top_bar)
        brand_text.setFont(QFont("Outfit", 13, QFont.Bold))
        brand_text.setStyleSheet("color: #4A5260; background: transparent;")
        top_layout.addWidget(brand_text)

        top_layout.addStretch(1)

        # Notification Bell
        self.bell_btn = QPushButton("🔔  0", self.top_bar)
        self.bell_btn.setFont(QFont("Outfit", 11, QFont.Bold))
        self.bell_btn.setStyleSheet(
            "QPushButton { background-color: #151925; border: 1px solid rgba(255,255,255,0.08);"
            " color: #8D96A8; border-radius: 6px; padding: 6px 12px; }"
            "QPushButton:hover { background-color: #1B2030; color: #F5F7FA; }"
        )
        self.bell_btn.clicked.connect(self.controller.show_notifications_dialog)
        top_layout.addWidget(self.bell_btn)

        # Profile button
        self.profile_btn = QPushButton("👤  Admin  ▾", self.top_bar)
        self.profile_btn.setFont(QFont("Outfit", 11, QFont.Bold))
        self.profile_btn.setStyleSheet(
            "QPushButton { background-color: #151925; border: 1px solid rgba(255,255,255,0.08);"
            " color: #F5F7FA; border-radius: 6px; padding: 6px 14px; }"
            "QPushButton:hover { background-color: #1B2030; }"
        )
        self.profile_btn.clicked.connect(self.controller.show_profile_menu)
        top_layout.addWidget(self.profile_btn)

        right_layout.addWidget(self.top_bar)
        
        # Inner Content Stack
        self.content_stack = QStackedWidget(self.right_pane)
        right_layout.addWidget(self.content_stack)
        
        layout.addWidget(self.right_pane)


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PMLA-SCWE - Student Analytics & Cyber-Wellbeing Engine")
        self.resize(1100, 680)
        self.setMinimumSize(1000, 600)
        self.setStyleSheet(GLOBAL_STYLESHEET)
        
        self.current_user = None
        self.target_student_id = None
        
        # Central Stacked Widget
        self.central_stack = QStackedWidget(self)
        self.setCentralWidget(self.central_stack)
        
        # Page Views mappings
        self.views = {}
        
        # Setup Login View
        self.login_view = LoginFrame(self.central_stack, controller=self, on_login_success=self.on_login_success)
        self.central_stack.addWidget(self.login_view)
        
        # Setup Workspace View
        self.workspace = WorkspaceWidget(self.central_stack, self)
        self.central_stack.addWidget(self.workspace)
        
        self.show_login_screen()

    def show_login_screen(self):
        self.current_user = None
        self.central_stack.setCurrentIndex(0)

    def on_login_success(self):
        self.workspace.content_stack.setEnabled(True)
        
        # Initialize views dynamic binding inside Workspace stacked widget
        self.setup_pages()
        
        self.refresh_top_bar_counts()
        self.central_stack.setCurrentIndex(1)
        self.switch_to_frame("dashboard")

    def setup_pages(self):
        # Clear existing items if any
        while self.workspace.content_stack.count() > 0:
            w = self.workspace.content_stack.widget(0)
            self.workspace.content_stack.removeWidget(w)
            w.deleteLater()
            
        self.views.clear()
        
        pages_config = [
            ("dashboard", DashboardFrame),
            ("students", StudentsFrame),
            ("attendance", AttendanceFrame),
            ("assessments", AssessmentsFrame),
            ("wellness", WellnessFrame),
            ("analytics", AnalyticsViewFrame),
            ("reports", ReportsFrame),
            ("interventions", InterventionsFrame),
            ("ai_assistant", AIAssistantFrame),
            ("users", UsersFrame),
        ]

        
        for name, view_class in pages_config:
            view_instance = view_class(self.workspace.content_stack, self)
            self.workspace.content_stack.addWidget(view_instance)
            self.views[name] = view_instance

    def refresh_top_bar_counts(self):
        if not self.current_user:
            return

        try:
            from core.notification_service import get_unread_notification_count
            unread = get_unread_notification_count()
            if unread > 0:
                self.workspace.bell_btn.setText(f"🔔  {unread}")
                self.workspace.bell_btn.setStyleSheet(
                    "QPushButton { background-color: rgba(229,72,77,0.15);"
                    " border: 1px solid rgba(229,72,77,0.35);"
                    " color: #E5484D; border-radius: 6px; padding: 6px 12px; }"
                    "QPushButton:hover { background-color: rgba(229,72,77,0.25); }"
                )
            else:
                self.workspace.bell_btn.setText("🔔  0")
                self.workspace.bell_btn.setStyleSheet(
                    "QPushButton { background-color: #151925;"
                    " border: 1px solid rgba(255,255,255,0.08);"
                    " color: #8D96A8; border-radius: 6px; padding: 6px 12px; }"
                    "QPushButton:hover { background-color: #1B2030; color: #F5F7FA; }"
                )
        except Exception:
            pass

        fname = self.current_user.get("full_name", "Admin")
        role = self.current_user.get("role", "Teacher")
        display = fname.split()[0] if fname else "Admin"
        self.workspace.profile_btn.setText(f"👤  {display}  ▾")


    def show_notifications_dialog(self):
        dialog = NotificationsDialog(self)
        dialog.exec()

    def show_profile_menu(self):
        menu = QMenu(self)
        
        action_profile = QAction("👤 My Profile", menu)
        action_profile.triggered.connect(self.open_my_profile_dialog)
        menu.addAction(action_profile)
        
        action_pwd = QAction("🔒 Change Password", menu)
        action_pwd.triggered.connect(self.open_change_password_dialog)
        menu.addAction(action_pwd)
        
        if self.current_user["role"] == "Admin":
            action_users = QAction("👥 User Management", menu)
            action_users.triggered.connect(lambda: self.switch_to_frame("users"))
            menu.addAction(action_users)
            
        action_db = QAction("🗄 Database Status", menu)
        action_db.triggered.connect(self.show_db_status)
        menu.addAction(action_db)
        
        menu.addSeparator()
        
        action_logout = QAction("🚪 Logout Profile", menu)
        action_logout.triggered.connect(self.perform_logout)
        menu.addAction(action_logout)
        
        # Position menu at bottom of profile button
        button_pos = self.workspace.profile_btn.mapToGlobal(QPoint(0, self.workspace.profile_btn.height()))
        menu.exec(button_pos)

    def open_my_profile_dialog(self):
        dialog = MyProfileDialog(self, self.current_user)
        dialog.exec()

    def open_change_password_dialog(self):
        dialog = ChangePasswordDialog(self, self.current_user["user_id"])
        dialog.exec()

    def show_db_status(self):
        from core.database import get_db_status
        status = get_db_status()
        QMessageBox.information(
            self, "Database Connection",
            f"Backend: {status['backend']}\nDetails: {status['display']}"
        )

    def switch_to_frame(self, name: str):
        if not self.workspace.nav_buttons:
            return
            
        if self.current_user and self.current_user.get("role") == "Viewer":
            if name not in ["dashboard", "reports", "analytics", "ai_assistant"]:
                QMessageBox.warning(
                    self, "Access Denied",
                    "Access Denied: Viewers are only authorized to read dashboard analytics and reports."
                )
                return

        # Update sidebar button active highlighting
        for tab_name, btn in self.workspace.nav_buttons.items():
            if tab_name == name:
                btn.setProperty("active", "true")
            else:
                btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            
        if name in self.views:
            # Refresh details on view before showing it if has load hook
            view_instance = self.views[name]
            if hasattr(view_instance, "refresh_dashboard") and name == "dashboard":
                view_instance.refresh_dashboard()
            elif hasattr(view_instance, "load_students") and name == "students":
                view_instance.load_students()
            elif hasattr(view_instance, "load_class_roster") and name == "attendance":
                view_instance.load_class_roster()
            elif hasattr(view_instance, "update_db_status") and hasattr(view_instance, "load_student_assessment_history") and name == "assessments":
                view_instance.load_student_assessment_history()
            elif hasattr(view_instance, "update_db_status") and hasattr(view_instance, "load_student_wellness_history") and name == "wellness":
                view_instance.load_student_wellness_history()
            elif hasattr(view_instance, "refresh_report_data") and name == "reports":
                view_instance.refresh_report_data()
            elif hasattr(view_instance, "load_users") and name == "users":
                view_instance.load_users()
                
            self.workspace.content_stack.setCurrentWidget(view_instance)
            self.refresh_top_bar_counts()

    def perform_logout(self):
        self.show_login_screen()


def run():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
