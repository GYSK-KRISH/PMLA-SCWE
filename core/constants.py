"""Application constants for PMLA-SCWE."""

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
