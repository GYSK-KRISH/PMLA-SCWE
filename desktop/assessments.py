"""CustomTkinter panel for adding student diagnostic marks and displaying test history logs."""

from __future__ import annotations
import datetime
import customtkinter as ctk

from core import student_service, assessment_service
from core.database import get_db_status


class AssessmentsFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Grid configuration
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=1)

        # Header Section
        header_frame = ctk.CTkFrame(self, fg_color="#0F0F0F", border_color="#2A2A2A", border_width=1, corner_radius=12, height=80)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header_frame,
            text="ACADEMIC ASSESSMENTS & GRADES",
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

        # Selection Panel (Lookup Student)
        lookup_frame = ctk.CTkFrame(self, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        lookup_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        sid_lbl = ctk.CTkLabel(
            lookup_frame,
            text="Enter Student ID:",
            font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            text_color="#AAAAAA"
        )
        sid_lbl.grid(row=0, column=0, padx=(20, 10), pady=15, sticky="w")

        self.sid_entry = ctk.CTkEntry(
            lookup_frame,
            placeholder_text="e.g. 1",
            width=120,
            fg_color="#181818",
            border_color="#303030",
            focused_border_color="#FF0000",
            placeholder_text_color="#717171",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=13)
        )
        self.sid_entry.grid(row=0, column=1, padx=10, pady=15, sticky="w")
        self.sid_entry.bind("<Return>", lambda e: self.load_student_assessment_history())

        search_btn = ctk.CTkButton(
            lookup_frame,
            text="Load Records",
            command=self.load_student_assessment_history,
            fg_color="#272727",
            hover_color="#333333",
            text_color="#FFFFFF",
            border_width=1,
            border_color="#3A3A3A",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold")
        )
        search_btn.grid(row=0, column=2, padx=15, pady=15, sticky="w")

        self.student_info_lbl = ctk.CTkLabel(
            lookup_frame,
            text="No student selected.",
            font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            text_color="#AAAAAA"
        )
        self.student_info_lbl.grid(row=0, column=3, padx=20, pady=15, sticky="w")

        # Left Frame: Assessment History List
        self.history_panel = ctk.CTkScrollableFrame(
            self,
            fg_color="#1A1A1A",
            border_color="#2A2A2A",
            border_width=1,
            corner_radius=12,
            label_text="TEST HISTORY LOGS",
            label_font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            label_text_color="#FFFFFF"
        )
        self.history_panel.grid(row=2, column=0, sticky="nsew", padx=(20, 10), pady=10)

        # Right Frame: Register New Grade Form
        self.form_panel = ctk.CTkFrame(self, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        self.form_panel.grid(row=2, column=1, sticky="nsew", padx=(10, 20), pady=10)
        self.form_panel.grid_columnconfigure(0, weight=1)

        form_title = ctk.CTkLabel(
            self.form_panel,
            text="ADD NEW ASSESSMENT ENTRY",
            font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            text_color="#FFFFFF"
        )
        form_title.pack(pady=(20, 15))

        # Form fields
        self.topic_var = ctk.StringVar(value="Pandas Basics")
        self.topics = [
            "Pandas Basics", "SQL SELECT", "SQL JOIN", "Data Visualization",
            "Cyber Safety", "Python Functions", "Digital Wellness",
            "Spreadsheet Skills", "AI Literacy", "Ethics in Technology"
        ]
        
        lbl_topic = ctk.CTkLabel(self.form_panel, text="Objective / Topic:", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#AAAAAA")
        lbl_topic.pack(anchor="w", padx=30, pady=(5, 2))
        
        self.topic_menu = ctk.CTkOptionMenu(
            self.form_panel,
            values=self.topics,
            variable=self.topic_var,
            width=280,
            fg_color="#181818",
            button_color="#E50914",
            button_hover_color="#CC0000",
            dropdown_fg_color="#1A1A1A",
            dropdown_text_color="#FFFFFF",
            text_color="#FFFFFF"
        )
        self.topic_menu.pack(padx=30, pady=5)

        lbl_score = ctk.CTkLabel(self.form_panel, text="Score Obtained*:", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#AAAAAA")
        lbl_score.pack(anchor="w", padx=30, pady=(10, 2))

        self.score_entry = ctk.CTkEntry(
            self.form_panel, 
            placeholder_text="e.g. 85.5", 
            width=280, 
            fg_color="#181818", 
            border_color="#303030", 
            focused_border_color="#FF0000",
            placeholder_text_color="#717171",
            text_color="#FFFFFF"
        )
        self.score_entry.pack(padx=30, pady=5)

        lbl_max = ctk.CTkLabel(self.form_panel, text="Maximum Score:", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#AAAAAA")
        lbl_max.pack(anchor="w", padx=30, pady=(10, 2))

        self.max_entry = ctk.CTkEntry(
            self.form_panel, 
            placeholder_text="Default 100", 
            width=280, 
            fg_color="#181818", 
            border_color="#303030", 
            focused_border_color="#FF0000",
            placeholder_text_color="#717171",
            text_color="#FFFFFF"
        )
        self.max_entry.pack(padx=30, pady=5)

        lbl_date = ctk.CTkLabel(self.form_panel, text="Test Date (YYYY-MM-DD)*:", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#AAAAAA")
        lbl_date.pack(anchor="w", padx=30, pady=(10, 2))

        self.date_entry = ctk.CTkEntry(
            self.form_panel, 
            placeholder_text="YYYY-MM-DD", 
            width=280, 
            fg_color="#181818", 
            border_color="#303030", 
            focused_border_color="#FF0000",
            placeholder_text_color="#717171",
            text_color="#FFFFFF"
        )
        self.date_entry.pack(padx=30, pady=5)
        self.date_entry.insert(0, datetime.date.today().isoformat())

        self.form_status_lbl = ctk.CTkLabel(
            self.form_panel,
            text="",
            font=ctk.CTkFont(family="Outfit", size=13),
            text_color="#FF0000"
        )
        self.form_status_lbl.pack(pady=10)

        save_btn = ctk.CTkButton(
            self.form_panel,
            text="SUBMIT GRADE",
            command=self.submit_grade,
            height=40,
            width=280,
            fg_color="#E50914",
            hover_color="#CC0000",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold")
        )
        save_btn.pack(pady=(5, 20))

        # State cache
        self.active_student_id = None

    def update_db_status(self):
        status = get_db_status()
        self.db_label.configure(text=status["display"])
        color = "#2ecc71" if status["backend"] == "MySQL" else "#ff9f43"
        self.db_label.configure(text_color=color)

    def load_student_assessment_history(self):
        self.update_db_status()
        
        # Clear previous list
        for w in self.history_panel.winfo_children():
            w.destroy()

        self.active_student_id = None
        self.student_info_lbl.configure(text="No student selected.", text_color="#95a5a6")

        sid_raw = self.sid_entry.get().strip()
        if not sid_raw:
            self.show_form_message("Please enter a student ID.", is_error=True)
            return

        try:
            sid = int(sid_raw)
        except ValueError:
            self.show_form_message("Student ID must be a numeric value.", is_error=True)
            return

        # Fetch student details
        res = student_service.search_students(str(sid))
        if not res:
            self.show_form_message(f"Student ID {sid} does not exist.", is_error=True)
            return
        
        student = res[0]
        self.active_student_id = sid
        self.student_info_lbl.configure(
            text=f"Active: {student['first_name']} {student['last_name']} ({student['class_section']})",
            text_color="#FFFFFF"
        )

        # Fetch diagnostic history
        logs = assessment_service.get_assessment_history(sid)
        if not logs:
            no_logs_lbl = ctk.CTkLabel(
                self.history_panel,
                text="No academic grade records found for this student.",
                font=ctk.CTkFont(family="Outfit", size=13),
                text_color="#AAAAAA"
            )
            no_logs_lbl.pack(pady=40)
            return

        # Draw columns headings
        headers_frame = ctk.CTkFrame(self.history_panel, fg_color="transparent")
        headers_frame.pack(fill="x", pady=(5, 10), padx=5)
        
        ctk.CTkLabel(headers_frame, text="Test Date", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#AAAAAA", width=95).pack(side="left")
        ctk.CTkLabel(headers_frame, text="Objective ID / Description", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#AAAAAA").pack(side="left", padx=25)
        ctk.CTkLabel(headers_frame, text="Score", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#AAAAAA", width=80).pack(side="right")

        # Roster list
        for idx, log in enumerate(logs):
            row_bg = "#1A1A1A" if idx % 2 == 0 else "#181818"
            row = ctk.CTkFrame(self.history_panel, fg_color=row_bg, height=35, corner_radius=4)
            row.pack(fill="x", pady=2, ipady=3)

            date_lbl = ctk.CTkLabel(row, text=str(log["test_date"]), font=ctk.CTkFont(family="Outfit", size=12), text_color="#FFFFFF", width=95)
            date_lbl.pack(side="left", padx=5)

            # Map index topic name if index maps
            topic_id = log["objective_id"]
            topic_name = self.topics[(topic_id - 1) % len(self.topics)] if topic_id else "General Topic"
            desc_lbl = ctk.CTkLabel(row, text=f"ID {topic_id or 0} - {topic_name}", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#FFFFFF")
            desc_lbl.pack(side="left", padx=15)

            score_str = f"{log['score_obtained']:.1f} / {log['max_score']:.1f}"
            score_lbl = ctk.CTkLabel(row, text=score_str, font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#FFFFFF", width=80)
            score_lbl.pack(side="right", padx=10)

    def submit_grade(self):
        self.update_db_status()
        
        if not self.active_student_id:
            self.show_form_message("Load a valid student profile first.", is_error=True)
            return

        topic = self.topic_var.get()
        # Derive objective_id as index + 1
        objective_id = self.topics.index(topic) + 1

        score_raw = self.score_entry.get().strip()
        max_raw = self.max_entry.get().strip() or "100"
        date_raw = self.date_entry.get().strip()

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
                self.score_entry.delete(0, "end")
                self.max_entry.delete(0, "end")
                # Reload list
                self.load_student_assessment_history()
            else:
                self.show_form_message("Database failed to record grade.", is_error=True)
        except Exception as e:
            self.show_form_message(f"Database error: {e}", is_error=True)

    def show_form_message(self, text: str, is_error: bool = False):
        color = "#e74c3c" if is_error else "#2ecc71"
        self.form_status_lbl.configure(text=text, text_color=color)
        self.after(4000, lambda: self.form_status_lbl.configure(text=""))
