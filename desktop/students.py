"""CustomTkinter panel for student registration, search, and CRUD administration."""

from __future__ import annotations
import tkinter as tk
import customtkinter as ctk

from core import student_service


class StudentsFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header Section
        header_frame = ctk.CTkFrame(self, fg_color="#0F0F0F", border_color="#2A2A2A", border_width=1, corner_radius=12, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header_frame,
            text="STUDENT DIRECTORY",
            font=ctk.CTkFont(family="Outfit", size=24, weight="bold"),
            text_color="#FFFFFF"
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        # Controls & Search Panel
        search_frame = ctk.CTkFrame(self, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        search_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        # Add Student Button
        add_btn = ctk.CTkButton(
            search_frame,
            text="+ REGISTER NEW STUDENT",
            command=self.open_add_student_dialog,
            fg_color="#E50914",
            hover_color="#CC0000",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold")
        )
        add_btn.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Search inputs
        search_lbl = ctk.CTkLabel(
            search_frame,
            text="Search:",
            font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            text_color="#AAAAAA"
        )
        search_lbl.grid(row=0, column=1, padx=(30, 5), pady=15, sticky="e")

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Enter Name, Class or ID...",
            width=250,
            fg_color="#181818",
            border_color="#303030",
            focused_border_color="#FF0000",
            placeholder_text_color="#717171",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=13)
        )
        self.search_entry.grid(row=0, column=2, padx=10, pady=15, sticky="w")
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        search_action_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.perform_search,
            width=100,
            fg_color="#272727",
            hover_color="#333333",
            text_color="#FFFFFF",
            border_width=1,
            border_color="#3A3A3A",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold")
        )
        search_action_btn.grid(row=0, column=3, padx=10, pady=15, sticky="w")

        clear_action_btn = ctk.CTkButton(
            search_frame,
            text="Clear",
            command=self.clear_search,
            width=80,
            fg_color="#272727",
            hover_color="#333333",
            text_color="#FFFFFF",
            border_width=1,
            border_color="#3A3A3A",
            font=ctk.CTkFont(family="Outfit", size=13)
        )
        clear_action_btn.grid(row=0, column=4, padx=(0, 20), pady=15, sticky="w")

        # Table Display ScrollFrame
        self.table_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="#1A1A1A",
            border_color="#2A2A2A",
            border_width=1,
            corner_radius=12,
            label_text="REGISTERED STUDENTS LIST",
            label_font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            label_text_color="#FFFFFF"
        )
        self.table_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.table_scroll.grid_columnconfigure(0, weight=1)  # ID
        self.table_scroll.grid_columnconfigure(1, weight=3)  # Name
        self.table_scroll.grid_columnconfigure(2, weight=2)  # Class
        self.table_scroll.grid_columnconfigure(3, weight=3)  # Email
        self.table_scroll.grid_columnconfigure(4, weight=2)  # Phone
        self.table_scroll.grid_columnconfigure(5, weight=2)  # Actions

        # Status Message Box
        self.status_msg = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Outfit", size=13),
            text_color="#34A853"
        )
        self.status_msg.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 15))

        # Initial Load
        self.load_students()

    def load_students(self, query: str | None = None):
        # Clear existing roster rows
        for widget in self.table_scroll.winfo_children():
            widget.destroy()

        if query:
            students = student_service.search_students(query)
        else:
            students = student_service.get_all_students()

        if not students:
            no_lbl = ctk.CTkLabel(
                self.table_scroll,
                text="No student records found.",
                font=ctk.CTkFont(family="Outfit", size=14),
                text_color="#95a5a6"
            )
            no_lbl.grid(row=0, column=0, columnspan=6, pady=40)
            return

        # Headers
        headers = ["ID", "Student Name", "Class/Section", "Email Address", "Phone Number", "Manage Actions"]
        for col_idx, header in enumerate(headers):
            lbl = ctk.CTkLabel(
                self.table_scroll,
                text=header,
                font=ctk.CTkFont(family="Outfit", size=12, weight="bold"),
                text_color="#AAAAAA"
            )
            sticky_val = "w" if col_idx < 5 else ""
            lbl.grid(row=0, column=col_idx, sticky=sticky_val, padx=15, pady=(5, 10))

        # Rows
        for row_idx, student in enumerate(students, start=1):
            sid = student["student_id"]
            name = f"{student['first_name']} {student['last_name']}"
            class_sec = student["class_section"]
            email = student["email"] or "N/A"
            phone = student["phone"] or "N/A"

            row_bg = "#1A1A1A" if row_idx % 2 == 0 else "#181818"
            row_frame = ctk.CTkFrame(self.table_scroll, fg_color=row_bg, height=45, corner_radius=6)
            row_frame.grid(row=row_idx, column=0, columnspan=6, sticky="ew", pady=3, ipady=4)
            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, weight=3)
            row_frame.grid_columnconfigure(2, weight=2)
            row_frame.grid_columnconfigure(3, weight=3)
            row_frame.grid_columnconfigure(4, weight=2)
            row_frame.grid_columnconfigure(5, weight=2)

            ctk.CTkLabel(row_frame, text=str(sid), font=ctk.CTkFont(family="Outfit", size=13), text_color="#FFFFFF").grid(row=0, column=0, sticky="w", padx=15)
            ctk.CTkLabel(row_frame, text=name, font=ctk.CTkFont(family="Outfit", size=13, weight="bold"), text_color="#FFFFFF").grid(row=0, column=1, sticky="w", padx=15)
            ctk.CTkLabel(row_frame, text=class_sec, font=ctk.CTkFont(family="Outfit", size=13), text_color="#FFFFFF").grid(row=0, column=2, sticky="w", padx=15)
            ctk.CTkLabel(row_frame, text=email, font=ctk.CTkFont(family="Outfit", size=12), text_color="#AAAAAA").grid(row=0, column=3, sticky="w", padx=15)
            ctk.CTkLabel(row_frame, text=phone, font=ctk.CTkFont(family="Outfit", size=12), text_color="#AAAAAA").grid(row=0, column=4, sticky="w", padx=15)

            # Action buttons
            actions_sub_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_sub_frame.grid(row=0, column=5, padx=10)

            edit_btn = ctk.CTkButton(
                actions_sub_frame,
                text="Edit",
                command=lambda s=student: self.open_edit_student_dialog(s),
                width=55,
                height=24,
                fg_color="#272727",
                hover_color="#333333",
                text_color="#FFFFFF",
                border_width=1,
                border_color="#3A3A3A",
                font=ctk.CTkFont(family="Outfit", size=11)
            )
            edit_btn.pack(side="left", padx=3)

            delete_btn = ctk.CTkButton(
                actions_sub_frame,
                text="Delete",
                command=lambda id=sid: self.confirm_delete_student(id),
                width=60,
                height=24,
                fg_color="#181818",
                border_color="#3A1A1A",
                border_width=1,
                hover_color="#3A1616",
                text_color="#FF4D4D",
                font=ctk.CTkFont(family="Outfit", size=11)
            )
            delete_btn.pack(side="left", padx=3)

    def perform_search(self):
        q = self.search_entry.get().strip()
        if not q:
            self.load_students()
            return
        self.load_students(q)
        self.show_status(f"Search results loaded for '{q}'.")

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.load_students()
        self.show_status("Cleared search query.")

    def show_status(self, text: str, is_error: bool = False):
        color = "#e74c3c" if is_error else "#2ecc71"
        self.status_msg.configure(text=text, text_color=color)
        self.after(4000, lambda: self.status_msg.configure(text=""))

    def confirm_delete_student(self, student_id: int):
        # CTk Confirmation Box Toplevel
        confirm_win = ctk.CTkToplevel(self)
        confirm_win.title("Delete Student Confirmation")
        confirm_win.geometry("380x180")
        confirm_win.resizable(False, False)
        confirm_win.transient(self.winfo_toplevel())
        confirm_win.grab_set()

        # Center Window
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() // 2) - 190
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() // 2) - 90
        confirm_win.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(
            confirm_win,
            text=f"Are you sure you want to permanently delete\nStudent ID {student_id}?\n\nThis will remove all associated logs and audits.",
            font=ctk.CTkFont(family="Outfit", size=13),
            text_color="#e0e0e0"
        )
        label.pack(pady=20)

        btn_frame = ctk.CTkFrame(confirm_win, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20)

        def proceed():
            try:
                if student_service.delete_student(student_id):
                    self.show_status(f"Successfully deleted student ID {student_id}.")
                    self.load_students()
                else:
                    self.show_status("Failed to delete student.", is_error=True)
            except Exception as e:
                self.show_status(f"Database error: {e}", is_error=True)
            confirm_win.destroy()

        yes_btn = ctk.CTkButton(btn_frame, text="DELETE", fg_color="#E50914", hover_color="#CC0000", command=proceed, width=100)
        yes_btn.pack(side="left", expand=True, padx=10)

        no_btn = ctk.CTkButton(btn_frame, text="CANCEL", fg_color="#272727", hover_color="#333333", text_color="#FFFFFF", command=confirm_win.destroy, width=100)
        no_btn.pack(side="right", expand=True, padx=10)

    def open_add_student_dialog(self):
        self.open_student_form_dialog()

    def open_edit_student_dialog(self, student: dict):
        self.open_student_form_dialog(student)

    def open_student_form_dialog(self, student_data: dict | None = None):
        form_win = ctk.CTkToplevel(self)
        form_win.configure(fg_color="#181818")
        is_edit = student_data is not None
        title = "Edit Student Profile" if is_edit else "Register New Student"
        form_win.title(title)
        form_win.geometry("450x520")
        form_win.resizable(False, False)
        form_win.transient(self.winfo_toplevel())
        form_win.grab_set()

        # Center Window
        x = self.winfo_toplevel().winfo_x() + (self.winfo_toplevel().winfo_width() // 2) - 225
        y = self.winfo_toplevel().winfo_y() + (self.winfo_toplevel().winfo_height() // 2) - 260
        form_win.geometry(f"+{x}+{y}")

        title_lbl = ctk.CTkLabel(
            form_win,
            text=title.upper(),
            font=ctk.CTkFont(family="Outfit", size=18, weight="bold"),
            text_color="#FFFFFF"
        )
        title_lbl.pack(pady=15)

        # Form Inputs Scroll Frame
        form_frame = ctk.CTkFrame(form_win, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30)

        # Fields
        labels_fields = [
            ("First Name*:", "first_name", "entry"),
            ("Last Name*:", "last_name", "entry"),
            ("Class/Section* (e.g. XII-A):", "class_section", "entry"),
            ("Date of Birth (YYYY-MM-DD):", "dob", "entry"),
            ("Gender (M/F/O):", "gender", "option"),
            ("Email Address:", "email", "entry"),
            ("Phone Number:", "phone", "entry"),
        ]

        widgets = {}
        for row, (label_text, field_name, w_type) in enumerate(labels_fields):
            lbl = ctk.CTkLabel(
                form_frame,
                text=label_text,
                font=ctk.CTkFont(family="Outfit", size=12, weight="bold"),
                text_color="#AAAAAA"
            )
            lbl.grid(row=row, column=0, sticky="w", pady=6)

            if w_type == "entry":
                entry = ctk.CTkEntry(
                    form_frame, 
                    width=220, 
                    fg_color="#1A1A1A", 
                    border_color="#303030", 
                    focused_border_color="#FF0000",
                    placeholder_text_color="#717171",
                    text_color="#FFFFFF",
                    font=ctk.CTkFont(family="Outfit", size=12)
                )
                entry.grid(row=row, column=1, sticky="e", pady=6)
                if is_edit and student_data.get(field_name):
                    entry.insert(0, str(student_data[field_name]))
                widgets[field_name] = entry
            elif w_type == "option":
                var = tk.StringVar(value=student_data.get("gender", "O") if is_edit else "O")
                opt = ctk.CTkOptionMenu(
                    form_frame, 
                    values=["M", "F", "O"], 
                    variable=var, 
                    width=120, 
                    fg_color="#1A1A1A", 
                    button_color="#E50914", 
                    button_hover_color="#CC0000",
                    dropdown_fg_color="#181818", 
                    dropdown_text_color="#FFFFFF",
                    text_color="#FFFFFF"
                )
                opt.grid(row=row, column=1, sticky="w", pady=6)
                widgets[field_name] = var

        # Action Buttons
        btn_frame = ctk.CTkFrame(form_win, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom", pady=20, padx=30)

        def save():
            first = widgets["first_name"].get().strip()
            last = widgets["last_name"].get().strip()
            cls = widgets["class_section"].get().strip()
            dob_val = widgets["dob"].get().strip() or None
            gender_val = widgets["gender"].get()
            email_val = widgets["email"].get().strip() or None
            phone_val = widgets["phone"].get().strip() or None

            if not first or not last or not cls:
                widgets["first_name"].focus()
                # Simple color feedback or window title alert
                return

            import datetime
            if dob_val:
                try:
                    datetime.datetime.strptime(dob_val, "%Y-%m-%d")
                except ValueError:
                    widgets["dob"].configure(border_color="#FF0000")
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
                if is_edit:
                    ok = student_service.update_student(student_data["student_id"], payload)
                    msg = "Student updated successfully."
                else:
                    ok = student_service.add_student(payload)
                    msg = "Student registered successfully."

                if ok:
                    from core.database import log_activity
                    log_activity(f"Student {first} {last} registered" if not is_edit else f"Student ID {student_data['student_id']} profile updated")
                    self.show_status(msg)
                    self.load_students()
                    form_win.destroy()
                else:
                    self.show_status("Operation failed. Try again.", is_error=True)
            except Exception as e:
                self.show_status(f"Error saving profile: {e}", is_error=True)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="SAVE CHANGES" if is_edit else "REGISTER STUDENT",
            fg_color="#E50914",
            hover_color="#CC0000",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold"),
            command=save
        )
        save_btn.pack(side="left", expand=True, padx=5)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="CANCEL",
            fg_color="#272727",
            hover_color="#333333",
            text_color="#ffffff",
            command=form_win.destroy
        )
        cancel_btn.pack(side="right", expand=True, padx=5)
