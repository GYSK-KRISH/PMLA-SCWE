"""CustomTkinter Login panel for administrative access authorization."""

from __future__ import annotations
import customtkinter as ctk

from core import auth_service
from core.database import get_db_status


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, on_login_success):
        super().__init__(parent, fg_color="#1A1A1A", corner_radius=12)
        self.controller = controller
        self.on_login_success = on_login_success

        # Center contents
        self.grid_columnconfigure(0, weight=1)
        
        # Upper Margin
        self.grid_rowconfigure(0, minsize=40)
        self.grid_rowconfigure(7, minsize=40)

        # Title/Brand
        title_lbl = ctk.CTkLabel(
            self,
            text="PMLA-SCWE LOGIN",
            font=ctk.CTkFont(family="Outfit", size=26, weight="bold"),
            text_color="#FFFFFF"
        )
        title_lbl.grid(row=1, column=0, pady=(10, 5), sticky="n")

        subtitle_lbl = ctk.CTkLabel(
            self,
            text="Predictive Learning & Cyber-Wellness Engine",
            font=ctk.CTkFont(family="Outfit", size=13),
            text_color="#AAAAAA"
        )
        subtitle_lbl.grid(row=2, column=0, pady=(0, 30), sticky="n")

        # Username Input
        self.username_entry = ctk.CTkEntry(
            self,
            placeholder_text="Administrator Username",
            width=280,
            height=45,
            fg_color="#181818",
            border_color="#303030",
            focused_border_color="#FF0000",
            placeholder_text_color="#717171",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=13)
        )
        self.username_entry.grid(row=3, column=0, pady=10, sticky="n")

        # Password Input
        self.password_entry = ctk.CTkEntry(
            self,
            placeholder_text="Password",
            show="*",
            width=280,
            height=45,
            fg_color="#181818",
            border_color="#303030",
            focused_border_color="#FF0000",
            placeholder_text_color="#717171",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=13)
        )
        self.password_entry.grid(row=4, column=0, pady=10, sticky="n")
        self.password_entry.bind("<Return>", lambda e: self.attempt_login())

        # Error / Status Feedback Label
        self.feedback_lbl = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Outfit", size=13),
            text_color="#FF0000"
        )
        self.feedback_lbl.grid(row=5, column=0, pady=5, sticky="n")

        # Login Action Button
        login_btn = ctk.CTkButton(
            self,
            text="AUTHORIZE ACCESS",
            command=self.attempt_login,
            width=280,
            height=45,
            fg_color="#E50914",
            hover_color="#CC0000",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold")
        )
        login_btn.grid(row=6, column=0, pady=(15, 10), sticky="n")

        # Database Fallback Status Indicator
        self.db_status_lbl = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Outfit", size=11),
            text_color="#AAAAAA"
        )
        self.db_status_lbl.grid(row=8, column=0, pady=(10, 20), sticky="s")
        self.update_status()

    def update_status(self):
        status = get_db_status()
        self.db_status_lbl.configure(text=status["display"])
        color = "#34A853" if status["backend"] == "MySQL" else "#FFD600"
        self.db_status_lbl.configure(text_color=color)

    def attempt_login(self):
        self.update_status()
        
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.show_error("Fields cannot remain empty.")
            return

        try:
            user = auth_service.login_user(username, password)
            if user:
                # Store logged-in user inside controller session context
                self.controller.current_user = user
                
                # Clear fields
                self.username_entry.delete(0, "end")
                self.password_entry.delete(0, "end")
                self.feedback_lbl.configure(text="")
                
                # Trigger callback
                self.on_login_success()
            else:
                self.show_error("Invalid username or password.")
        except Exception as e:
            self.show_error(f"Database error occurred: {e}")

    def show_error(self, text: str):
        self.feedback_lbl.configure(text=text, text_color="#e74c3c")
