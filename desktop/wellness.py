"""CustomTkinter panel for lodging cyber audits and showing digital distraction/screen logs."""

from __future__ import annotations
import datetime
import customtkinter as ctk

from core import student_service, wellness_service
from core.database import get_db_status


class WellnessFrame(ctk.CTkFrame):
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
            text="STUDENT CYBER WELLNESS AUDIT",
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

        # Selection Control Panel
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
        self.sid_entry.bind("<Return>", lambda e: self.load_student_wellness_history())

        search_btn = ctk.CTkButton(
            lookup_frame,
            text="Load Records",
            command=self.load_student_wellness_history,
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

        # Left Frame: Audit History Logs
        self.history_panel = ctk.CTkScrollableFrame(
            self,
            fg_color="#1A1A1A",
            border_color="#2A2A2A",
            border_width=1,
            corner_radius=12,
            label_text="CYBER AUDIT HISTORY LOGS",
            label_font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            label_text_color="#FFFFFF"
        )
        self.history_panel.grid(row=2, column=0, sticky="nsew", padx=(20, 10), pady=10)

        # Right Frame: New Audit Form Panel
        self.form_panel = ctk.CTkFrame(self, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        self.form_panel.grid(row=2, column=1, sticky="nsew", padx=(10, 20), pady=10)
        self.form_panel.grid_columnconfigure(0, weight=1)

        form_title = ctk.CTkLabel(
            self.form_panel,
            text="SUBMIT NEW CYBER AUDIT",
            font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            text_color="#FFFFFF"
        )
        form_title.pack(pady=(15, 10))

        # Form Fields Frame
        form_fields_frame = ctk.CTkScrollableFrame(self.form_panel, fg_color="transparent", height=320)
        form_fields_frame.pack(fill="both", expand=True, padx=20)
        form_fields_frame.grid_columnconfigure(0, weight=1)
        form_fields_frame.grid_columnconfigure(1, weight=1)

        # 1. Screen time fields
        ctk.CTkLabel(form_fields_frame, text="Daily Screen Time (hrs)*:", font=ctk.CTkFont(family="Outfit", size=11, weight="bold"), text_color="#AAAAAA").grid(row=0, column=0, sticky="w", pady=4)
        self.daily_entry = ctk.CTkEntry(form_fields_frame, placeholder_text="Study + Rec", width=120, fg_color="#181818", border_color="#303030", focused_border_color="#FF0000", placeholder_text_color="#717171", text_color="#FFFFFF")
        self.daily_entry.grid(row=0, column=1, sticky="e", pady=4)

        ctk.CTkLabel(form_fields_frame, text="Study Screen Time (hrs)*:", font=ctk.CTkFont(family="Outfit", size=11, weight="bold"), text_color="#AAAAAA").grid(row=1, column=0, sticky="w", pady=4)
        self.study_entry = ctk.CTkEntry(form_fields_frame, placeholder_text="e.g. 3.5", width=120, fg_color="#181818", border_color="#303030", focused_border_color="#FF0000", placeholder_text_color="#717171", text_color="#FFFFFF")
        self.study_entry.grid(row=1, column=1, sticky="e", pady=4)

        ctk.CTkLabel(form_fields_frame, text="Recreational Screen (hrs)*:", font=ctk.CTkFont(family="Outfit", size=11, weight="bold"), text_color="#AAAAAA").grid(row=2, column=0, sticky="w", pady=4)
        self.rec_entry = ctk.CTkEntry(form_fields_frame, placeholder_text="e.g. 1.5", width=120, fg_color="#181818", border_color="#303030", focused_border_color="#FF0000", placeholder_text_color="#717171", text_color="#FFFFFF")
        self.rec_entry.grid(row=2, column=1, sticky="e", pady=4)

        # 2. Sleep fields
        ctk.CTkLabel(form_fields_frame, text="Sleep Duration (hrs)*:", font=ctk.CTkFont(family="Outfit", size=11, weight="bold"), text_color="#AAAAAA").grid(row=3, column=0, sticky="w", pady=4)
        self.sleep_entry = ctk.CTkEntry(form_fields_frame, placeholder_text="e.g. 8.0", width=120, fg_color="#181818", border_color="#303030", focused_border_color="#FF0000", placeholder_text_color="#717171", text_color="#FFFFFF")
        self.sleep_entry.grid(row=3, column=1, sticky="e", pady=4)

        # 3. Distraction slider/segmented (1-5)
        ctk.CTkLabel(form_fields_frame, text="Digital Distraction (1-5)*:", font=ctk.CTkFont(family="Outfit", size=11, weight="bold"), text_color="#AAAAAA").grid(row=4, column=0, sticky="w", pady=4)
        self.distract_opt = ctk.CTkOptionMenu(
            form_fields_frame, 
            values=["1", "2", "3", "4", "5"], 
            width=120, 
            fg_color="#181818", 
            button_color="#E50914", 
            button_hover_color="#CC0000",
            dropdown_fg_color="#1A1A1A",
            dropdown_text_color="#FFFFFF",
            text_color="#FFFFFF"
        )
        self.distract_opt.grid(row=4, column=1, sticky="e", pady=4)

        # 4. Safety awareness slider/segmented (1-5)
        ctk.CTkLabel(form_fields_frame, text="Cyber Safety (1-5)*:", font=ctk.CTkFont(family="Outfit", size=11, weight="bold"), text_color="#AAAAAA").grid(row=5, column=0, sticky="w", pady=4)
        self.safety_opt = ctk.CTkOptionMenu(
            form_fields_frame, 
            values=["1", "2", "3", "4", "5"], 
            width=120, 
            fg_color="#181818", 
            button_color="#E50914", 
            button_hover_color="#CC0000",
            dropdown_fg_color="#1A1A1A",
            dropdown_text_color="#FFFFFF",
            text_color="#FFFFFF"
        )
        self.safety_opt.set("5")
        self.safety_opt.grid(row=5, column=1, sticky="e", pady=4)

        # 5. Remarks & Date
        ctk.CTkLabel(form_fields_frame, text="Remarks:", font=ctk.CTkFont(family="Outfit", size=11, weight="bold"), text_color="#AAAAAA").grid(row=6, column=0, sticky="w", pady=4)
        self.remarks_entry = ctk.CTkEntry(form_fields_frame, placeholder_text="e.g. Balanced logs", width=120, fg_color="#181818", border_color="#303030", focused_border_color="#FF0000", placeholder_text_color="#717171", text_color="#FFFFFF")
        self.remarks_entry.grid(row=6, column=1, sticky="e", pady=4)

        ctk.CTkLabel(form_fields_frame, text="Audit Date (YYYY-MM-DD):", font=ctk.CTkFont(family="Outfit", size=11, weight="bold"), text_color="#AAAAAA").grid(row=7, column=0, sticky="w", pady=4)
        self.date_entry = ctk.CTkEntry(form_fields_frame, placeholder_text="YYYY-MM-DD", width=120, fg_color="#181818", border_color="#303030", focused_border_color="#FF0000", placeholder_text_color="#717171", text_color="#FFFFFF")
        self.date_entry.grid(row=7, column=1, sticky="e", pady=4)
        self.date_entry.insert(0, datetime.date.today().isoformat())

        self.form_status_lbl = ctk.CTkLabel(
            self.form_panel,
            text="",
            font=ctk.CTkFont(family="Outfit", size=12),
            text_color="#FF0000"
        )
        self.form_status_lbl.pack(pady=5)

        save_btn = ctk.CTkButton(
            self.form_panel,
            text="SUBMIT AUDIT",
            command=self.submit_cyber_audit,
            height=38,
            width=280,
            fg_color="#E50914",
            hover_color="#CC0000",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold")
        )
        save_btn.pack(pady=(5, 15))

        self.active_student_id = None

    def update_db_status(self):
        status = get_db_status()
        self.db_label.configure(text=status["display"])
        color = "#2ecc71" if status["backend"] == "MySQL" else "#ff9f43"
        self.db_label.configure(text_color=color)

    def load_student_wellness_history(self):
        self.update_db_status()
        
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

        history = wellness_service.get_student_audits(sid)
        if not history:
            no_logs = ctk.CTkLabel(
                self.history_panel,
                text="No cyber wellness audits lodged for this student.",
                font=ctk.CTkFont(family="Outfit", size=13),
                text_color="#AAAAAA"
            )
            no_logs.pack(pady=40)
            return

        for idx, audit in enumerate(history):
            card = ctk.CTkFrame(self.history_panel, fg_color="#181818" if idx % 2 == 0 else "#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=8)
            card.pack(fill="x", pady=4, ipady=6, padx=5)

            # Date line
            top_line = ctk.CTkFrame(card, fg_color="transparent")
            top_line.pack(fill="x", padx=10, pady=(2, 5))
            
            date_lbl = ctk.CTkLabel(top_line, text=f"Date: {audit['audit_date']}", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#FFFFFF")
            date_lbl.pack(side="left")

            score_lbl = ctk.CTkLabel(top_line, text=f"Wellness Index: {audit['wellness_score'] or 0.0:.1f}%", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#34A853")
            score_lbl.pack(side="right")

            # Metrics
            metrics_lbl = ctk.CTkLabel(
                card,
                text=f"Screen: {audit['daily_screen_time']:.1f}h (Study: {audit['study_screen_time']:.1f}h / Rec: {audit['recreational_screen_time']:.1f}h)  |  Sleep: {audit['sleep_duration']:.1f}h\nDistraction: {audit['digital_distraction_level']}/5  |  Safety Awareness: {audit['cyber_safety_awareness']}/5",
                font=ctk.CTkFont(family="Outfit", size=11),
                text_color="#FFFFFF",
                justify="left"
            )
            metrics_lbl.pack(anchor="w", padx=10, pady=2)

            if audit.get("remarks"):
                rem_lbl = ctk.CTkLabel(card, text=f"Remarks: {audit['remarks']}", font=ctk.CTkFont(family="Outfit", size=11), text_color="#AAAAAA")
                rem_lbl.pack(anchor="w", padx=10, pady=(2, 2))

    def submit_cyber_audit(self):
        self.update_db_status()
        
        if not self.active_student_id:
            self.show_form_message("Load a student profile first.", is_error=True)
            return

        daily_raw = self.daily_entry.get().strip()
        study_raw = self.study_entry.get().strip()
        rec_raw = self.rec_entry.get().strip()
        sleep_raw = self.sleep_entry.get().strip()
        distract_raw = self.distract_opt.get()
        safety_raw = self.safety_opt.get()
        remarks_val = self.remarks_entry.get().strip() or None
        date_raw = self.date_entry.get().strip()

        if not daily_raw or not study_raw or not rec_raw or not sleep_raw or not date_raw:
            self.show_form_message("Please fill in all mandatory fields.", is_error=True)
            return

        try:
            daily = float(daily_raw)
            study = float(study_raw)
            rec = float(rec_raw)
            sleep = float(sleep_raw)
            distract = int(distract_raw)
            safety = int(safety_raw)
        except ValueError:
            self.show_form_message("Check numeric fields for invalid input formats.", is_error=True)
            return

        # Prepare payload
        payload = {
            "student_id": self.active_student_id,
            "daily_screen_time": daily,
            "study_screen_time": study,
            "recreational_screen_time": rec,
            "sleep_duration": sleep,
            "digital_distraction_level": distract,
            "cyber_safety_awareness": safety,
            "remarks": remarks_val,
            "audit_date": date_raw
        }

        # Run validations
        errors = wellness_service.validate_audit_data(payload)
        if errors:
            self.show_form_message(errors[0], is_error=True)
            return

        try:
            if wellness_service.add_cyber_audit(payload):
                from core.database import log_activity
                log_activity(f"Cyber wellness audit completed for Student ID {self.active_student_id}")
                self.show_form_message("Wellness audit saved successfully!", is_error=False)
                # Clear fields
                self.daily_entry.delete(0, "end")
                self.study_entry.delete(0, "end")
                self.rec_entry.delete(0, "end")
                self.sleep_entry.delete(0, "end")
                self.remarks_entry.delete(0, "end")
                # Reload list
                self.load_student_wellness_history()
            else:
                self.show_form_message("Database failed to insert audit record.", is_error=True)
        except Exception as e:
            self.show_form_message(f"Database error: {e}", is_error=True)

    def show_form_message(self, text: str, is_error: bool = False):
        color = "#e74c3c" if is_error else "#2ecc71"
        self.form_status_lbl.configure(text=text, text_color=color)
        self.after(4000, lambda: self.form_status_lbl.configure(text=""))
