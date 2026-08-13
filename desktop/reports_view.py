"""CustomTkinter panel for class-wide risk reports, teacher alerts, and CSV exports."""

from __future__ import annotations
import customtkinter as ctk

from core import reports
from core.database import get_db_status


class ReportsFrame(ctk.CTkFrame):
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
            text="CLASS REPORTS & ANALYTICS EXPORTERS",
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

        # Class Summary Stats Panel
        self.stats_panel = ctk.CTkFrame(self, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        self.stats_panel.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        for c in range(3):
            self.stats_panel.grid_columnconfigure(c, weight=1)

        self.avg_acad_lbl = self.create_metric_lbl(self.stats_panel, 0, "ACADEMIC CLASS AVG")
        self.avg_att_lbl = self.create_metric_lbl(self.stats_panel, 1, "ATTENDANCE CLASS AVG")
        self.avg_well_lbl = self.create_metric_lbl(self.stats_panel, 2, "CYBER-WELLNESS AVG")

        # Details and Exports Split
        details_frame = ctk.CTkFrame(self, fg_color="transparent")
        details_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        details_frame.grid_columnconfigure(0, weight=3)
        details_frame.grid_columnconfigure(1, weight=2)
        details_frame.grid_rowconfigure(0, weight=1)

        # Left Detail: Risk Distribution profile
        self.risk_panel = ctk.CTkFrame(details_frame, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        self.risk_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.risk_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.risk_panel,
            text="RISK DISTRIBUTION PROFILE",
            font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            text_color="#FFFFFF"
        ).grid(row=0, column=0, pady=(20, 15), sticky="w", padx=25)

        self.risk_labels = {}
        risk_types = [("LOW RISK Students", "LOW", "#34A853"), ("MEDIUM RISK Students", "MEDIUM", "#FF7A00"), ("HIGH RISK Students", "HIGH", "#FF0000")]
        for idx, (label_title, key, color) in enumerate(risk_types, start=1):
            row = ctk.CTkFrame(self.risk_panel, fg_color="#1A1A1A" if idx % 2 == 0 else "#181818", border_color="#2A2A2A", border_width=1, height=40)
            row.grid(row=idx, column=0, sticky="ew", padx=20, pady=4, ipady=4)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(row, text=label_title, font=ctk.CTkFont(family="Outfit", size=13, weight="bold"), text_color="#FFFFFF").grid(row=0, column=0, sticky="w", padx=15)
            
            cnt_lbl = ctk.CTkLabel(row, text="0", font=ctk.CTkFont(family="Outfit", size=16, weight="bold"), text_color=color)
            cnt_lbl.grid(row=0, column=1, sticky="e", padx=15)
            self.risk_labels[key] = cnt_lbl

        # Right Detail: Action buttons
        actions_panel = ctk.CTkFrame(details_frame, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        actions_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        actions_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            actions_panel,
            text="EXPORT EXPORTERS UTILITIES",
            font=ctk.CTkFont(family="Outfit", size=14, weight="bold"),
            text_color="#FFFFFF"
        ).pack(pady=(20, 20))

        self.btn_class_chart = ctk.CTkButton(
            actions_panel,
            text="Generate Class Performance Map",
            command=self.generate_class_chart,
            height=40,
            width=220,
            fg_color="#272727",
            hover_color="#333333",
            text_color="#FFFFFF",
            border_width=1,
            border_color="#3A3A3A",
            font=ctk.CTkFont(family="Outfit", size=13)
        )
        self.btn_class_chart.pack(pady=10, padx=20, fill="x")

        self.btn_class_export = ctk.CTkButton(
            actions_panel,
            text="Export Class Report (CSV & Text)",
            command=self.export_class_reports,
            height=40,
            width=220,
            fg_color="#E50914",
            hover_color="#CC0000",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Outfit", size=13)
        )
        self.btn_class_export.pack(pady=10, padx=20, fill="x")

        self.feedback_lbl = ctk.CTkLabel(
            actions_panel,
            text="",
            font=ctk.CTkFont(family="Outfit", size=13),
            text_color="#34A853"
        )
        self.feedback_lbl.pack(pady=15)

        # Load data
        self.refresh_report_data()

    def update_db_status(self):
        status = get_db_status()
        self.db_label.configure(text=status["display"])
        color = "#34A853" if status["backend"] == "MySQL" else "#FFD600"
        self.db_label.configure(text_color=color)

    def create_metric_lbl(self, parent, col, title) -> ctk.CTkLabel:
        card = ctk.CTkFrame(parent, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=10, height=80)
        card.grid(row=0, column=col, padx=10, pady=15, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(family="Outfit", size=10, weight="bold"), text_color="#AAAAAA").grid(row=0, column=0, pady=(10, 2))
        
        val_lbl = ctk.CTkLabel(card, text="0.0%", font=ctk.CTkFont(family="Outfit", size=20, weight="bold"), text_color="#FFFFFF")
        val_lbl.grid(row=1, column=0, pady=(2, 10))

        return val_lbl

    def refresh_report_data(self):
        self.update_db_status()

        # Load metrics
        summary = reports.get_class_summary_data()

        self.avg_acad_lbl.configure(text=f"{summary['avg_academic']:.1f}%")
        self.avg_att_lbl.configure(text=f"{summary['avg_attendance']:.1f}%")
        self.avg_well_lbl.configure(text=f"{summary['avg_wellness']:.1f}%")

        # Set risk numbers
        risk_dist = summary["risk_distribution"]
        for key, label in self.risk_labels.items():
            label.configure(text=str(risk_dist.get(key, 0)))

    def generate_class_chart(self):
        self.btn_class_chart.configure(state="disabled", text="Generating...")
        self.update()

        try:
            from core import graphs
            path = graphs.plot_class_performance()
            self.show_feedback("Scatter chart saved under 'reports/'.")
        except Exception as e:
            self.show_feedback(f"Chart error: {e}", is_error=True)
        finally:
            self.btn_class_chart.configure(state="normal", text="Generate Class Performance Map")

    def export_class_reports(self):
        self.btn_class_export.configure(state="disabled", text="Exporting...")
        self.update()

        try:
            csv_path = reports.export_class_report_csv()
            
            txt_path = "reports/class_report.txt"
            class_summary = reports.get_class_summary_data()
            text_content = reports.build_teacher_report(class_summary)
            import os
            os.makedirs("reports", exist_ok=True)
            with open(txt_path, "w", encoding="utf-8") as tf:
                tf.write(text_content)

            self.show_feedback("Class reports saved under 'reports/'.")
        except Exception as e:
            self.show_feedback(f"Export error: {e}", is_error=True)
        finally:
            self.btn_class_export.configure(state="normal", text="Export Class Report (CSV & Text)")

    def show_feedback(self, text: str, is_error: bool = False):
        color = "#FF0000" if is_error else "#34A853"
        self.feedback_lbl.configure(text=text, text_color=color)
        self.after(4000, lambda: self.feedback_lbl.configure(text=""))
