"""Graph generation module using Matplotlib for PDF and offline reports."""

from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .database import execute_select
from .analytics import get_student_analytics_summary


# Styling configurations matching premium aesthetics
PRIMARY_COLOR = "#E50914"     # Button red
SECONDARY_COLOR = "#FF7A00"   # Soft orange / Medium risk
SUCCESS_COLOR = "#34A853"     # Emerald green / Low risk
DANGER_COLOR = "#FF0000"      # Red / Danger
NEUTRAL_COLOR = "#AAAAAA"     # Gray
GRID_COLOR = "#2A2A2A"

# Global Matplotlib rcParams for dark theme
plt.rcParams['figure.facecolor'] = '#1A1A1A'
plt.rcParams['axes.facecolor'] = '#1A1A1A'
plt.rcParams['axes.edgecolor'] = '#2A2A2A'
plt.rcParams['text.color'] = '#E5E5E5'
plt.rcParams['axes.labelcolor'] = '#E5E5E5'
plt.rcParams['xtick.color'] = '#AAAAAA'
plt.rcParams['ytick.color'] = '#AAAAAA'
plt.rcParams['grid.color'] = '#2A2A2A'
plt.rcParams['legend.facecolor'] = '#1A1A1A'
plt.rcParams['legend.edgecolor'] = '#2A2A2A'


def _create_placeholder_chart(title: str, text: str, filepath: str) -> None:
    """Helper to generate a clean placeholder chart when data is missing."""
    plt.figure(figsize=(6, 4), dpi=100)
    plt.text(0.5, 0.5, text, ha="center", va="center", fontsize=14, color="#AAAAAA", weight="bold")
    plt.title(title, fontsize=12, color="#FFFFFF", weight="bold")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.gca().axis("off")
    plt.tight_layout()
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    plt.savefig(filepath, format="png")
    plt.close()


def plot_student_progress(student_id: int) -> str:
    """Generates and saves the student academic progress trend graph."""
    filepath = f"reports/student_{student_id}_progress.png"
    os.makedirs("reports", exist_ok=True)

    rows = execute_select(
        "SELECT week_start, score FROM Weekly_Progress WHERE student_id = %s ORDER BY week_start ASC",
        (student_id,)
    )
    if not rows:
        _create_placeholder_chart("Academic Score Trend", "No Progress Data Available", filepath)
        return filepath

    weeks = [str(r["week_start"]) for r in rows]
    scores = [float(r["score"]) for r in rows]

    plt.figure(figsize=(7, 4), dpi=100)
    plt.plot(weeks, scores, marker="o", color=PRIMARY_COLOR, linewidth=2, markersize=6, label="Weekly Score")
    plt.fill_between(weeks, scores, alpha=0.1, color=PRIMARY_COLOR)
    
    plt.title("Academic Weekly Progress Trend", fontsize=12, fontweight="bold", pad=15)
    plt.xlabel("Week Start Date", fontsize=10)
    plt.ylabel("Score (%)", fontsize=10)
    plt.ylim(0, 105)
    plt.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR)
    plt.xticks(rotation=15, ha="right", fontsize=9)
    plt.tight_layout()
    plt.savefig(filepath, format="png")
    plt.close()
    return filepath


