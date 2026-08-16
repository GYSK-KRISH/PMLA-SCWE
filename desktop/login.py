"""PySide6 Login panel — v1.1 Premium glassmorphism with animated error feedback."""

from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPainter, QColor, QRadialGradient, QPen

from core import auth_service
from core.database import get_db_status


class EyeToggleButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(40, 40)
        self.setToolTip("Show password")
        self.clicked.connect(self.update_tooltip)

    def update_tooltip(self):
        if self.isChecked():
            self.setToolTip("Hide password")
        else:
            self.setToolTip("Show password")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Base background matching text input
        painter.fillRect(self.rect(), QColor("#13131A"))
        
        # Border lines matching inputs
        painter.setPen(QPen(QColor("#23232F"), 1))
        painter.drawLine(0, 0, 0, self.height())
        painter.drawLine(0, 0, self.width(), 0)
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())

        # Vector Eye Drawing
        painter.setPen(QPen(QColor(113, 113, 122), 2))
        painter.setBrush(Qt.NoBrush)
        
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        
        if self.isChecked():
            # Hide password - slashed eye outline
            painter.drawArc(cx - 10, cy - 6, 20, 12, 35 * 16, 110 * 16)
            painter.drawArc(cx - 10, cy - 6, 20, 12, 215 * 16, 110 * 16)
            painter.drawLine(cx - 8, cy - 6, cx + 8, cy + 6)
        else:
            # Show password - full eye outline and pupil
            painter.drawArc(cx - 10, cy - 6, 20, 12, 35 * 16, 110 * 16)
            painter.drawArc(cx - 10, cy - 6, 20, 12, 215 * 16, 110 * 16)
            painter.setBrush(QColor(113, 113, 122))
            painter.drawEllipse(cx - 3, cy - 3, 6, 6)


