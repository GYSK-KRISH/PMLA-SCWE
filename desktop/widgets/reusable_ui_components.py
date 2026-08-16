"""Reusable UI component library for PMLA-SCWE PySide6 Desktop Application.

Version 1.1 — Premium Modern UI System

Components:
    SectionHeader        — Section title with optional subtitle and right badge
    StatusBadge          — Color-coded pill label (success/warning/danger/info)
    AnimatedProgressBar  — Themed QProgressBar with QPropertyAnimation fill
    InfoRow              — Two-column label/value display row
    SuggestedQuestionButton — Compact chip button for AI suggested queries
    EmptyState           — Polished empty-state widget with icon, title, description
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QProgressBar, QSizePolicy,
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve,
)
from PySide6.QtGui import QFont


# ---------------------------------------------------------------------------
# SectionHeader
# ---------------------------------------------------------------------------

class SectionHeader(QWidget):
    """Section title bar with optional subtitle and right-side badge or widget.

    Usage::

        header = SectionHeader("STUDENT OVERVIEW", subtitle="Class XII-A")
        header = SectionHeader("ALERTS", badge_text="3", badge_variant="danger")
    """

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        badge_text: str = "",
        badge_variant: str = "info",
        parent=None,
    ):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Left block: title + optional subtitle
        left_block = QWidget(self)
        left_block.setStyleSheet("background: transparent;")
        left_v = QVBoxLayout(left_block)
        left_v.setContentsMargins(0, 0, 0, 0)
        left_v.setSpacing(2)

        title_lbl = QLabel(title, left_block)
        title_lbl.setFont(QFont("Outfit", 11, QFont.Bold))
        title_lbl.setStyleSheet(
            "color: #8D96A8; letter-spacing: 1px; "
            "text-transform: uppercase; background: transparent; border: none;"
        )
        left_v.addWidget(title_lbl)

        if subtitle:
            sub_lbl = QLabel(subtitle, left_block)
            sub_lbl.setFont(QFont("Outfit", 11))
            sub_lbl.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
            left_v.addWidget(sub_lbl)

        layout.addWidget(left_block)
        layout.addStretch(1)

        # Optional right badge
        if badge_text:
            badge = StatusBadge(badge_text, variant=badge_variant, parent=self)
            layout.addWidget(badge)


# ---------------------------------------------------------------------------
# StatusBadge
# ---------------------------------------------------------------------------

_BADGE_STYLES = {
    "success": ("rgba(48, 196, 141, 0.15)", "#30C48D", "rgba(48, 196, 141, 0.30)"),
    "warning": ("rgba(245, 165, 36, 0.15)", "#F5A524", "rgba(245, 165, 36, 0.30)"),
    "danger":  ("rgba(229, 72, 77, 0.15)",  "#E5484D", "rgba(229, 72, 77, 0.30)"),
    "info":    ("rgba(77, 141, 255, 0.15)", "#4D8DFF", "rgba(77, 141, 255, 0.30)"),
    "purple":  ("rgba(124, 92, 255, 0.15)", "#7C5CFF", "rgba(124, 92, 255, 0.30)"),
    "muted":   ("rgba(141, 150, 168, 0.12)","#8D96A8", "rgba(141, 150, 168, 0.20)"),
}


class StatusBadge(QLabel):
    """Color-coded compact pill badge for status indicators.

    Variants: 'success', 'warning', 'danger', 'info', 'purple', 'muted'

    Usage::

        badge = StatusBadge("● Online", variant="success")
        badge = StatusBadge("HIGH RISK", variant="danger")
    """

    def __init__(self, text: str, variant: str = "info", parent=None):
        super().__init__(text, parent)
        bg, fg, border = _BADGE_STYLES.get(variant, _BADGE_STYLES["info"])
        self.setStyleSheet(
            f"background-color: {bg};"
            f"color: {fg};"
            f"border: 1px solid {border};"
            f"border-radius: 10px;"
            f"padding: 3px 10px;"
            f"font-size: 11px;"
            f"font-weight: 700;"
        )
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Outfit", 11, QFont.Bold))


# ---------------------------------------------------------------------------
# AnimatedProgressBar
# ---------------------------------------------------------------------------

_BAR_OBJECT_NAMES = {
    "red":     "ProgressBar",
    "success": "SuccessBar",
    "warning": "WarningBar",
    "purple":  "PurpleBar",
    "blue":    "BlueBar",
}


class AnimatedProgressBar(QWidget):
    """Themed progress bar with animated fill via QPropertyAnimation.

    Usage::

        bar = AnimatedProgressBar(value=72.5, variant="success")
        bar = AnimatedProgressBar(value=45.0, variant="warning", height=8)
    """

    def __init__(
        self,
        value: float = 0.0,
        variant: str = "red",
        bar_height: int = 6,
        animate: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._bar = QProgressBar(self)
        self._bar.setRange(0, 1000)
        self._bar.setValue(0)
        self._bar.setFixedHeight(bar_height)
        self._bar.setTextVisible(False)
        self._bar.setObjectName(_BAR_OBJECT_NAMES.get(variant, "ProgressBar"))

        layout.addWidget(self._bar)

        # Animate from 0 → target value
        target_int = max(0, min(1000, int(value * 10)))

        if animate and target_int > 0:
            self._anim = QPropertyAnimation(self._bar, b"value")
            self._anim.setDuration(600)
            self._anim.setStartValue(0)
            self._anim.setEndValue(target_int)
            self._anim.setEasingCurve(QEasingCurve.OutCubic)
            self._anim.start()
        else:
            self._bar.setValue(target_int)

    def set_value(self, value: float, animate: bool = True) -> None:
        """Update the progress bar value (0–100)."""
        target_int = max(0, min(1000, int(value * 10)))
        if animate:
            self._anim = QPropertyAnimation(self._bar, b"value")
            self._anim.setDuration(500)
            self._anim.setStartValue(self._bar.value())
            self._anim.setEndValue(target_int)
            self._anim.setEasingCurve(QEasingCurve.OutCubic)
            self._anim.start()
        else:
            self._bar.setValue(target_int)


# ---------------------------------------------------------------------------
# InfoRow
# ---------------------------------------------------------------------------

class InfoRow(QWidget):
    """Two-column label/value display row with consistent spacing.

    Usage::

        row = InfoRow("Provider:", "Google Gemini")
        row = InfoRow("Status:", "Online", value_variant="success")
    """

    def __init__(
        self,
        label: str,
        value: str,
        value_variant: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        lbl = QLabel(label, self)
        lbl.setFont(QFont("Outfit", 11))
        lbl.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        lbl.setFixedWidth(90)
        lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(lbl)

        if value_variant:
            val_widget = StatusBadge(value, variant=value_variant, parent=self)
        else:
            val_widget = QLabel(value, self)
            val_widget.setFont(QFont("Outfit", 11, QFont.Bold))
            val_widget.setStyleSheet("color: #F5F7FA; background: transparent; border: none;")
            val_widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            val_widget.setWordWrap(True)

        layout.addWidget(val_widget, 1)

    def update_value(self, new_value: str) -> None:
        """Update the displayed value text."""
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and item.widget():
                w = item.widget()
                if isinstance(w, QLabel) and w.text() != "":
                    # Skip the label column
                    pass
        # Simpler: find second QLabel
        labels = self.findChildren(QLabel)
        if len(labels) >= 2:
            labels[1].setText(new_value)


# ---------------------------------------------------------------------------
# SuggestedQuestionButton
# ---------------------------------------------------------------------------

class SuggestedQuestionButton(QPushButton):
    """Compact chip-style button for AI suggested questions.

    Uses the #ChipButton object name from theme.py stylesheet.

    Usage::

        btn = SuggestedQuestionButton("Show students needing attention")
        btn.clicked.connect(handler)
    """

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("ChipButton")
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont("Outfit", 11))
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)


# ---------------------------------------------------------------------------
# EmptyState
# ---------------------------------------------------------------------------

class EmptyState(QWidget):
    """Polished empty-state widget displayed when no data is available.

    Renders:
        - Large icon/emoji character
        - Bold title
        - Descriptive subtitle
        - Optional action button

    Usage::

        state = EmptyState(
            icon="🔍",
            title="No Students Found",
            description="Try adjusting your search or add a new student.",
            action_text="Add Student",
            action_callback=self.open_add_dialog,
        )
    """

    def __init__(
        self,
        icon: str = "📭",
        title: str = "Nothing here yet",
        description: str = "No data is available to display.",
        action_text: str = "",
        action_callback=None,
        parent=None,
    ):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        # Icon
        icon_lbl = QLabel(icon, self)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 40))
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(
            "color: #3A3F55; background: transparent; border: none;"
        )
        layout.addWidget(icon_lbl)

        # Title
        title_lbl = QLabel(title, self)
        title_lbl.setFont(QFont("Outfit", 16, QFont.Bold))
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet(
            "color: #8D96A8; background: transparent; border: none;"
        )
        layout.addWidget(title_lbl)

        # Description
        desc_lbl = QLabel(description, self)
        desc_lbl.setFont(QFont("Outfit", 12))
        desc_lbl.setAlignment(Qt.AlignCenter)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(
            "color: #4A5060; background: transparent; border: none;"
        )
        desc_lbl.setMaximumWidth(340)
        layout.addWidget(desc_lbl)

        # Optional action button
        if action_text and action_callback:
            layout.addSpacing(8)
            btn = QPushButton(action_text, self)
            btn.setObjectName("PrimaryButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedWidth(160)
            btn.setFixedHeight(38)
            btn.setFont(QFont("Outfit", 12, QFont.Bold))
            btn.clicked.connect(action_callback)
            layout.addWidget(btn, alignment=Qt.AlignCenter)
