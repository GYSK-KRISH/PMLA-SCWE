"""Hoverable, elevational animated card frame widget for PySide6 desktop views.

Version 1.1 — hover background change added via stylesheet swap
combined with shadow animation. Qt does not support CSS transition
on background-color, so we use enterEvent/leaveEvent + setStyleSheet.
"""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QColor


_STYLE_NORMAL = (
    "QFrame#CardFrame {"
    "  background-color: #151925;"
    "  border: 1px solid rgba(255, 255, 255, 0.06);"
    "  border-radius: 12px;"
    "}"
)

_STYLE_HOVER = (
    "QFrame#CardFrame {"
    "  background-color: #1B2030;"
    "  border: 1px solid rgba(255, 255, 255, 0.10);"
    "  border-radius: 12px;"
    "}"
)


class AnimatedCard(QFrame):
    """Card frame with hover shadow elevation and background state change.

    Hover behavior:
        - Background: #151925 → #1B2030
        - Shadow blur: 15 → 30 px
        - Shadow color: black → soft purple glow
        - Shadow offset: (0, 2) → (0, 6)

    Animation duration: ~180 ms (OutQuad easing).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CardFrame")

        # Soft resting shadow
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setColor(QColor(0, 0, 0, 90))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)

        # Shadow blur animation
        self.blur_anim = QPropertyAnimation(self.shadow, b"blurRadius")
        self.blur_anim.setDuration(180)
        self.blur_anim.setEasingCurve(QEasingCurve.OutQuad)

        # Shadow offset animation
        self.offset_anim = QPropertyAnimation(self.shadow, b"offset")
        self.offset_anim.setDuration(180)
        self.offset_anim.setEasingCurve(QEasingCurve.OutQuad)

    def enterEvent(self, event):
        # Swap background via stylesheet
        self.setStyleSheet(_STYLE_HOVER)

        # Animate shadow to elevated state
        self.blur_anim.stop()
        self.offset_anim.stop()
        self.blur_anim.setEndValue(30)
        self.offset_anim.setEndValue(QPoint(0, 6))
        self.shadow.setColor(QColor(124, 92, 255, 55))  # Soft purple glow
        self.blur_anim.start()
        self.offset_anim.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        # Restore background via stylesheet
        self.setStyleSheet(_STYLE_NORMAL)

        # Animate shadow back to resting state
        self.blur_anim.stop()
        self.offset_anim.stop()
        self.blur_anim.setEndValue(15)
        self.offset_anim.setEndValue(QPoint(0, 2))
        self.shadow.setColor(QColor(0, 0, 0, 90))
        self.blur_anim.start()
        self.offset_anim.start()

        super().leaveEvent(event)
