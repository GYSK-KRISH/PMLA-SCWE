"""Flask blueprint routing class reports, charts triggering, and exports."""

from __future__ import annotations
import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, send_file

from core import reports
from core.database import get_db_status

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports")
def view_reports():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    db_status = get_db_status()
    summary = reports.get_class_summary_data()

    return render_template(
        "reports.html",
        active_tab="reports",
        db_status=db_status,
        summary=summary
    )


@reports_bp.route("/reports/generate_chart", methods=["POST"])
def generate_chart():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    try:
        from core import graphs
        chart_path = graphs.plot_class_performance()
        # Returns web path relative to static/
        # Check if the chart was successfully generated under dynamic location
        if os.path.exists(chart_path):
            return jsonify({"success": True, "message": "Scatter chart generated successfully!", "path": "/" + chart_path})
        return jsonify({"success": False, "message": "Chart file not found after generation."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Chart error: {e}"}), 500


@reports_bp.route("/reports/export/csv", methods=["GET"])
def export_csv():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    try:
        csv_path = reports.export_class_report_csv()
        if os.path.exists(csv_path):
            return send_file(os.path.abspath(csv_path), as_attachment=True, download_name="class_report.csv")
        return "File not found", 404
    except Exception as e:
        return f"Error: {e}", 500


@reports_bp.route("/reports/export/txt", methods=["GET"])
def export_txt():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    try:
        class_summary = reports.get_class_summary_data()
        text_content = reports.build_teacher_report(class_summary)
        
        txt_path = "reports/class_report.txt"
        os.makedirs("reports", exist_ok=True)
        with open(txt_path, "w", encoding="utf-8") as tf:
            tf.write(text_content)
            
        if os.path.exists(txt_path):
            return send_file(os.path.abspath(txt_path), as_attachment=True, download_name="class_report.txt")
        return "File not found", 404
    except Exception as e:
        return f"Error: {e}", 500