def plot_attendance(student_id: int) -> str:
    """Generates and saves the student attendance pie/donut chart."""
    filepath = f"reports/student_{student_id}_attendance.png"
    os.makedirs("reports", exist_ok=True)

    rows = execute_select(
        "SELECT status, COUNT(*) as cnt FROM Attendance WHERE student_id = %s GROUP BY status",
        (student_id,)
    )
    if not rows:
        _create_placeholder_chart("Attendance Distribution", "No Attendance Data Available", filepath)
        return filepath

    status_counts = {"P": 0, "A": 0}
    for r in rows:
        status_counts[r["status"]] = int(r["cnt"])

    labels = ["Present", "Absent"]
    sizes = [status_counts["P"], status_counts["A"]]
    colors = [SUCCESS_COLOR, DANGER_COLOR]

    if sum(sizes) == 0:
        _create_placeholder_chart("Attendance Distribution", "No Attendance Records Found", filepath)
        return filepath

    plt.figure(figsize=(5, 4), dpi=100)
    wedges, texts, autotexts = plt.pie(
        sizes, labels=labels, autopct="%1.1f%%", startangle=90,
        colors=colors, textprops=dict(color="#E5E5E5"),
        wedgeprops=dict(width=0.4, edgecolor="#1A1A1A", linewidth=2)
    )
    
    plt.setp(autotexts, size=9, weight="bold")
    plt.setp(texts, size=10)
    plt.title("Attendance Distribution Profile", fontsize=12, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(filepath, format="png")
    plt.close()
    return filepath


def plot_cyber_wellness(student_id: int) -> str:
    """Generates and saves a dual-axis cyber wellness analysis chart."""
    filepath = f"reports/student_{student_id}_wellness.png"
    os.makedirs("reports", exist_ok=True)

    rows = execute_select(
        "SELECT audit_date, daily_screen_time, study_screen_time, recreational_screen_time, wellness_score "
        "FROM Cyber_Audit WHERE student_id = %s ORDER BY audit_date ASC",
        (student_id,)
    )
    if not rows:
        _create_placeholder_chart("Cyber Wellness Analysis", "No Cyber Wellness Audit Data Available", filepath)
        return filepath

    dates = [str(r["audit_date"]) for r in rows]
    daily = [float(r["daily_screen_time"]) for r in rows]
    study = [float(r["study_screen_time"]) for r in rows]
    recreational = [float(r["recreational_screen_time"]) for r in rows]
    scores = [float(r["wellness_score"]) for r in rows]

    fig, ax1 = plt.subplots(figsize=(8, 4), dpi=100)

    # Bar chart for screen times
    x = range(len(dates))
    width = 0.25
    ax1.bar([i - width for i in x], study, width, label="Study Screen Time", color="#3EA6FF")
    ax1.bar(x, recreational, width, label="Recreational Screen Time", color="#FF7A00")
    ax1.bar([i + width for i in x], daily, width, label="Total Screen Time", color="#717171", alpha=0.6)
    
    ax1.set_xlabel("Audit Date", fontsize=10)
    ax1.set_ylabel("Screen Time (Hours)", fontsize=10)
    ax1.set_ylim(0, 24)
    ax1.set_xticks(x)
    ax1.set_xticklabels(dates, rotation=15, ha="right", fontsize=9)
    ax1.grid(True, linestyle="--", alpha=0.3, color=GRID_COLOR)
    ax1.legend(loc="upper left", fontsize=8)

    # Line chart for wellness score on secondary axis
    ax2 = ax1.twinx()
    ax2.plot(dates, scores, color="#34A853", marker="D", linewidth=2.5, markersize=6, label="Wellness Index")
    ax2.set_ylabel("Wellness Index (%)", fontsize=10, color="#34A853")
    ax2.tick_params(axis="y", labelcolor="#34A853")
    ax2.set_ylim(0, 105)
    ax2.legend(loc="upper right", fontsize=8)

    plt.title("Cyber-Wellness & Screen Time Overview", fontsize=12, fontweight="bold", pad=15)
    fig.tight_layout()
    plt.savefig(filepath, format="png")
    plt.close()
    return filepath


def plot_learning_health(student_id: int) -> str:
    """Generates a bar chart showing the breakdown of components of Learning Health Score."""
    filepath = f"reports/student_{student_id}_learning_health.png"
    os.makedirs("reports", exist_ok=True)

    summary = get_student_analytics_summary(student_id)
    if not summary:
        _create_placeholder_chart("Learning Health Breakdown", "Student Record Not Found", filepath)
        return filepath

    # Components and weights
    components = [
        "Academic Avg\n(40%)",
        "Weekly Progress\n(25%)",
        "Attendance\n(20%)",
        "Cyber Wellness\n(15%)"
    ]
    scores = [
        summary["academic_average"],
        summary["weekly_progress"],
        summary["attendance_percentage"],
        summary["cyber_wellness_score"]
    ]
    colors = [PRIMARY_COLOR, SECONDARY_COLOR, SUCCESS_COLOR, "#3EA6FF"]

    plt.figure(figsize=(7, 4), dpi=100)
    bars = plt.barh(components, scores, color=colors, height=0.5, edgecolor="none")
    
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 2, bar.get_y() + bar.get_height()/2, f"{width:.1f}%", 
                 ha="left", va="center", fontsize=9, fontweight="bold", color="#E5E5E5")

    plt.title(f"Learning Health Score Breakdown (Total: {summary['learning_health_score']:.1f}%)", 
              fontsize=12, fontweight="bold", pad=15)
    plt.xlabel("Component Score (%)", fontsize=10)
    plt.xlim(0, 115)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(filepath, format="png")
    plt.close()
    return filepath


