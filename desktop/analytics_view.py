"""CustomTkinter panel for student predictive analytics, Learning Health Score breakdown, and actions."""

from __future__ import annotations
import customtkinter as ctk

from core import student_service, analytics, recommendation


class AnalyticsViewFrame(ctk.CTkFrame):
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
            text="PREDICTIVE STUDENT ANALYTICS & INSIGHTS",
            font=ctk.CTkFont(family="Outfit", size=24, weight="bold"),
            text_color="#FFFFFF"
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=10)

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
        self.sid_entry.bind("<Return>", lambda e: self.load_student_analytics())

        search_btn = ctk.CTkButton(
            lookup_frame,
            text="Run Analytics",
            command=self.load_student_analytics,
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

        # Left Column: LHS details, Academic, Attendance & Wellness Metrics
        self.left_scroll = ctk.CTkScrollableFrame(self, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        self.left_scroll.grid(row=2, column=0, sticky="nsew", padx=(20, 10), pady=10)

        # Right Column: Insights & Actions Checklist + Export Triggers
        self.right_scroll = ctk.CTkScrollableFrame(self, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        self.right_scroll.grid(row=2, column=1, sticky="nsew", padx=(10, 20), pady=10)

        # State Cache
        self.active_student_id = None
        self.student_summary = None

        # Build initial instructions in scroll panels
        self.draw_instruction_placeholders()

    def draw_instruction_placeholders(self):
        lbl1 = ctk.CTkLabel(
            self.left_scroll,
            text="Enter a Student ID above and click 'Run Analytics' to\nretrieve Learning Health Scores, Weekly Performance Regression\ntrends, and active risk metrics.",
            font=ctk.CTkFont(family="Outfit", size=13),
            text_color="#AAAAAA",
            justify="center"
        )
        lbl1.pack(pady=100)

        lbl2 = ctk.CTkLabel(
            self.right_scroll,
            text="AI-derived insights and personalized teacher action checklists\nwill display here.",
            font=ctk.CTkFont(family="Outfit", size=13),
            text_color="#AAAAAA",
            justify="center"
        )
        lbl2.pack(pady=100)

    def load_student_analytics(self):
        # Clear containers
        for w in self.left_scroll.winfo_children():
            w.destroy()
        for w in self.right_scroll.winfo_children():
            w.destroy()

        self.active_student_id = None
        self.student_summary = None
        self.student_info_lbl.configure(text="No student selected.", text_color="#95a5a6")

        sid_raw = self.sid_entry.get().strip()
        if not sid_raw:
            self.draw_instruction_placeholders()
            return

        try:
            sid = int(sid_raw)
        except ValueError:
            self.draw_instruction_placeholders()
            return

        # Fetch calculations
        summary = analytics.get_student_analytics_summary(sid)
        if not summary:
            self.student_info_lbl.configure(text=f"Student ID {sid} not found in database.", text_color="#e74c3c")
            self.draw_instruction_placeholders()
            return

        self.active_student_id = sid
        self.student_summary = summary
        self.student_info_lbl.configure(
            text=f"Active: {summary['student_name']} ({summary['class_section']})",
            text_color="#FFFFFF"
        )

        # BUILD LEFT PANEL: KPI METRICS
        # LHS and Risk Cards side-by-side
        top_cards = ctk.CTkFrame(self.left_scroll, fg_color="transparent")
        top_cards.pack(fill="x", padx=10, pady=10)
        top_cards.grid_columnconfigure(0, weight=1)
        top_cards.grid_columnconfigure(1, weight=1)

        # LHS Card
        lhs_card = ctk.CTkFrame(top_cards, fg_color="#212121", border_color="#2A2A2A", border_width=1, corner_radius=10, height=80)
        lhs_card.grid(row=0, column=0, padx=5, sticky="ew")
        lhs_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(lhs_card, text="LEARNING HEALTH SCORE", font=ctk.CTkFont(family="Outfit", size=10, weight="bold"), text_color="#AAAAAA").grid(row=0, column=0, pady=(10, 2))
        ctk.CTkLabel(lhs_card, text=f"{summary['learning_health_score']:.1f} / 100", font=ctk.CTkFont(family="Outfit", size=20, weight="bold"), text_color="#FFFFFF").grid(row=1, column=0, pady=(2, 10))

        # Risk Card
        risk_color = "#FF0000" if summary["risk_level"] == "HIGH" else ("#FF7A00" if summary["risk_level"] == "MEDIUM" else "#34A853")
        risk_card = ctk.CTkFrame(top_cards, fg_color="#212121", border_color="#2A2A2A", border_width=1, corner_radius=10, height=80)
        risk_card.grid(row=0, column=1, padx=5, sticky="ew")
        risk_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(risk_card, text="RISK CLASSIFICATION", font=ctk.CTkFont(family="Outfit", size=10, weight="bold"), text_color="#AAAAAA").grid(row=0, column=0, pady=(10, 2))
        ctk.CTkLabel(risk_card, text=summary["risk_level"], font=ctk.CTkFont(family="Outfit", size=20, weight="bold"), text_color=risk_color).grid(row=1, column=0, pady=(2, 10))

        # Academic Frame
        acad_frame = ctk.CTkFrame(self.left_scroll, fg_color="#181818", border_color="#2A2A2A", border_width=1, corner_radius=10)
        acad_frame.pack(fill="x", padx=10, pady=5, ipady=5)
        ctk.CTkLabel(acad_frame, text="ACADEMIC METRICS", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#FFFFFF").pack(anchor="w", padx=15, pady=(5, 5))
        
        detail_txt1 = (
            f"• Academic Quiz Average: {summary['academic_average']:.1f}% ({summary['academic_status']})\n"
            f"• Weekly Progress Trend: {summary['trend']}\n"
            f"• Regression Predicted Next Score: {summary['predicted_next_score']:.1f}%"
        )
        ctk.CTkLabel(acad_frame, text=detail_txt1, font=ctk.CTkFont(family="Outfit", size=12), text_color="#FFFFFF", justify="left").pack(anchor="w", padx=15, pady=(0, 5))

        # Attendance Frame
        att_frame = ctk.CTkFrame(self.left_scroll, fg_color="#181818", border_color="#2A2A2A", border_width=1, corner_radius=10)
        att_frame.pack(fill="x", padx=10, pady=5, ipady=5)
        ctk.CTkLabel(att_frame, text="ATTENDANCE METRICS", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#FFFFFF").pack(anchor="w", padx=15, pady=(5, 5))
        
        detail_txt2 = (
            f"• Overall Attendance Rate: {summary['attendance_percentage']:.1f}% ({summary['attendance_status']})"
        )
        ctk.CTkLabel(att_frame, text=detail_txt2, font=ctk.CTkFont(family="Outfit", size=12), text_color="#FFFFFF", justify="left").pack(anchor="w", padx=15, pady=(0, 5))

        # Cyber Wellness Frame
        well_frame = ctk.CTkFrame(self.left_scroll, fg_color="#181818", border_color="#2A2A2A", border_width=1, corner_radius=10)
        well_frame.pack(fill="x", padx=10, pady=5, ipady=5)
        ctk.CTkLabel(well_frame, text="CYBER WELLNESS METRICS", font=ctk.CTkFont(family="Outfit", size=12, weight="bold"), text_color="#FFFFFF").pack(anchor="w", padx=15, pady=(5, 5))
        
        detail_txt3 = (
            f"• Cyber Wellness Index: {summary['cyber_wellness_score']:.1f}% ({summary['wellness_status']})\n"
            f"• Daily Screen Exposure: {summary['screen_time_hours']:.1f} hours/day"
        )
        ctk.CTkLabel(well_frame, text=detail_txt3, font=ctk.CTkFont(family="Outfit", size=12), text_color="#FFFFFF", justify="left").pack(anchor="w", padx=15, pady=(0, 5))

        # BUILD RIGHT PANEL: INSIGHTS & ACTIONS
        # Explainable Insights list
        ctk.CTkLabel(
            self.right_scroll,
            text="EXPLAINABLE INSIGHTS",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=10, pady=(10, 5))

        insights = recommendation.explain_learning_insights(summary)
        for ins in insights:
            lbl_ins = ctk.CTkLabel(
                self.right_scroll,
                text=f"• {ins}",
                font=ctk.CTkFont(family="Outfit", size=12),
                text_color="#FFFFFF",
                justify="left",
                wraplength=340
            )
            lbl_ins.pack(anchor="w", padx=15, pady=2)

        # Personalized Action Items
        ctk.CTkLabel(
            self.right_scroll,
            text="TEACHER INTERVENTION CHECKLIST",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=10, pady=(15, 5))

        plan = recommendation.generate_intervention_plan(summary)
        for p in plan:
            # CustomTkinter CTkCheckBox is beautiful here!
            cb = ctk.CTkCheckBox(
                self.right_scroll,
                text=p,
                font=ctk.CTkFont(family="Outfit", size=12),
                text_color="#FFFFFF",
                border_color="#303030",
                checkmark_color="#FFFFFF",
                fg_color="#E50914"
            )
            cb.pack(anchor="w", padx=15, pady=4)

        # Report Export Utilities Frame
        export_frame = ctk.CTkFrame(self.right_scroll, fg_color="#181818", border_color="#2A2A2A", border_width=1, corner_radius=10)
        export_frame.pack(fill="x", padx=10, pady=(20, 10), ipady=5)
        
        ctk.CTkLabel(
            export_frame,
            text="REPORT EXPORT & VISUAL CHARTS",
            font=ctk.CTkFont(family="Outfit", size=11, weight="bold"),
            text_color="#AAAAAA"
        ).pack(anchor="w", padx=15, pady=(8, 5))

        self.btn_chart = ctk.CTkButton(
            export_frame,
            text="Generate Visual Matplotlib Charts",
            command=self.trigger_chart_generation,
            fg_color="#272727",
            hover_color="#333333",
            text_color="#FFFFFF",
            border_width=1,
            border_color="#3A3A3A",
            font=ctk.CTkFont(family="Outfit", size=12)
        )
        self.btn_chart.pack(fill="x", padx=15, pady=4)

        self.btn_export = ctk.CTkButton(
            export_frame,
            text="Export Report (CSV & Text)",
            command=self.trigger_report_export,
            fg_color="#E50914",
            hover_color="#CC0000",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Outfit", size=12)
        )
        self.btn_export.pack(fill="x", padx=15, pady=4)

        self.feedback_lbl = ctk.CTkLabel(
            export_frame,
            text="",
            font=ctk.CTkFont(family="Outfit", size=11),
            text_color="#2ecc71"
        )
        self.feedback_lbl.pack(pady=(2, 5))

    def trigger_chart_generation(self):
        if not self.active_student_id:
            return
        
        self.btn_chart.configure(state="disabled", text="Generating...")
        self.update()

        try:
            # Matplotlib is imported dynamically to decouple core logic and avoid delays
            from core import graphs
            
            p1 = graphs.plot_student_progress(self.active_student_id)
            p2 = graphs.plot_attendance(self.active_student_id)
            p3 = graphs.plot_cyber_wellness(self.active_student_id)
            p4 = graphs.plot_learning_health(self.active_student_id)

            self.show_feedback(f"Charts saved in root 'reports/'.")
        except Exception as e:
            self.show_feedback(f"Chart error: {e}", is_error=True)
        finally:
            self.btn_chart.configure(state="normal", text="Generate Visual Matplotlib Charts")

    def trigger_report_export(self):
        if not self.active_student_id or not self.student_summary:
            return

        self.btn_export.configure(state="disabled", text="Exporting...")
        self.update()

        try:
            from core import reports
            
            csv_path = reports.export_student_report_csv(self.active_student_id)
            
            txt_path = f"reports/student_{self.active_student_id}_report.txt"
            text_content = reports.build_student_report(self.student_summary)
            import os
            os.makedirs("reports", exist_ok=True)
            with open(txt_path, "w", encoding="utf-8") as tf:
                tf.write(text_content)

            self.show_feedback("Report CSV & Text saved under 'reports/'.")
        except Exception as e:
            self.show_feedback(f"Export error: {e}", is_error=True)
        finally:
            self.btn_export.configure(state="normal", text="Export Report (CSV & Text)")

    def show_feedback(self, text: str, is_error: bool = False):
        color = "#FF0000" if is_error else "#34A853"
        self.feedback_lbl.configure(text=text, text_color=color)
        self.after(4000, lambda: self.feedback_lbl.configure(text=""))
