"""Application constants for PMLA-SCWE.

Centralizes threshold constants, risk scoring weights, attendance translations,
and early warning notification definitions for the Explainable Learning Risk Engine.
"""

# Attendance states
PRESENT = "P"
ABSENT = "A"

# Presentation translations
ATTENDANCE_STATUS_MAP = {
    PRESENT: "Present",
    ABSENT: "Absent",
}

REVERSE_ATTENDANCE_STATUS_MAP = {
    "Present": PRESENT,
    "Absent": ABSENT,
}

# ---------------------------------------------------------------------------
# Threshold Constants (Configurable Reference Benchmarks)
# ---------------------------------------------------------------------------

# Academic Performance Thresholds (%)
ACADEMIC_EXCELLENT = 85.0
ACADEMIC_SATISFACTORY = 60.0
ACADEMIC_CRITICAL = 50.0

# Attendance Thresholds (%)
ATTENDANCE_SATISFACTORY = 85.0
ATTENDANCE_MINIMUM_CBSE = 75.0

# Learning Health Score (LHS) Thresholds (0-100)
LHS_OPTIMAL = 75.0
LHS_MONITOR = 60.0
LHS_CRITICAL = 50.0

# Cyber-Wellbeing & Screen Exposure Thresholds
MAX_HEALTHY_DAILY_SCREEN_HOURS = 6.0
MIN_HEALTHY_SLEEP_HOURS = 6.5
WELLNESS_CONCERN_THRESHOLD = 55.0
WELLNESS_OPTIMAL_THRESHOLD = 80.0

# ---------------------------------------------------------------------------
# Transparent Multi-Factor Risk Scoring Constants
# Total Max Risk Score = 100 points (0 = zero risk, 100 = critical risk)
# ---------------------------------------------------------------------------
MAX_ACADEMIC_RISK_POINTS = 35
MAX_ATTENDANCE_RISK_POINTS = 30
MAX_TREND_RISK_POINTS = 15
MAX_WELLNESS_RISK_POINTS = 10
MAX_LHS_RISK_POINTS = 10

# Risk Level Classification Cutoffs
RISK_SCORE_HIGH_THRESHOLD = 70
RISK_SCORE_MEDIUM_THRESHOLD = 35

# Risk Level Labels
RISK_LEVEL_LOW = "LOW"
RISK_LEVEL_MEDIUM = "MEDIUM"
RISK_LEVEL_HIGH = "HIGH"
RISK_LEVEL_INSUFFICIENT = "INSUFFICIENT DATA"

# Performance Trajectory Classifications
TRAJECTORY_IMPROVING = "IMPROVING"
TRAJECTORY_STABLE = "STABLE"
TRAJECTORY_DECLINING = "DECLINING"
TRAJECTORY_INSUFFICIENT = "INSUFFICIENT DATA"

# Regression Slope Sensitivity Cutoff (pts / week)
SLOPE_IMPROVING_THRESHOLD = 0.15
SLOPE_DECLINING_THRESHOLD = -0.15

# Early Warning Codes
WARN_ACADEMIC = "ACADEMIC_WARNING"
WARN_ATTENDANCE = "ATTENDANCE_WARNING"
WARN_DECLINE = "PERFORMANCE_DECLINE"
WARN_CONSISTENCY = "CONSISTENCY_WARNING"
WARN_MULTI_FACTOR = "MULTI_FACTOR_HIGH_RISK"