def plot_class_performance() -> str:
    """Generates and saves a scatter plot of Class Performance vs Wellness Scores."""
    filepath = "reports/class_performance_scatter.png"
    os.makedirs("reports", exist_ok=True)

    rows = execute_select("SELECT student_id FROM Students")
    if not rows:
        _create_placeholder_chart("Class Performance Matrix", "No Student Records Found", filepath)
        return filepath

    academics = []
    wellness = []
    healths = []

    for r in rows:
        summary = get_student_analytics_summary(r["student_id"])
        if not summary:
            continue
        academics.append(summary["academic_average"])
        wellness.append(summary["cyber_wellness_score"])
        healths.append(summary["learning_health_score"])

    if not academics:
        _create_placeholder_chart("Class Performance Matrix", "No Analytical Data Compiles", filepath)
        return filepath

    plt.figure(figsize=(7, 4.5), dpi=100)
    scatter = plt.scatter(
        wellness, academics, c=healths, cmap="plasma", 
        s=100, alpha=0.8, edgecolors="none"
    )
    cbar = plt.colorbar(scatter)
    cbar.set_label("Learning Health Score (%)", fontsize=10)
    
    plt.title("Class Academic Performance vs. Cyber-Wellness Map", fontsize=12, fontweight="bold", pad=15)
    plt.xlabel("Cyber Wellness Score (%)", fontsize=10)
    plt.ylabel("Academic Average Score (%)", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.4, color=GRID_COLOR)
    plt.tight_layout()
    plt.savefig(filepath, format="png")
    plt.close()
    return filepath


def plot_class_performance_trend() -> str:
    """Generates and saves the class-wide academic progress trend chart."""
    filepath = "reports/class_performance_trend.png"
    os.makedirs("reports", exist_ok=True)

    rows = execute_select(
        "SELECT week_start, AVG(score) as avg_score FROM Weekly_Progress GROUP BY week_start ORDER BY week_start ASC"
    )
    if not rows:
        _create_placeholder_chart("Class Performance Trend", "No Progress Data Available", filepath)
        return filepath

    weeks = [str(r["week_start"]) for r in rows]
    scores = [float(r["avg_score"]) for r in rows]

    plt.figure(figsize=(6, 3.5), dpi=100)
    plt.plot(weeks, scores, marker="s", color=PRIMARY_COLOR, linewidth=2.5, markersize=6, label="Class Avg")
    plt.fill_between(weeks, scores, alpha=0.1, color=PRIMARY_COLOR)
    
    plt.title("Class Academic Performance Trend", fontsize=11, fontweight="bold", pad=12)
    plt.xlabel("Week Start Date", fontsize=9)
    plt.ylabel("Average Score (%)", fontsize=9)
    plt.ylim(0, 105)
    plt.grid(True, linestyle="--", alpha=0.3, color=GRID_COLOR)
    plt.xticks(rotation=15, ha="right", fontsize=8)
    plt.tight_layout()
    plt.savefig(filepath, format="png")
    plt.close()
    return filepath
