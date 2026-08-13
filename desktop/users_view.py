"""CustomTkinter panel for administrative user accounts CRUD management."""

from __future__ import annotations
import tkinter as tk
import customtkinter as ctk

from core import user_service
from core.database import get_db_status


class UsersFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header Section
        header_frame = ctk.CTkFrame(self, fg_color="#0F0F0F", border_color="#2A2A2A", border_width=1, corner_radius=12, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header_frame,
            text="USER ACCOUNTS MANAGEMENT",
            font=ctk.CTkFont(family="Outfit", size=20, weight="bold"),
            text_color="#FFFFFF"
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=15)

        # Controls & Search Panel
        search_frame = ctk.CTkFrame(self, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        search_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        # Add User Button
        add_btn = ctk.CTkButton(
            search_frame,
            text="+ ADD SYSTEM USER",
            command=self.open_add_user_dialog,
            fg_color="#E50914",
            hover_color="#CC0000",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold")
        )
        add_btn.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Table Display ScrollFrame
        self.table_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="#1A1A1A",
            border_color="#2A2A2A",
            border_width=1,
            corner_radius=12,
            label_text="REGISTERED USER ROSTER",
            label_font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            label_text_color="#FFFFFF"
        )
        self.table_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.table_scroll.grid_columnconfigure(0, weight=1)

        # Status Bar
        self.status_msg = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), text_color="#2ecc71")
        self.status_msg.grid(row=3, column=0, pady=5)

        # Load initial user list
        self.load_users()

    def load_users(self):
        # Clear existing table rows
        for w in self.table_scroll.winfo_children():
            w.destroy()

        users = user_service.list_users()
        
        # Headers
        headers_frame = ctk.CTkFrame(self.table_scroll, fg_color="transparent")
        headers_frame.pack(fill="x", pady=(5, 10), padx=5)
        headers_frame.grid_columnconfigure(0, weight=2)
        headers_frame.grid_columnconfigure(1, weight=1)
        headers_frame.grid_columnconfigure(2, weight=1)
        headers_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(headers_frame, text="User Account", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#AAAAAA", anchor="w").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(headers_frame, text="Role", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#AAAAAA", anchor="w").grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(headers_frame, text="Status", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#AAAAAA", anchor="w").grid(row=0, column=2, sticky="w")
        ctk.CTkLabel(headers_frame, text="Actions", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#AAAAAA", anchor="e").grid(row=0, column=3, sticky="e", padx=15)

        if not users:
            no_users = ctk.CTkLabel(self.table_scroll, text="No users registered in system.", text_color="#AAAAAA")
            no_users.pack(pady=40)
            return

        for idx, u in enumerate(users):
            row_bg = "#1A1A1A" if idx % 2 == 0 else "#181818"
            row_frame = ctk.CTkFrame(self.table_scroll, fg_color=row_bg, height=45, corner_radius=6)
            row_frame.pack(fill="x", pady=2, ipady=4)
            row_frame.grid_columnconfigure(0, weight=2)
            row_frame.grid_columnconfigure(1, weight=1)
            row_frame.grid_columnconfigure(2, weight=1)
            row_frame.grid_columnconfigure(3, weight=1)

            # Name info
            name_lbl = ctk.CTkLabel(
                row_frame,
                text=f"{u['full_name']} (@{u['username']})",
                font=ctk.CTkFont(family="Outfit", size=13, weight="bold"),
                text_color="#FFFFFF"
            )
            name_lbl.grid(row=0, column=0, sticky="w", padx=15, pady=8)

            # Role
            role_lbl = ctk.CTkLabel(row_frame, text=u["role"], font=ctk.CTkFont(family="Outfit", size=12), text_color="#E5E5E5")
            role_lbl.grid(row=0, column=1, sticky="w", padx=5)

            # Status Badge
            status_color = "#34A853" if u["status"] == "Active" else "#FF0000"
            status_lbl = ctk.CTkLabel(row_frame, text=f"● {u['status']}", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color=status_color)
            status_lbl.grid(row=0, column=2, sticky="w", padx=5)

            # Actions Sub-frame
            actions_sub = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_sub.grid(row=0, column=3, sticky="e", padx=15)

            edit_btn = ctk.CTkButton(
                actions_sub,
                text="Edit",
                command=lambda user=u: self.open_edit_user_dialog(user),
                width=50,
                height=24,
                fg_color="#272727",
                hover_color="#333333",
                text_color="#FFFFFF",
                font=ctk.CTkFont(family="Outfit", size=11)
            )
            edit_btn.pack(side="left", padx=3)

            # Do not allow deleting the core admin
            if u["username"] != "admin":
                delete_btn = ctk.CTkButton(
                    actions_sub,
                    text="Delete",
                    command=lambda uid=u["user_id"]: self.confirm_delete_user(uid),
                    width=50,
                    height=24,
                    fg_color="#181818",
                    border_color="#3A1A1A",
                    border_width=1,
                    hover_color="#3A1616",
                    text_color="#FF4D4D",
                    font=ctk.CTkFont(family="Outfit", size=11)
                )
                delete_btn.pack(side="left", padx=3)

    def show_status(self, text: str, is_error: bool = False):
        color = "#e74c3c" if is_error else "#2ecc71"
        self.status_msg.configure(text=text, text_color=color)
        self.after(4000, lambda: self.status_msg.configure(text=""))

    def confirm_delete_user(self, user_id: int):
        confirm_win = ctk.CTkToplevel(self)
        confirm_win.title("Delete Account")
        confirm_win.geometry("380x160")
        confirm_win.resizable(False, False)
        confirm_win.transient(self.winfo_toplevel())
        confirm_win.grab_set()

        # Center
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() // 2) - 190
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() // 2) - 80
        confirm_win.geometry(f"+{x}+{y}")

        lbl = ctk.CTkLabel(confirm_win, text=f"Are you sure you want to permanently delete\nUser ID {user_id}?", font=ctk.CTkFont(family="Outfit", size=13))
        lbl.pack(pady=20)

        btn_frame = ctk.CTkFrame(confirm_win, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20)

        def proceed():
            if user_service.delete_user(user_id):
                self.show_status("User account deleted.")
                self.load_users()
            else:
                self.show_status("Action failed.", is_error=True)
            confirm_win.destroy()

        ctk.CTkButton(btn_frame, text="DELETE", fg_color="#E50914", hover_color="#CC0000", command=proceed, width=100).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="CANCEL", fg_color="#272727", hover_color="#333333", text_color="#FFFFFF", command=confirm_win.destroy, width=100).pack(side="right", expand=True, padx=5)

    def open_add_user_dialog(self):
        self.open_user_form_dialog()

    def open_edit_user_dialog(self, user: dict):
        self.open_user_form_dialog(user)

    def open_user_form_dialog(self, user_data: dict | None = None):
        form_win = ctk.CTkToplevel(self)
        form_win.configure(fg_color="#181818")
        is_edit = user_data is not None
        title = "Edit User Settings" if is_edit else "Register System User"
        form_win.title(title)
        form_win.geometry("450x420")
        form_win.resizable(False, False)
        form_win.transient(self.winfo_toplevel())
        form_win.grab_set()

        # Center
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() // 2) - 225
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() // 2) - 210
        form_win.geometry(f"+{x}+{y}")

        title_lbl = ctk.CTkLabel(form_win, text=title.upper(), font=ctk.CTkFont(family="Outfit", size=16, weight="bold"), text_color="#FFFFFF")
        title_lbl.pack(pady=15)

        form_frame = ctk.CTkFrame(form_win, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30)

        # Fields
        labels_fields = [
            ("Username (unique):", "username"),
            ("Full Name:", "full_name")
        ]
        
        widgets = {}
        for r, (label_text, field_name) in enumerate(labels_fields):
            ctk.CTkLabel(form_frame, text=label_text, font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#AAAAAA").grid(row=r, column=0, sticky="w", pady=8)
            entry = ctk.CTkEntry(form_frame, width=220, fg_color="#1A1A1A", border_color="#303030", focused_border_color="#FF0000", text_color="#FFFFFF")
            entry.grid(row=r, column=1, sticky="e", pady=8)
            if is_edit:
                entry.insert(0, str(user_data[field_name]))
                if field_name == "username":
                    entry.configure(state="disabled") # Cannot rename username
            widgets[field_name] = entry

        # Role Option Dropdown
        ctk.CTkLabel(form_frame, text="Privilege Role:", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#AAAAAA").grid(row=2, column=0, sticky="w", pady=8)
        role_var = tk.StringVar(value=user_data.get("role", "Teacher") if is_edit else "Teacher")
        role_opt = ctk.CTkOptionMenu(form_frame, values=["Admin", "Teacher", "Viewer"], variable=role_var, width=120, fg_color="#1A1A1A", button_color="#E50914")
        role_opt.grid(row=2, column=1, sticky="w", pady=8)

        # Status Option Dropdown
        ctk.CTkLabel(form_frame, text="Account Status:", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#AAAAAA").grid(row=3, column=0, sticky="w", pady=8)
        status_var = tk.StringVar(value=user_data.get("status", "Active") if is_edit else "Active")
        status_opt = ctk.CTkOptionMenu(form_frame, values=["Active", "Inactive"], variable=status_var, width=120, fg_color="#1A1A1A", button_color="#E50914")
        status_opt.grid(row=3, column=1, sticky="w", pady=8)

        # Password Entry (Only for registration)
        widgets["password"] = None
        if not is_edit:
            ctk.CTkLabel(form_frame, text="Initial Password:", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#AAAAAA").grid(row=4, column=0, sticky="w", pady=8)
            pass_entry = ctk.CTkEntry(form_frame, show="*", width=220, fg_color="#1A1A1A", border_color="#303030", focused_border_color="#FF0000", text_color="#FFFFFF")
            pass_entry.grid(row=4, column=1, sticky="e", pady=8)
            widgets["password"] = pass_entry

        btn_frame = ctk.CTkFrame(form_win, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom", pady=20, padx=30)

        def save():
            uname = widgets["username"].get().strip().lower()
            fname = widgets["full_name"].get().strip()
            role_val = role_var.get()
            stat_val = status_var.get()

            if not fname:
                return

            if is_edit:
                if user_service.update_user(user_data["user_id"], user_data["username"], fname, role_val, stat_val):
                    self.show_status("User settings updated.")
                    self.load_users()
                    form_win.destroy()
                else:
                    self.show_status("Failed to save changes.", is_error=True)
            else:
                passwd = widgets["password"].get()
                if not uname or not passwd:
                    return
                if user_service.create_user(uname, fname, passwd, role_val, stat_val):
                    self.show_status("User registered successfully.")
                    self.load_users()
                    form_win.destroy()
                else:
                    self.show_status("Username already exists or database error.", is_error=True)

        ctk.CTkButton(btn_frame, text="SAVE USER", fg_color="#E50914", hover_color="#CC0000", command=save, width=120).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="CANCEL", fg_color="#272727", hover_color="#333333", text_color="#FFFFFF", command=form_win.destroy, width=120).pack(side="right", expand=True, padx=5)
