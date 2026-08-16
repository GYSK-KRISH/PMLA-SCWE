"""Centralized design system theme configuration for the PySide6 desktop application.

Version 1.1 — Premium Modern UI System
Design tokens are the single source of truth for colors.
All widgets should reference COLORS or use GLOBAL_STYLESHEET.
"""

# ---------------------------------------------------------------------------
# Design Tokens — single source of truth
# ---------------------------------------------------------------------------
COLORS = {
    "background":        "#080A12",
    "secondary":         "#10131D",
    "card":              "#151925",
    "card_hover":        "#1B2030",
    "text":              "#F5F7FA",
    "muted":             "#8D96A8",
    "purple":            "#7C5CFF",
    "blue":              "#4D8DFF",
    "red":               "#E5484D",
    "success":           "#30C48D",
    "warning":           "#F5A524",
    # Derived / interaction
    "border":            "rgba(255, 255, 255, 0.06)",
    "border_light":      "rgba(255, 255, 255, 0.10)",
    "red_bg":            "rgba(229, 72, 77, 0.12)",
    "purple_bg":         "rgba(124, 92, 255, 0.12)",
    "blue_bg":           "rgba(77, 141, 255, 0.12)",
    "success_bg":        "rgba(48, 196, 141, 0.12)",
    "warning_bg":        "rgba(245, 165, 36, 0.12)",
}

# ---------------------------------------------------------------------------
# Navigation item definitions — centralized for easy icon/label updates
# ---------------------------------------------------------------------------
NAV_ITEMS = [
    ("Dashboard",           "dashboard"),
    ("Student Directory",   "students"),
    ("Attendance Registry", "attendance"),
    ("Assessments & Grades","assessments"),
    ("Cyber-Wellness",      "wellness"),
    ("Predictive Analytics","analytics"),
    ("Reports & Exporters", "reports"),
    ("Interventions",       "interventions"),
    ("AI Assistant",        "ai_assistant"),
]


