"""CustomTkinter panel for marking and saving bulk student attendance."""

from __future__ import annotations
import datetime
import tkinter as tk
import customtkinter as ctk

from core import attendance_service
from core.database import get_db_status


class AttendanceFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header section
        header_frame = ctk.CTkFrame(self, fg_color="#0F0F0F", border_color="#2A2A2A", border_width=1, corner_radius=12, height=80)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header_frame,
            text="ATTENDANCE REGISTRY",
            font=ctk.CTkFont(family="Outfit", size=24, weight="bold"),
            text_color="#FFFFFF"
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        self.db_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(family="Outfit", size=12),
            text_color="#AAAAAA"
        )
        self.db_label.grid(row=0, column=1, sticky="e", padx=20)
        self.update_db_status()

        # Filters controls panel
        controls_frame = ctk.CTkFrame(self, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        # Class dropdown selector
        class_label = ctk.CTkLabel(
            controls_frame,
            text="Select Class:",
            font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            text_color="#AAAAAA"
        )
        class_label.grid(row=0, column=0, padx=(20, 10), pady=15, sticky="w")

        self.classes = ["XII-A", "XII-B", "XI-A", "XI-B", "X-A", "X-B"]
        self.class_selector = ctk.CTkOptionMenu(
            controls_frame,
            values=self.classes,
            command=self.load_class_roster,
            fg_color="#181818",
            button_color="#E50914",
            button_hover_color="#CC0000",
            dropdown_fg_color="#1A1A1A",
            dropdown_text_color="#FFFFFF",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=13),
            dropdown_font=ctk.CTkFont(family="Outfit", size=13)
        )
        self.class_selector.grid(row=0, column=1, padx=10, pady=15, sticky="w")

        # Date entry selector
        date_label = ctk.CTkLabel(
            controls_frame,
            text="Date (YYYY-MM-DD):",
            font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            text_color="#AAAAAA"
        )
        date_label.grid(row=0, column=2, padx=(30, 10), pady=15, sticky="w")

        self.date_entry = ctk.CTkEntry(
            controls_frame,
            placeholder_text="YYYY-MM-DD",
            width=140,
            fg_color="#181818",
            border_color="#303030",
            focused_border_color="#FF0000",
            placeholder_text_color="#717171",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=13)
        )
        self.date_entry.grid(row=0, column=3, padx=10, pady=15, sticky="w")
        self.date_entry.insert(0, datetime.date.today().isoformat())
        self.date_entry.bind("<FocusOut>", lambda e: self.load_class_roster())
        self.date_entry.bind("<Return>", lambda e: self.load_class_roster())

        # Load button
        load_btn = ctk.CTkButton(
            controls_frame,
            text="Load Cohort",
            command=self.load_class_roster,
            fg_color="#272727",
            hover_color="#333333",
            text_color="#FFFFFF",
            border_width=1,
            border_color="#3A3A3A",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold")
        )
        load_btn.grid(row=0, column=4, padx=20, pady=15, sticky="w")

        # Student attendance roster table frame
        self.roster_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#1A1A1A",
            border_color="#2A2A2A",
            border_width=1,
            corner_radius=12,
            label_text="STUDENT LIST",
            label_font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            label_text_color="#FFFFFF"
        )
        self.roster_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.roster_frame.grid_columnconfigure(0, weight=2)
        self.roster_frame.grid_columnconfigure(1, weight=1)
        self.roster_frame.grid_columnconfigure(2, weight=1)

        # Bottom actions
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=15)
        actions_frame.grid_columnconfigure(0, weight=1)

        self.status_msg = ctk.CTkLabel(
            actions_frame,
            text="",
            font=ctk.CTkFont(family="Outfit", size=14),
            text_color="#34A853"
        )
        self.status_msg.grid(row=0, column=0, sticky="w", padx=10)

        self.save_btn = ctk.CTkButton(
            actions_frame,
            text="SAVE ALL ATTENDANCE",
            command=self.save_all_attendance,
            height=45,
            width=200,
            fg_color="#E50914",
            hover_color="#CC0000",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Outfit", size=14, weight="bold")
        )
        self.save_btn.grid(row=0, column=1, sticky="e", padx=10)

        # State containers
        self.student_rows = []
        self.attendance_values = {}  # student_id -> CTkSegmentedButton / status tracker

        # Initial load
        self.load_class_roster()

    def update_db_status(self):
        status = get_db_status()
        self.db_label.configure(text=status["display"])
        color = "#34A853" if status["backend"] == "MySQL" else "#FFD600"
        self.db_label.configure(text_color=color)

    def load_class_roster(self, *args):
        # Refresh database status label
        self.update_db_status()

        # Clear existing roster entries
        for widget in self.roster_frame.winfo_children():
            widget.destroy()

        self.attendance_values.clear()
        self.student_rows.clear()

        # Retrieve date & class
        selected_class = self.class_selector.get()
        date_str = self.date_entry.get().strip()

        # Validate date string
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            self.show_message("Invalid date format. Use YYYY-MM-DD.", is_error=True)
            return

        # Fetch students in the selected section
        students = attendance_service.get_students_by_class(selected_class)
        
        # Fetch existing attendance records for the date and class
        existing_attendance = attendance_service.get_attendance_for_date_and_class(date_str, selected_class)

        if not students:
            no_students_lbl = ctk.CTkLabel(
                self.roster_frame,
                text="No students found in this class section.",
                font=ctk.CTkFont(family="Outfit", size=14),
                text_color="#95a5a6"
            )
            no_students_lbl.grid(row=0, column=0, columnspan=3, pady=40)
            return

        # Draw Table Headers
        ctk.CTkLabel(
            self.roster_frame,
            text="Student Name",
            font=ctk.CTkFont(family="Outfit", size=12, weight="bold"),
            text_color="#AAAAAA"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(5, 10))

        ctk.CTkLabel(
            self.roster_frame,
            text="Roll Number / Info",
            font=ctk.CTkFont(family="Outfit", size=12, weight="bold"),
            text_color="#AAAAAA"
        ).grid(row=0, column=1, sticky="w", padx=15, pady=(5, 10))

        ctk.CTkLabel(
            self.roster_frame,
            text="Attendance Status",
            font=ctk.CTkFont(family="Outfit", size=12, weight="bold"),
            text_color="#AAAAAA"
        ).grid(row=0, column=2, padx=15, pady=(5, 10))

        # Populate student rows
        for idx, student in enumerate(students, start=1):
            student_id = student["student_id"]
            full_name = f"{student['first_name']} {student['last_name']}"
            roll_number = f"ID: {student_id}"

            # Alternate row background colors slightly for table styling
            row_bg = "#1A1A1A" if idx % 2 == 0 else "#181818"
            row_frame = ctk.CTkFrame(self.roster_frame, fg_color=row_bg, height=45, corner_radius=6)
            row_frame.grid(row=idx, column=0, columnspan=3, sticky="ew", pady=3, ipady=5)
            row_frame.grid_columnconfigure(0, weight=2)
            row_frame.grid_columnconfigure(1, weight=1)
            row_frame.grid_columnconfigure(2, weight=1)

            # Name Label
            name_lbl = ctk.CTkLabel(
                row_frame,
                text=full_name,
                font=ctk.CTkFont(family="Outfit", size=13, weight="bold"),
                text_color="#FFFFFF"
            )
            name_lbl.grid(row=0, column=0, sticky="w", padx=15, pady=5)

            # Info Label
            info_lbl = ctk.CTkLabel(
                row_frame,
                text=roll_number,
                font=ctk.CTkFont(family="Outfit", size=12),
                text_color="#AAAAAA"
            )
            info_lbl.grid(row=0, column=1, sticky="w", padx=15, pady=5)

            # Attendance Segmented Control ("Present" vs "Absent")
            # Fallback to "Present" if no record exists yet
            status_val = existing_attendance.get(student_id, "Present")
            
            status_btn = ctk.CTkSegmentedButton(
                row_frame,
                values=["Present", "Absent"],
                selected_color="#E50914",
                selected_hover_color="#CC0000",
                fg_color="#181818",
                text_color="#FFFFFF",
                selected_text_color="#FFFFFF",
                font=ctk.CTkFont(family="Outfit", size=11, weight="bold")
            )
            status_btn.grid(row=0, column=2, padx=15, pady=5)
            status_btn.set(status_val)
            
            self.attendance_values[student_id] = status_btn

        self.show_message(f"Roster loaded for Class {selected_class} on date {date_str}.")

    def save_all_attendance(self):
        # Refresh database status
        self.update_db_status()

        date_str = self.date_entry.get().strip()
        selected_class = self.class_selector.get()

        # Validate date string
        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            self.show_message("Invalid date format. Cannot save.", is_error=True)
            return

        if not self.attendance_values:
            self.show_message("No student records available to save.", is_error=True)
            return

        # Extract values
        records = {}
        for student_id, segmented_btn in self.attendance_values.items():
            status = segmented_btn.get()
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
        self.status_msg.configure(text=message, text_color=color)
        # Clear status message after 4 seconds
        self.after(4000, lambda: self.status_msg.configure(text=""))
