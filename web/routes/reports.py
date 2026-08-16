"""Flask blueprint routing professional report generation, live preview, PDF, and CSV downloads."""

from __future__ import annotations
import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, send_file

from core import report_service, student_service, reports
from core.database import get_db_status

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports")
def view_reports():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    db_status = get_db_status()
    summary = reports.get_class_summary_data()
    students = student_service.get_all_students()

    return render_template(
        "reports.html",
        active_tab="reports",
        db_status=db_status,
        summary=summary,
        students=students,
        report_types=report_service.REPORT_TYPES
    )


@reports_bp.route("/reports/preview", methods=["POST"])
def preview_report():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    data = request.get_json() or {}
    rtype = data.get("report_type", report_service.REPORT_TYPE_STUDENT_INTELLIGENCE)
    sid_raw = data.get("student_id")
    sid = int(sid_raw) if sid_raw and str(sid_raw).isdigit() else None
    c_name = data.get("class_name", "All")
    sec = data.get("section", "All")

    try:
        preview_text = report_service.generate_report_preview_text(
            report_type=rtype,
            student_id=sid,
            class_name=c_name,
            section=sec,
            options=data.get("options", {})
        )
        return jsonify({"success": True, "preview": preview_text})
    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 500


@reports_bp.route("/reports/export/pdf", methods=["GET"])
def export_pdf():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    rtype = request.args.get("report_type", report_service.REPORT_TYPE_STUDENT_INTELLIGENCE)
    sid_raw = request.args.get("student_id", "").strip()
    sid = int(sid_raw) if sid_raw.isdigit() else None
    c_name = request.args.get("class_name", "All").strip()
    sec = request.args.get("section", "All").strip()
    include_ai = request.args.get("include_ai_summary", "1") == "1"

    options = {
        "include_metrics": True,
        "include_charts": True,
        "include_risk_factors": True,
        "include_interventions": True,
        "include_ai_summary": include_ai
    }

    try:
        os.makedirs("reports", exist_ok=True)
        if rtype == report_service.REPORT_TYPE_STUDENT_INTELLIGENCE and sid:
            pdf_path = report_service.generate_student_pdf_report(student_id=sid, options=options)
            download_name = f"Student_Report_{sid}.pdf"
        else:
            pdf_path = report_service.generate_class_pdf_report(class_name=c_name, section=sec, options=options)
            download_name = f"Class_Report_{c_name}_{sec}.pdf"

        if os.path.exists(pdf_path):
            return send_file(os.path.abspath(pdf_path), as_attachment=True, download_name=download_name)
        return "PDF file could not be located.", 404
    except Exception as exc:
        return f"PDF Generation Error: {exc}", 500


@reports_bp.route("/reports/export/csv", methods=["GET"])
def export_csv():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))

    rtype = request.args.get("report_type", report_service.REPORT_TYPE_CLASS_PERFORMANCE)
    sid_raw = request.args.get("student_id", "").strip()
    sid = int(sid_raw) if sid_raw.isdigit() else None
    c_name = request.args.get("class_name", "All").strip()
    sec = request.args.get("section", "All").strip()

    try:
        csv_path = report_service.export_report_csv(
            report_type=rtype,
            class_name=c_name,
            section=sec,
            student_id=sid
        )
        if os.path.exists(csv_path):
            filename = f"student_{sid}_data.csv" if sid else f"class_{c_name}_{sec}_report.csv"
            return send_file(os.path.abspath(csv_path), as_attachment=True, download_name=filename)
        return "CSV file not found", 404
    except Exception as exc:
        return f"CSV Export Error: {exc}", 500


@reports_bp.route("/reports/export/txt", methods=["GET"])
def export_txt():
    """Legacy text report download."""
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
    except Exception as exc:
        return f"Error: {exc}", 500


@reports_bp.route("/reports/generate_chart", methods=["POST"])
def generate_chart():
    if not session.get("logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    try:
        from core import graphs
        chart_path = graphs.plot_class_performance()
        if os.path.exists(chart_path):
            return jsonify({"success": True, "message": "Performance chart generated successfully!", "path": "/" + chart_path})
        return jsonify({"success": False, "message": "Chart file not found after generation."})
    except Exception as exc:
        return jsonify({"success": False, "message": f"Chart error: {exc}"}), 500