class LoginFrame(QWidget):
    def __init__(self, parent, controller, on_login_success):
        super().__init__(parent)
        self.controller = controller
        self.on_login_success = on_login_success

        # Style override for text inputs, buttons, and layouts
        self.setStyleSheet("""
            QLineEdit {
                background-color: #13131A;
                border: 1px solid #23232F;
                border-radius: 8px;
                color: #FFFFFF;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #7C5CFF;
                box-shadow: 0 0 0 2px rgba(124, 92, 255, 0.15);
            }
            QPushButton#PrimaryButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #E50914, stop:1 #6E46FF);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: #FFFFFF;
                border-radius: 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton#PrimaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FF1E27, stop:1 #825CFF);
            }
            QPushButton#PrimaryButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #CC000C, stop:1 #5B32E6);
                padding-top: 2px;
                padding-left: 2px;
            }
            QPushButton#PrimaryButton:disabled {
                background-color: #2E2E3E;
                color: #71717A;
            }
        """)

        # Layout wrapper to center the login box
        main_layout = QHBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Login Card Panel
        self.card = QFrame(self)
        self.card.setObjectName("CardFrame")
        self.card.setFixedSize(360, 485)
        
        # Soft Glass Background style
        self.card.setStyleSheet("""
            #CardFrame {
                background-color: rgba(15, 16, 25, 225);
                border: 1px solid rgba(255, 255, 255, 25);
                border-radius: 20px;
            }
        """)

        # Soft Graphics Drop Shadow Glow
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(110, 70, 255, 45))
        shadow.setOffset(0, 4)
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(12)
        card_layout.setAlignment(Qt.AlignTop)

        # Title/Brand Logo
        logo_lbl = QLabel(
            "<span style='color:#7C5CFF; font-size:18px;'>✦</span>"
            "  <span style='color:#FFFFFF;'>PMLA</span>"
            "<span style='color:#E5484D;'>-SCWE</span>",
            self.card
        )
        logo_lbl.setTextFormat(Qt.RichText)
        logo_lbl.setFont(QFont("Outfit", 14, QFont.Bold))
        logo_lbl.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        card_layout.addWidget(logo_lbl)
        card_layout.addSpacing(5)

        # Title
        title_lbl = QLabel("Welcome back", self.card)
        title_lbl.setFont(QFont("Outfit", 22, QFont.Bold))
        title_lbl.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        card_layout.addWidget(title_lbl)

        subtitle_lbl = QLabel(
            "AI-powered learning analytics and student wellbeing insights.",
            self.card
        )
        subtitle_lbl.setFont(QFont("Outfit", 11))
        subtitle_lbl.setStyleSheet("color: #71717A; background: transparent; border: none;")
        subtitle_lbl.setWordWrap(True)
        card_layout.addWidget(subtitle_lbl)
        
        card_layout.addSpacing(10)

        # Username Input
        self.username_entry = QLineEdit(self.card)
        self.username_entry.setPlaceholderText("👤 Enter username")
        self.username_entry.setFixedHeight(40)
        self.username_entry.returnPressed.connect(self.focus_password_entry)
        card_layout.addWidget(self.username_entry)

        # Password Input Layout Block
        password_container = QWidget(self.card)
        password_container.setFixedHeight(40)
        password_container.setStyleSheet("background: transparent;")
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(0)

        self.password_entry = QLineEdit(password_container)
        self.password_entry.setPlaceholderText("Enter your password")
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setFixedHeight(40)
        self.password_entry.setStyleSheet(
            "QLineEdit { border-top-right-radius: 0px; border-bottom-right-radius: 0px; border-right: none; }"
        )
        self.password_entry.returnPressed.connect(self.attempt_login)

        self.password_toggle = EyeToggleButton(password_container)
        self.password_toggle.clicked.connect(self.toggle_password)

        password_layout.addWidget(self.password_entry, 1)
        password_layout.addWidget(self.password_toggle)
        card_layout.addWidget(password_container)

        # Error / Status Feedback Label with opacity effect
        self.feedback_lbl = QLabel("", self.card)
        self.feedback_lbl.setFont(QFont("Outfit", 12))
        self.feedback_lbl.setAlignment(Qt.AlignCenter)
        self.feedback_lbl.setWordWrap(True)
        self.feedback_lbl.setStyleSheet("background: transparent; border: none;")
        self.feedback_lbl.setVisible(False)

        # Opacity effect for fade-in animation
        self._feedback_opacity = QGraphicsOpacityEffect(self.feedback_lbl)
        self._feedback_opacity.setOpacity(0.0)
        self.feedback_lbl.setGraphicsEffect(self._feedback_opacity)

        self._feedback_fade = QPropertyAnimation(self._feedback_opacity, b"opacity")
        self._feedback_fade.setDuration(250)
        self._feedback_fade.setEasingCurve(QEasingCurve.OutCubic)

        card_layout.addWidget(self.feedback_lbl)

        # Login Action Button
        self.login_btn = QPushButton("SIGN IN", self.card)
        self.login_btn.setObjectName("PrimaryButton")
        self.login_btn.setFixedHeight(40)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.attempt_login)
        card_layout.addWidget(self.login_btn)

        card_layout.addSpacing(10)

        # Divider (Secure Access)
        divider_lbl = QLabel("────────── SECURE ACCESS ──────────", self.card)
        divider_lbl.setFont(QFont("Outfit", 9))
        divider_lbl.setStyleSheet("color: #23232F; background: transparent; border: none;")
        divider_lbl.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(divider_lbl)

        card_layout.addSpacing(5)

        # Footer Links Block
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(4)
        footer_layout.setAlignment(Qt.AlignCenter)
        
        forgot_btn = QPushButton("Forgot Password?", self.card)
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.setStyleSheet(
            "QPushButton { color: #71717A; background: transparent; border: none; font-size: 11px; font-weight: bold; }"
            "QPushButton:hover { color: #E5E5E5; }"
        )
        footer_layout.addWidget(forgot_btn)
        
        terms_lbl = QLabel("Terms of Use  |  Privacy Policy", self.card)
        terms_lbl.setFont(QFont("Outfit", 10))
        terms_lbl.setStyleSheet("color: #4A4A5A; background: transparent; border: none;")
        terms_lbl.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(terms_lbl)
        
        card_layout.addLayout(footer_layout)

        main_layout.addWidget(self.card)

        # Focus automatically starts on the username field
        self.username_entry.setFocus()

    def focus_password_entry(self):
        self.password_entry.setFocus()

    def toggle_password(self, checked):
        if checked:
            self.password_entry.setEchoMode(QLineEdit.Normal)
        else:
            self.password_entry.setEchoMode(QLineEdit.Password)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 1. Clerk Deep Base
        painter.fillRect(self.rect(), QColor("#07080D"))
        
        # 2. Large Purple Orb (cx: 20%, cy: 30%)
        w, h = self.width(), self.height()
        purple_grad = QRadialGradient(w * 0.2, h * 0.3, max(w, h) * 0.6)
        purple_grad.setColorAt(0, QColor(110, 70, 255, 90)) # ~35% alpha (90/255)
        purple_grad.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), purple_grad)
        
        # 3. Blue Orb (cx: 80%, cy: 70%)
        blue_grad = QRadialGradient(w * 0.8, h * 0.7, max(w, h) * 0.6)
        blue_grad.setColorAt(0, QColor(45, 100, 255, 50)) # ~20% alpha (50/255)
        blue_grad.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), blue_grad)
        
        # 4. PMLA Red Accent (cx: 50%, cy: 50%)
        red_grad = QRadialGradient(w * 0.5, h * 0.5, max(w, h) * 0.7)
        red_grad.setColorAt(0, QColor(220, 38, 38, 45)) # ~18% alpha (45/255)
        red_grad.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), red_grad)
        
        # 5. Faint Grid overlay (40px spacing)
        pen = QPen(QColor(255, 255, 255, 4), 1, Qt.SolidLine) # very faint white
        painter.setPen(pen)
        grid_size = 40
        for x in range(0, w, grid_size):
            painter.drawLine(x, 0, x, h)
         # Draw last vertical edge line if needed
        for y in range(0, h, grid_size):
            painter.drawLine(0, y, w, y)

    def attempt_login(self):
        username = self.username_entry.text().strip()
        password = self.password_entry.text()

        if not username or not password:
            self.show_error("Fields cannot remain empty.")
            return

        # Disable login button briefly while authentication is processing
        self.login_btn.setEnabled(False)
        self.login_btn.setText("AUTHENTICATING...")
        self.repaint()

        # Run check asynchronously to allow UI to update and prevent double click
        QTimer.singleShot(100, lambda: self.process_auth(username, password))

    def process_auth(self, username, password):
        try:
            user = auth_service.login_user(username, password)
            if user:
                # Store logged-in user inside controller session context
                self.controller.current_user = user
                
                # Clear fields
                self.username_entry.clear()
                self.password_entry.clear()
                self.feedback_lbl.clear()
                
                # Reset password toggle state
                self.password_toggle.setChecked(False)
                self.password_entry.setEchoMode(QLineEdit.Password)
                
                # Trigger callback
                self.on_login_success()
            else:
                self.show_error("Invalid username or password.")
        except Exception as e:
            self.show_error(f"Database error occurred: {e}")
        finally:
            self.login_btn.setEnabled(True)
            self.login_btn.setText("SIGN IN")

    def show_error(self, text: str):
        self.feedback_lbl.setText(text)
        self.feedback_lbl.setStyleSheet("color: #E5484D; background: transparent; border: none;")
        self.feedback_lbl.setVisible(True)
        # Fade in
        self._feedback_fade.stop()
        self._feedback_fade.setStartValue(0.0)
        self._feedback_fade.setEndValue(1.0)
        self._feedback_fade.start()

    def clear_feedback(self):
        """Fade out and hide the feedback label."""
        self._feedback_fade.stop()
        self._feedback_fade.setStartValue(1.0)
        self._feedback_fade.setEndValue(0.0)
        self._feedback_fade.finished.connect(lambda: self.feedback_lbl.setVisible(False))
        self._feedback_fade.start()
