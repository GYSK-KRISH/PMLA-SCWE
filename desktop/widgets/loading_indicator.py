"""Three-dot pulsing loading indicator widget for PySide6 desktop views."""

from __future__ import annotations
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter, QColor


class LoadingIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 20)
        self.active_index = 0

        # Timer to advance the dot animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance_animation)
        self.timer.start(250)

    def advance_animation(self):
        self.active_index = (self.active_index + 1) % 3
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        dot_radius = 4
        spacing = 14
        start_x = 12
        cy = self.height() / 2

        for i in range(3):
            cx = start_x + (i * spacing)
            if i == self.active_index:
                # Pulsing state dot
                painter.setBrush(QColor("#7C5CFF"))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(
                    int(cx - dot_radius - 1.5), 
                    int(cy - dot_radius - 1.5), 
                    int((dot_radius + 1.5) * 2), 
                    int((dot_radius + 1.5) * 2)
                )
            else:
                # Dimmed state dot
                painter.setBrush(QColor("#4A4F6B"))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(
                    int(cx - dot_radius), 
                    int(cy - dot_radius), 
                    int(dot_radius * 2), 
                    int(dot_radius * 2)
                )