# ---------------------------------------------------------------------------
# Global PySide6 Stylesheet — v1.1 Premium Dark
# ---------------------------------------------------------------------------
GLOBAL_STYLESHEET = """
/* ================================================================
   BASE
   ================================================================ */
QWidget {
    background-color: #080A12;
    color: #F5F7FA;
    font-family: 'Outfit', 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #080A12;
}

/* ================================================================
   SCROLL AREAS
   ================================================================ */
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

/* ================================================================
   SCROLLBARS
   ================================================================ */
QScrollBar:vertical {
    border: none;
    background-color: #080A12;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background-color: #1F2438;
    min-height: 24px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background-color: #2B314E;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}
QScrollBar:horizontal {
    border: none;
    background-color: #080A12;
    height: 8px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background-color: #1F2438;
    min-width: 24px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #2B314E;
}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
    width: 0px;
}

/* ================================================================
   CARD FRAMES
   ================================================================ */
QFrame#CardFrame {
    background-color: #151925;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
}

QFrame#InnerCardFrame {
    background-color: #10131D;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
}

/* ================================================================
   SIDEBAR
   ================================================================ */
QFrame#Sidebar {
    background-color: #10131D;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* ================================================================
   TOP BAR
   ================================================================ */
QFrame#TopBar {
    background-color: rgba(8, 10, 18, 0.92);
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

/* ================================================================
   LABELS
   ================================================================ */
QLabel {
    background: transparent;
    border: none;
}
QLabel#SectionTitle {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #8D96A8;
    background: transparent;
    border: none;
}
QLabel#PageTitle {
    font-size: 20px;
    font-weight: 700;
    color: #F5F7FA;
    background: transparent;
    border: none;
}

/* ================================================================
   BUTTONS — Default
   ================================================================ */
QPushButton {
    background-color: #151925;
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #F5F7FA;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #1B2030;
    border-color: rgba(255, 255, 255, 0.15);
}
QPushButton:pressed {
    background-color: #10131D;
    border-color: rgba(255, 255, 255, 0.08);
}
QPushButton:disabled {
    background-color: #0D1018;
    color: #3A3F50;
    border-color: rgba(255, 255, 255, 0.03);
}
QPushButton:focus {
    border: 1px solid #7C5CFF;
    outline: none;
}

/* ================================================================
   BUTTONS — Primary (PMLA Red Accent)
   ================================================================ */
QPushButton#PrimaryButton {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #E50914, stop:1 #6E46FF
    );
    border: 1px solid rgba(255, 255, 255, 0.10);
    color: #FFFFFF;
    border-radius: 8px;
    font-weight: 700;
}
QPushButton#PrimaryButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #FF1E27, stop:1 #825CFF
    );
}
QPushButton#PrimaryButton:pressed {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #CC000C, stop:1 #5B32E6
    );
}
QPushButton#PrimaryButton:disabled {
    background: #1A1C28;
    color: #3A3F50;
    border-color: transparent;
}

/* ================================================================
   BUTTONS — Sidebar Navigation
   ================================================================ */
QPushButton#NavButton {
    background-color: transparent;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 0px;
    color: #8D96A8;
    text-align: left;
    padding: 10px 15px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton#NavButton:hover {
    background-color: rgba(255, 255, 255, 0.04);
    color: #C8CFDA;
    border-left: 3px solid rgba(255, 255, 255, 0.08);
}
QPushButton#NavButton[active="true"] {
    background-color: rgba(229, 72, 77, 0.12);
    color: #E5484D;
    font-weight: 700;
    border-left: 3px solid #E5484D;
}

/* ================================================================
   BUTTONS — Chip/Suggested
   ================================================================ */
QPushButton#ChipButton {
    background-color: rgba(124, 92, 255, 0.10);
    border: 1px solid rgba(124, 92, 255, 0.25);
    border-radius: 16px;
    color: #A084FF;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 600;
}
QPushButton#ChipButton:hover {
    background-color: rgba(124, 92, 255, 0.20);
    border-color: rgba(124, 92, 255, 0.45);
    color: #C0AAFF;
}
QPushButton#ChipButton:pressed {
    background-color: rgba(124, 92, 255, 0.30);
}

/* ================================================================
   LINE EDITS
   ================================================================ */
QLineEdit {
    background-color: #10131D;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #F5F7FA;
    padding: 8px 12px;
    selection-background-color: #7C5CFF;
    selection-color: #FFFFFF;
}
QLineEdit:focus {
    border: 1px solid #7C5CFF;
    background-color: #0E1119;
}
QLineEdit:disabled {
    background-color: #0D1018;
    color: #3A3F50;
    border-color: rgba(255, 255, 255, 0.03);
}
QLineEdit::placeholder {
    color: #4A5060;
}

/* ================================================================
   COMBO BOXES
   ================================================================ */
QComboBox {
    background-color: #10131D;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #F5F7FA;
    padding: 6px 12px;
}
QComboBox:on {
    border: 1px solid #7C5CFF;
}
QComboBox:focus {
    border: 1px solid #7C5CFF;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #8D96A8;
    width: 0;
    height: 0;
}
QComboBox QAbstractItemView {
    background-color: #10131D;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    selection-background-color: #7C5CFF;
    selection-color: #FFFFFF;
    color: #F5F7FA;
    padding: 4px;
    outline: none;
}
QComboBox QAbstractItemView::item {
    padding: 6px 12px;
    border-radius: 4px;
    min-height: 28px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #1B2030;
}

/* ================================================================
   CHECKBOXES
   ================================================================ */
QCheckBox {
    color: #F5F7FA;
    spacing: 8px;
    background: transparent;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 5px;
    background-color: #10131D;
}
QCheckBox::indicator:checked {
    background-color: #E5484D;
    border-color: #E5484D;
}
QCheckBox::indicator:unchecked:hover {
    border-color: rgba(255, 255, 255, 0.30);
}

/* ================================================================
   PROGRESS BARS
   ================================================================ */
QProgressBar {
    background-color: #10131D;
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background-color: #E5484D;
    border-radius: 4px;
}
QProgressBar#SuccessBar::chunk {
    background-color: #30C48D;
}
QProgressBar#WarningBar::chunk {
    background-color: #F5A524;
}
QProgressBar#PurpleBar::chunk {
    background-color: #7C5CFF;
}
QProgressBar#BlueBar::chunk {
    background-color: #4D8DFF;
}

/* ================================================================
   TABLE WIDGETS
   ================================================================ */
QTableWidget {
    background-color: #151925;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    gridline-color: rgba(255, 255, 255, 0.05);
    color: #F5F7FA;
    outline: none;
    selection-background-color: rgba(124, 92, 255, 0.18);
    selection-color: #F5F7FA;
}
QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
QTableWidget::item:selected {
    background-color: rgba(124, 92, 255, 0.18);
    color: #F5F7FA;
}
QTableWidget::item:hover {
    background-color: rgba(255, 255, 255, 0.03);
}
QHeaderView::section {
    background-color: #10131D;
    color: #8D96A8;
    border: none;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    padding: 8px 12px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
QHeaderView::section:first {
    border-top-left-radius: 8px;
}
QHeaderView::section:last {
    border-top-right-radius: 8px;
    border-right: none;
}

/* ================================================================
   TAB WIDGETS
   ================================================================ */
QTabWidget::pane {
    background-color: #151925;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 10px;
}
QTabWidget::tab-bar {
    alignment: left;
}
QTabBar::tab {
    background-color: transparent;
    color: #8D96A8;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 4px;
}
QTabBar::tab:hover {
    color: #C8CFDA;
    background-color: rgba(255, 255, 255, 0.03);
}
QTabBar::tab:selected {
    color: #E5484D;
    border-bottom: 2px solid #E5484D;
    background-color: rgba(229, 72, 77, 0.06);
}

/* ================================================================
   DIALOGS
   ================================================================ */
QDialog {
    background-color: #10131D;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
}
QDialog QLabel {
    background: transparent;
    border: none;
}

/* ================================================================
   TOOLTIPS
   ================================================================ */
QToolTip {
    background-color: #1B2030;
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 6px;
    color: #F5F7FA;
    font-size: 12px;
    padding: 6px 10px;
}

/* ================================================================
   SPLITTER
   ================================================================ */
QSplitter::handle {
    background-color: rgba(255, 255, 255, 0.05);
    width: 1px;
    height: 1px;
}
QSplitter::handle:hover {
    background-color: rgba(255, 255, 255, 0.12);
}

/* ================================================================
   MENUS
   ================================================================ */
QMenu {
    background-color: #10131D;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    color: #F5F7FA;
    padding: 6px;
}
QMenu::item {
    padding: 7px 20px;
    border-radius: 6px;
    font-size: 13px;
}
QMenu::item:selected {
    background-color: #1B2030;
    color: #FFFFFF;
}
QMenu::separator {
    height: 1px;
    background: rgba(255, 255, 255, 0.05);
    margin: 5px 10px;
}

/* ================================================================
   MESSAGE BOXES
   ================================================================ */
QMessageBox {
    background-color: #10131D;
    color: #F5F7FA;
}
QMessageBox QPushButton {
    min-width: 80px;
}

/* ================================================================
   SPIN BOX
   ================================================================ */
QSpinBox, QDoubleSpinBox {
    background-color: #10131D;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #F5F7FA;
    padding: 6px 10px;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #7C5CFF;
}

/* ================================================================
   DATE EDIT
   ================================================================ */
QDateEdit {
    background-color: #10131D;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #F5F7FA;
    padding: 6px 10px;
}
QDateEdit:focus {
    border: 1px solid #7C5CFF;
}
QCalendarWidget QWidget {
    background-color: #10131D;
    color: #F5F7FA;
}

/* ================================================================
   TEXT EDIT / PLAIN TEXT EDIT
   ================================================================ */
QTextEdit, QPlainTextEdit {
    background-color: #10131D;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #F5F7FA;
    padding: 8px;
    selection-background-color: #7C5CFF;
}
QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #7C5CFF;
}

/* ================================================================
   GROUP BOX
   ================================================================ */
QGroupBox {
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    margin-top: 14px;
    font-weight: 700;
    font-size: 11px;
    color: #8D96A8;
    letter-spacing: 0.5px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    top: -2px;
    padding: 0 6px;
    background-color: #10131D;
    color: #8D96A8;
}
"""
