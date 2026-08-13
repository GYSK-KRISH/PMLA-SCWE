"""CustomTkinter application controller managing panels and authentication states."""

from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Import Views
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

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# Placeholder Frames for upcoming features in future phases
class PlaceholderFrame(ctk.CTkFrame):
    def __init__(self, parent, title_text):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        inner = ctk.CTkFrame(self, fg_color="#161625", corner_radius=12)
        inner.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        inner.grid_columnconfigure(0, weight=1)
        inner.grid_rowconfigure(0, weight=1)

        content_box = ctk.CTkFrame(inner, fg_color="transparent")
        content_box.grid(row=0, column=0)

        title = ctk.CTkLabel(
            content_box,
            text=title_text.upper(),
            font=ctk.CTkFont(family="Outfit", size=24, weight="bold"),
            text_color="#00d2ff"
        )
        title.pack(pady=10)

        info = ctk.CTkLabel(
            content_box,
            text="This section is currently undergoing migration in Phase 5-9.\nIt will connect seamlessly to core services once built.",
            font=ctk.CTkFont(family="Outfit", size=13),
            text_color="#95a5a6"
        )
        info.pack(pady=10)


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PMLA-SCWE - Student Analytics & Cyber-Wellbeing Engine")
        self.geometry("1100x680")
        self.minsize(1000, 600)

        # Main Layout Grid
        self.grid_columnconfigure(0, weight=0)  # Sidebar (initially hidden)
        self.grid_columnconfigure(1, weight=1)  # Content area
        self.grid_rowconfigure(0, weight=1)

        # Active User Context Session
        self.current_user = None

        # Sidebar navigation container
        self.sidebar = None
        self.top_bar = None

        # Content frame container
        self.content_container = ctk.CTkFrame(self, fg_color="#0F0F0F")
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Login View initially loaded
        self.active_frame = None
        self.show_login_screen()

    def show_login_screen(self):
        # Clear sidebar if it exists
        if self.sidebar:
            self.sidebar.destroy()
            self.sidebar = None
            self.grid_columnconfigure(0, weight=0)

        # Clear top bar if it exists
        if self.top_bar:
            self.top_bar.destroy()
            self.top_bar = None

        # Reset grid weights
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(1, weight=0)

        # Render login frame in center of content area
        if self.active_frame:
            self.active_frame.destroy()

        login_center = ctk.CTkFrame(self.content_container, fg_color="transparent")
        login_center.grid(row=0, column=0)

        self.active_frame = LoginFrame(
            login_center,
            controller=self,
            on_login_success=self.on_login_success
        )
        self.active_frame.pack(padx=20, pady=20)

    def on_login_success(self):
        # Create Top Bar Header first
        self.create_top_bar()

        # Create Sidebar
        self.create_sidebar()
        
        # Switch to Dashboard
        self.switch_to_frame("dashboard")

    def create_top_bar(self):
        # Configure content container row weights
        self.content_container.grid_rowconfigure(0, weight=0)
        self.content_container.grid_rowconfigure(1, weight=1)

        self.top_bar = ctk.CTkFrame(self.content_container, fg_color="#0F0F0F", height=50, corner_radius=0)
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 0))

        # Brand Text
        lbl = ctk.CTkLabel(
            self.top_bar,
            text="Student Analytics Command Center",
            font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            text_color="#AAAAAA"
        )
        lbl.pack(side="left", padx=10)

        # Right buttons panel
        right_panel = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        right_panel.pack(side="right", padx=10)

        # Notification Bell
        self.bell_btn = ctk.CTkButton(
            right_panel,
            text="🔔 0",
            width=55,
            height=30,
            fg_color="#1A1A1A",
            border_color="#2A2A2A",
            border_width=1,
            hover_color="#272727",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=11, weight="bold"),
            command=self.show_notifications_dropdown
        )
        self.bell_btn.pack(side="left", padx=5)

        # Profile Dropdown
        self.profile_btn = ctk.CTkButton(
            right_panel,
            text="👤 Admin ▼",
            width=150,
            height=30,
            fg_color="#1A1A1A",
            border_color="#2A2A2A",
            border_width=1,
            hover_color="#272727",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=11, weight="bold"),
            command=self.show_profile_dropdown
        )
        self.profile_btn.pack(side="left", padx=5)

        self.refresh_top_bar_counts()

    def refresh_top_bar_counts(self):
        if not self.current_user:
            return
        
        # Refresh notifications count
        try:
            from core.notification_service import get_unread_notification_count
            unread = get_unread_notification_count()
            self.bell_btn.configure(text=f"🔔 {unread}")
            if unread > 0:
                self.bell_btn.configure(text_color="#FF4D4D")
            else:
                self.bell_btn.configure(text_color="#FFFFFF")
        except Exception:
            pass

        # Refresh profile text
        fname = self.current_user.get("full_name", "Admin")
        role = self.current_user.get("role", "Teacher")
        self.profile_btn.configure(text=f"👤 {fname} ({role}) ▼")

    def show_notifications_dropdown(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Notifications")
        popup.geometry("380x350")
        popup.configure(fg_color="#181818")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()

        # Center relative to parent window
        x = self.winfo_x() + (self.winfo_width() // 2) - 190
        y = self.winfo_y() + (self.winfo_height() // 2) - 175
        popup.geometry(f"+{x}+{y}")

        title_lbl = ctk.CTkLabel(popup, text="🔔 SYSTEM NOTIFICATIONS", font=ctk.CTkFont(family="Outfit", size=14, weight="bold"), text_color="#FFFFFF")
        title_lbl.pack(pady=12)

        # ScrollFrame for list
        scroll = ctk.CTkScrollableFrame(popup, fg_color="#121212", border_color="#2A2A2A", border_width=1, corner_radius=8, height=220)
        scroll.pack(fill="both", expand=True, padx=15, pady=5)

        try:
            from core.notification_service import get_notifications, mark_notification_as_read, generate_system_alerts
            generate_system_alerts()
            notifs = get_notifications()
        except Exception:
            notifs = []

        if not notifs:
            lbl = ctk.CTkLabel(scroll, text="No system notifications active.", text_color="#717171", font=ctk.CTkFont(family="Outfit", size=12))
            lbl.pack(pady=40)
        else:
            for idx, n in enumerate(notifs):
                color = "#FFFFFF"
                if n["priority"] == "HIGH":
                    color = "#FF4D4D"
                elif n["priority"] == "MEDIUM":
                    color = "#FFD600"
                
                is_unread = n["is_read"] == 0
                weight = "bold" if is_unread else "normal"

                frame = ctk.CTkFrame(scroll, fg_color="#1C1C1C" if is_unread else "#151515", corner_radius=6)
                frame.pack(fill="x", pady=2, padx=2)

                txt_lbl = ctk.CTkLabel(
                    frame,
                    text=f"{n['title']}\n{n['message']}",
                    text_color=color,
                    font=ctk.CTkFont(family="Outfit", size=11, weight=weight),
                    justify="left",
                    wraplength=220
                )
                txt_lbl.pack(anchor="w", padx=10, pady=8)

                if is_unread:
                    def mark_read(nid=n["notification_id"]):
                        mark_notification_as_read(nid)
                        self.refresh_top_bar_counts()
                        popup.destroy()
                        self.show_notifications_dropdown()
                    
                    btn = ctk.CTkButton(
                        frame,
                        text="Mark Read",
                        width=60,
                        height=20,
                        fg_color="#E50914",
                        hover_color="#CC0000",
                        text_color="#FFFFFF",
                        font=ctk.CTkFont(family="Outfit", size=10, weight="bold"),
                        command=mark_read
                    )
                    btn.pack(anchor="e", padx=10, pady=(0, 6))

        # Close button
        btn_close = ctk.CTkButton(popup, text="CLOSE WINDOW", fg_color="#272727", hover_color="#333333", text_color="#FFFFFF", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), command=popup.destroy)
        btn_close.pack(fill="x", side="bottom", padx=15, pady=10)

    def show_profile_dropdown(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Admin Profile Menu")
        popup.geometry("260x340")
        popup.configure(fg_color="#181818")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()

        x = self.winfo_x() + (self.winfo_width() // 2) - 130
        y = self.winfo_y() + (self.winfo_height() // 2) - 170
        popup.geometry(f"+{x}+{y}")

        # Profile avatar
        avatar_lbl = ctk.CTkLabel(popup, text="[ A ]", font=ctk.CTkFont(family="Outfit", size=28, weight="bold"), text_color="#E50914")
        avatar_lbl.pack(pady=(15, 2))

        name_lbl = ctk.CTkLabel(popup, text=self.current_user["full_name"], font=ctk.CTkFont(family="Outfit", size=13, weight="bold"), text_color="#FFFFFF")
        name_lbl.pack()

        role_lbl = ctk.CTkLabel(popup, text=self.current_user["role"], font=ctk.CTkFont(family="Outfit", size=11), text_color="#717171")
        role_lbl.pack(pady=(0, 10))

        def my_profile():
            popup.destroy()
            self.open_my_profile_dialog()

        def change_pwd():
            popup.destroy()
            self.open_change_password_dialog()

        def user_mgmt():
            popup.destroy()
            if self.current_user["role"] != "Admin":
                messagebox.showwarning("Access Denied", "Only administrators can access User Accounts Management.")
                return
            self.switch_to_frame("users")

        def db_status():
            popup.destroy()
            from core.database import get_db_status
            status = get_db_status()
            messagebox.showinfo("Database Connection", f"Backend: {status['backend']}\nDetails: {status['display']}")

        def do_logout():
            popup.destroy()
            self.perform_logout()

        ctk.CTkButton(popup, text="👤 My Profile", fg_color="transparent", text_color="#E5E5E5", hover_color="#212121", anchor="w", command=my_profile).pack(fill="x", padx=15, pady=2)
        ctk.CTkButton(popup, text="🔒 Change Password", fg_color="transparent", text_color="#E5E5E5", hover_color="#212121", anchor="w", command=change_pwd).pack(fill="x", padx=15, pady=2)
        
        if self.current_user["role"] == "Admin":
            ctk.CTkButton(popup, text="👥 User Management", fg_color="transparent", text_color="#E5E5E5", hover_color="#212121", anchor="w", command=user_mgmt).pack(fill="x", padx=15, pady=2)

        ctk.CTkButton(popup, text="🗄 Database Status", fg_color="transparent", text_color="#E5E5E5", hover_color="#212121", anchor="w", command=db_status).pack(fill="x", padx=15, pady=2)
        
        line = ctk.CTkFrame(popup, height=1, fg_color="#2A2A2A")
        line.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(popup, text="🚪 Logout Profile", fg_color="#181818", border_color="#3A1A1A", border_width=1, hover_color="#3A1616", text_color="#FF4D4D", command=do_logout).pack(fill="x", padx=15, pady=(0, 10))

    def open_my_profile_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("My Profile Details")
        win.geometry("380x220")
        win.configure(fg_color="#181818")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        x = self.winfo_x() + (self.winfo_width() // 2) - 190
        y = self.winfo_y() + (self.winfo_height() // 2) - 110
        win.geometry(f"+{x}+{y}")

        title = ctk.CTkLabel(win, text="👤 MY ACCOUNT PROFILE", font=ctk.CTkFont(family="Outfit", size=14, weight="bold"), text_color="#FFFFFF")
        title.pack(pady=15)

        info_frame = ctk.CTkFrame(win, fg_color="transparent")
        info_frame.pack(padx=20, fill="both", expand=True)

        ctk.CTkLabel(info_frame, text=f"Username:  @{self.current_user['username']}", font=ctk.CTkFont(family="Outfit", size=12), text_color="#E5E5E5").pack(anchor="w", pady=4)
        ctk.CTkLabel(info_frame, text=f"Full Name:  {self.current_user['full_name']}", font=ctk.CTkFont(family="Outfit", size=12), text_color="#E5E5E5").pack(anchor="w", pady=4)
        ctk.CTkLabel(info_frame, text=f"Access Role:  {self.current_user['role']}", font=ctk.CTkFont(family="Outfit", size=12), text_color="#E5E5E5").pack(anchor="w", pady=4)
        ctk.CTkLabel(info_frame, text=f"Status:  ● {self.current_user['status']}", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#34A853").pack(anchor="w", pady=4)

        ctk.CTkButton(win, text="CLOSE", fg_color="#272727", hover_color="#333333", text_color="#FFFFFF", command=win.destroy).pack(pady=15, padx=20, fill="x")

    def open_change_password_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Change Password")
        win.geometry("400x320")
        win.configure(fg_color="#181818")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        x = self.winfo_x() + (self.winfo_width() // 2) - 200
        y = self.winfo_y() + (self.winfo_height() // 2) - 160
        win.geometry(f"+{x}+{y}")

        title = ctk.CTkLabel(win, text="🔒 UPDATE ACCOUNT PASSWORD", font=ctk.CTkFont(family="Outfit", size=14, weight="bold"), text_color="#FFFFFF")
        title.pack(pady=15)

        form_frame = ctk.CTkFrame(win, fg_color="transparent")
        form_frame.pack(padx=30, fill="both", expand=True)

        ctk.CTkLabel(form_frame, text="Current Password:", font=ctk.CTkFont(family="Outfit", size=11, weight="bold"), text_color="#AAAAAA").grid(row=0, column=0, sticky="w", pady=6)
        old_entry = ctk.CTkEntry(form_frame, show="*", width=200, fg_color="#1A1A1A", border_color="#303030")
        old_entry.grid(row=0, column=1, sticky="e", pady=6)

        ctk.CTkLabel(form_frame, text="New Password:", font=ctk.CTkFont(family="Outfit", size=11, weight="bold"), text_color="#AAAAAA").grid(row=1, column=0, sticky="w", pady=6)
        new_entry = ctk.CTkEntry(form_frame, show="*", width=200, fg_color="#1A1A1A", border_color="#303030")
        new_entry.grid(row=1, column=1, sticky="e", pady=6)

        ctk.CTkLabel(form_frame, text="Confirm Password:", font=ctk.CTkFont(family="Outfit", size=11, weight="bold"), text_color="#AAAAAA").grid(row=2, column=0, sticky="w", pady=6)
        confirm_entry = ctk.CTkEntry(form_frame, show="*", width=200, fg_color="#1A1A1A", border_color="#303030")
        confirm_entry.grid(row=2, column=1, sticky="e", pady=6)

        status_lbl = ctk.CTkLabel(win, text="", font=ctk.CTkFont(size=12))
        status_lbl.pack(pady=2)

        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15, padx=30)

        def proceed():
            old_val = old_entry.get()
            new_val = new_entry.get()
            conf_val = confirm_entry.get()

            if not old_val or not new_val:
                status_lbl.configure(text="Fields cannot remain empty.", text_color="#e74c3c")
                return
            if new_val != conf_val:
                status_lbl.configure(text="Passwords do not match.", text_color="#e74c3c")
                return
            
            from core.user_service import change_user_password
            if change_user_password(self.current_user["user_id"], old_val, new_val):
                status_lbl.configure(text="Password updated successfully!", text_color="#2ecc71")
                win.after(1500, win.destroy)
            else:
                status_lbl.configure(text="Incorrect current password.", text_color="#e74c3c")

        ctk.CTkButton(btn_frame, text="UPDATE PASSWORD", fg_color="#E50914", hover_color="#CC0000", command=proceed, width=150).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="CANCEL", fg_color="#272727", hover_color="#333333", text_color="#FFFFFF", command=win.destroy, width=120).pack(side="right", expand=True, padx=5)

    def create_sidebar(self):
        self.grid_columnconfigure(0, weight=1, minsize=220)
        
        self.sidebar = ctk.CTkFrame(self, fg_color="#0F0F0F", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_columnconfigure(1, weight=0)

        # Vertical separator border
        sep = ctk.CTkFrame(self.sidebar, width=1, fg_color="#2A2A2A", corner_radius=0)
        sep.grid(row=0, column=1, rowspan=15, sticky="ns")

        # Brand Title
        brand_lbl = ctk.CTkLabel(
            self.sidebar,
            text="PMLA-SCWE",
            font=ctk.CTkFont(family="Outfit", size=22, weight="bold"),
            text_color="#FFFFFF"
        )
        brand_lbl.grid(row=0, column=0, padx=20, pady=(25, 5), sticky="w")

        v_lbl = ctk.CTkLabel(
            self.sidebar,
            text="v2.0 - Core Edition",
            font=ctk.CTkFont(family="Outfit", size=11),
            text_color="#717171"
        )
        v_lbl.grid(row=1, column=0, padx=20, pady=(0, 25), sticky="w")

        # Sidebar Buttons Configuration
        self.nav_buttons = {}
        tabs = [
            ("Dashboard", "dashboard"),
            ("Student Directory", "students"),
            ("Attendance Registry", "attendance"),
            ("Assessments & Grades", "assessments"),
            ("Cyber-Wellness Audit", "wellness"),
            ("Predictive Analytics", "analytics"),
            ("Reports & Exporters", "reports"),
            ("AI Decision Assistant", "ai_assistant"),
        ]

        for idx, (title, name) in enumerate(tabs, start=2):
            btn = ctk.CTkButton(
                self.sidebar,
                text=title,
                anchor="w",
                height=38,
                fg_color="transparent",
                text_color="#E5E5E5",
                hover_color="#212121",
                corner_radius=8,
                font=ctk.CTkFont(family="Outfit", size=13),
                command=lambda n=name: self.switch_to_frame(n)
            )
            btn.grid(row=idx, column=0, padx=15, pady=3, sticky="ew")
            self.nav_buttons[name] = btn

        # Logout Button
        self.sidebar.grid_rowconfigure(10, weight=1)  # Spacer
        
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="LOGOUT USER",
            height=38,
            fg_color="#181818",
            border_color="#3A1A1A",
            border_width=1,
            hover_color="#2A1515",
            text_color="#FF4D4D",
            corner_radius=8,
            font=ctk.CTkFont(family="Outfit", size=12, weight="bold"),
            command=self.perform_logout
        )
        logout_btn.grid(row=11, column=0, padx=15, pady=20, sticky="ew")

    def switch_to_frame(self, name: str):
        if not self.sidebar:
            return

        # Check Viewer access privileges!
        if self.current_user and self.current_user.get("role") == "Viewer":
            if name not in ["dashboard", "reports", "analytics", "ai_assistant"]:
                messagebox.showwarning(
                    "Access Denied",
                    "Access Denied: Viewers are only authorized to read dashboard analytics and reports."
                )
                return

        # Update button highlights
        for tab_name, btn in self.nav_buttons.items():
            if tab_name == name:
                btn.configure(fg_color="#3A1616", text_color="#FF4D4D")
            else:
                btn.configure(fg_color="transparent", text_color="#E5E5E5")

        # Destroy old frame
        if self.active_frame:
            self.active_frame.destroy()

        # Route and initialize views
        if name == "dashboard":
            self.active_frame = DashboardFrame(self.content_container, self)
        elif name == "students":
            self.active_frame = StudentsFrame(self.content_container, self)
        elif name == "attendance":
            self.active_frame = AttendanceFrame(self.content_container, self)
        elif name == "assessments":
            self.active_frame = AssessmentsFrame(self.content_container, self)
        elif name == "wellness":
            self.active_frame = WellnessFrame(self.content_container, self)
        elif name == "analytics":
            self.active_frame = AnalyticsViewFrame(self.content_container, self)
        elif name == "reports":
            self.active_frame = ReportsFrame(self.content_container, self)
        elif name == "ai_assistant":
            self.active_frame = AIAssistantFrame(self.content_container, self)
        elif name == "users":
            self.active_frame = UsersFrame(self.content_container, self)

        # Active view gridded at row 1 (below top_bar at row 0)
        self.active_frame.grid(row=1, column=0, sticky="nsew")
        self.refresh_top_bar_counts()

    def perform_logout(self):
        self.current_user = None
        self.show_login_screen()


def run():
    app = MainApp()
    app.mainloop()


if __name__ == "__main__":
    run()
