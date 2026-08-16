"""PySide6 panel for AI Teacher Copilot & Decision Support System.

Version 1.4 — AI Teacher Copilot
Features:
- 8 Predefined grounded Copilot Actions (Explain Risk, Study Plan 7/14/30d, Weak Topics,
  Intervention Plan, Class Summary, Compare Students, Parent Letter, Teacher Actions).
- Non-blocking QThread background execution.
- Deterministic offline resilience & fallback display.
- Advisory human-in-the-loop confirmation notices.
"""

from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QGridLayout, QScrollArea, QCheckBox, QComboBox, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont

from core import ai, student_service
from desktop.widgets.reusable_ui_components import (
    InfoRow, StatusBadge, SectionHeader
)
from desktop.widgets.loading_indicator import LoadingIndicator


class CopilotWorker(QThread):
    finished = Signal(dict)

    def __init__(self, action_name: str, params: dict):
        super().__init__()
        self.action_name = action_name
        self.params = params

    def run(self):
        try:
            res = ai.dispatch_copilot_action(self.action_name, self.params)
            self.finished.emit(res)
        except Exception as exc:
            self.finished.emit({
                "success": False,
                "response": f"System execution error: {exc}",
                "provider": None,
                "model": None,
                "fallback_used": False,
                "is_offline_fallback": True,
                "error": str(exc)
            })


class SpeakWorker(QThread):
    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def run(self):
        try:
            from core import voice_service
            voice_service.speak_response(self.text)
        except Exception:
            pass


class MessageBubble(QFrame):
    def __init__(self, parent, sender: str, text: str, is_loading: bool = False):
        super().__init__(parent)
        self.setObjectName("InnerCardFrame")
        self.setMaximumWidth(680)

        # Style based on sender
        if sender in ["You", "You (Voice)"]:
            self.setStyleSheet(
                "QFrame { background-color: #7C5CFF; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; }"
                "QLabel { color: #FFFFFF; background: transparent; border: none; }"
            )
        elif sender == "System":
            self.setStyleSheet(
                "QFrame { background-color: #151925; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; }"
                "QLabel { color: #F5A524; background: transparent; border: none; }"
            )
        else:
            self.setStyleSheet(
                "QFrame { background-color: #10131D; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; }"
                "QLabel { color: #F5F7FA; background: transparent; border: none; }"
            )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(6)

        sender_lbl = QLabel(sender, self)
        sender_lbl.setFont(QFont("Outfit", 9, QFont.Bold))
        sender_lbl.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        layout.addWidget(sender_lbl)

        if is_loading:
            indicator = LoadingIndicator(self)
            layout.addWidget(indicator)
        else:
            txt_lbl = QLabel(text, self)
            txt_lbl.setFont(QFont("Outfit", 11))
            txt_lbl.setWordWrap(True)
            txt_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            layout.addWidget(txt_lbl)


class AIAssistantFrame(QWidget):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.active_workers = []
        self.speak_worker = None
        self.thinking_bubble = None

        # Main Layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(15, 12, 15, 12)
        root_layout.setSpacing(10)

        # -------------------------------------------------------------------
        # 1. Header Section
        # -------------------------------------------------------------------
        header_frame = QFrame(self)
        header_frame.setObjectName("CardFrame")
        header_frame.setFixedHeight(54)
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(16, 0, 16, 0)

        title = QLabel("AI TEACHER COPILOT & DECISION SUPPORT", header_frame)
        title.setFont(QFont("Outfit", 17, QFont.Bold))
        title.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        h_layout.addWidget(title)

        subtitle = QLabel("Grounded • Advisory • Decision-Support System", header_frame)
        subtitle.setFont(QFont("Outfit", 11))
        subtitle.setStyleSheet("color: #8D96A8; background: transparent; border: none;")
        h_layout.addWidget(subtitle)
        h_layout.addStretch(1)

        root_layout.addWidget(header_frame)

        # -------------------------------------------------------------------
        # 2. Context Parameters & Control Bar
        # -------------------------------------------------------------------
        ctrl_frame = QFrame(self)
        ctrl_frame.setObjectName("CardFrame")
        c_layout = QHBoxLayout(ctrl_frame)
        c_layout.setContentsMargins(16, 8, 16, 8)
        c_layout.setSpacing(12)

        c_layout.addWidget(QLabel("Target Student ID:", ctrl_frame))
        self.sid_entry = QLineEdit(ctrl_frame)
        self.sid_entry.setPlaceholderText("e.g. 1")
        self.sid_entry.setFixedWidth(75)
        c_layout.addWidget(self.sid_entry)

        c_layout.addWidget(QLabel("Study Duration:", ctrl_frame))
        self.duration_combo = QComboBox(ctrl_frame)
        self.duration_combo.addItems(["7 Days", "14 Days", "30 Days"])
        self.duration_combo.setFixedWidth(90)
        c_layout.addWidget(self.duration_combo)

        c_layout.addWidget(QLabel("Compare With ID:", ctrl_frame))
        self.compare_sid_entry = QLineEdit(ctrl_frame)
        self.compare_sid_entry.setPlaceholderText("e.g. 2")
        self.compare_sid_entry.setFixedWidth(75)
        c_layout.addWidget(self.compare_sid_entry)

        c_layout.addStretch(1)

        self.speech_cb = QCheckBox("Speak AI Audio", ctrl_frame)
        self.speech_cb.setChecked(False)
        c_layout.addWidget(self.speech_cb)

        root_layout.addWidget(ctrl_frame)

        # -------------------------------------------------------------------
        # 3. Copilot 8 Quick Actions Grid
        # -------------------------------------------------------------------
        quick_frame = QFrame(self)
        quick_frame.setObjectName("CardFrame")
        qf_layout = QVBoxLayout(quick_frame)
        qf_layout.setContentsMargins(14, 10, 14, 10)
        qf_layout.setSpacing(8)

        q_hdr = SectionHeader("COPILOT PEDAGOGICAL ACTIONS", subtitle="Select a grounded AI decision-support workflow", parent=quick_frame)
        qf_layout.addWidget(q_hdr)

        btn_grid = QGridLayout()
        btn_grid.setSpacing(8)

        self.actions_map = [
            ("🔍 Explain Risk", "explain_risk", 0, 0),
            ("📚 Create Study Plan", "study_plan", 0, 1),
            ("🎯 Identify Weak Topics", "identify_weak_topics", 0, 2),
            ("🛠️ Intervention Plan", "generate_intervention", 0, 3),
            ("📊 Class Summary", "class_summary", 1, 0),
            ("⚖️ Compare Students", "compare_students", 1, 1),
            ("✉️ Draft Parent Letter", "parent_summary", 1, 2),
            ("💡 Suggest Actions", "suggest_actions", 1, 3),
        ]

        for label, act_key, r, c in self.actions_map:
            btn = QPushButton(label, quick_frame)
            btn.setFont(QFont("Outfit", 10, QFont.Bold))
            btn.setStyleSheet(
                "QPushButton { background: #151925; color: #F5F7FA; border: 1px solid rgba(255,255,255,0.08);"
                " border-radius: 6px; padding: 7px 10px; text-align: left; }"
                "QPushButton:hover { background: #1B2030; border-color: #7C5CFF; color: #FFFFFF; }"
            )
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, k=act_key: self.trigger_copilot_action(k))
            btn_grid.addWidget(btn, r, c)

        qf_layout.addLayout(btn_grid)
        root_layout.addWidget(quick_frame)

        # -------------------------------------------------------------------
        # 4. Split Workspace (Chat Logs + Metadata & Safety Panel)
        # -------------------------------------------------------------------
        split_widget = QWidget(self)
        split_layout = QHBoxLayout(split_widget)
        split_layout.setContentsMargins(0, 0, 0, 0)
        split_layout.setSpacing(10)

        # Left Column: Conversation Stream
        self.chat_scroll = QScrollArea(split_widget)
        self.chat_scroll.setObjectName("CardFrame")
        self.chat_scroll.setWidgetResizable(True)
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setContentsMargins(14, 14, 14, 14)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_scroll.setWidget(self.chat_content)
        split_layout.addWidget(self.chat_scroll, 3)

        # Right Column: Metadata & Safety Panel
        self.meta_panel = QFrame(split_widget)
        self.meta_panel.setObjectName("CardFrame")
        self.meta_panel.setFixedWidth(260)
        mp_layout = QVBoxLayout(self.meta_panel)
        mp_layout.setContentsMargins(16, 16, 16, 16)
        mp_layout.setSpacing(12)
        mp_layout.setAlignment(Qt.AlignTop)

        lbl_meta = QLabel("COPILOT STATUS & SAFETY", self.meta_panel)
        lbl_meta.setFont(QFont("Outfit", 12, QFont.Bold))
        lbl_meta.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        mp_layout.addWidget(lbl_meta)

        self.info_provider = InfoRow("Provider:", "Auto", parent=self.meta_panel)
        mp_layout.addWidget(self.info_provider)

        self.info_model = InfoRow("Active Model:", "gemini-2.5-flash", parent=self.meta_panel)
        mp_layout.addWidget(self.info_model)

        self.info_fallback = InfoRow("Fallback Used:", "No", parent=self.meta_panel)
        mp_layout.addWidget(self.info_fallback)

        self.status_badge = StatusBadge("● Online", variant="success", parent=self.meta_panel)
        mp_layout.addWidget(self.status_badge)

        # Advisory Human-in-the-Loop Safety Card
        safety_card = QFrame(self.meta_panel)
        safety_card.setObjectName("InnerCardFrame")
        safety_card.setStyleSheet("background-color: rgba(124, 92, 255, 0.08); border: 1px solid rgba(124, 92, 255, 0.25); border-radius: 8px; padding: 10px;")
        sc_l = QVBoxLayout(safety_card)
        sc_l.setContentsMargins(8, 8, 8, 8)
        sc_l.setSpacing(4)

        sc_title = QLabel("🛡️ ADVISORY DECISION SUPPORT", safety_card)
        sc_title.setFont(QFont("Outfit", 9, QFont.Bold))
        sc_title.setStyleSheet("color: #7C5CFF;")
        sc_l.addWidget(sc_title)

        sc_txt = QLabel("All AI outputs are grounded decision-support recommendations. Educator confirmation is strictly required before initiating official interventions.", safety_card)
        sc_txt.setFont(QFont("Outfit", 9))
        sc_txt.setStyleSheet("color: #8D96A8;")
        sc_txt.setWordWrap(True)
        sc_l.addWidget(sc_txt)

        mp_layout.addWidget(safety_card)
        mp_layout.addStretch(1)
        split_layout.addWidget(self.meta_panel, 1)

        root_layout.addWidget(split_widget, 1)

        # -------------------------------------------------------------------
        # 5. Bottom Input Bar for Free-Form Inquiries
        # -------------------------------------------------------------------
        input_frame = QWidget(self)
        if_layout = QHBoxLayout(input_frame)
        if_layout.setContentsMargins(0, 0, 0, 0)
        if_layout.setSpacing(8)

        self.input_entry = QLineEdit(input_frame)
        self.input_entry.setPlaceholderText("Ask the Copilot a pedagogical question or enter a student query...")
        self.input_entry.setFixedHeight(38)
        self.input_entry.returnPressed.connect(self.send_freeform_message)
        if_layout.addWidget(self.input_entry)

        self.mic_btn = QPushButton("🎤 Voice", input_frame)
        self.mic_btn.setFixedHeight(38)
        self.mic_btn.setFixedWidth(80)
        self.mic_btn.setFont(QFont("Outfit", 11, QFont.Bold))
        self.mic_btn.setCursor(Qt.PointingHandCursor)
        self.mic_btn.clicked.connect(self.trigger_voice_command)
        if_layout.addWidget(self.mic_btn)

        send_btn = QPushButton("ASK COPILOT", input_frame)
        send_btn.setObjectName("PrimaryButton")
        send_btn.setFixedHeight(38)
        send_btn.setFixedWidth(110)
        send_btn.setFont(QFont("Outfit", 11, QFont.Bold))
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.clicked.connect(self.send_freeform_message)
        if_layout.addWidget(send_btn)

        root_layout.addWidget(input_frame)

        # Refresh initial metadata status
        self.refresh_metadata_status()

        # Initial Welcome Message
        self.add_message(
            "AI Copilot",
            "Welcome to the **PMLA-SCWE AI Teacher Copilot**!\n\n"
            "Select one of the 8 quick action workflows above or type any pedagogical question below.\n"
            "All recommendations are strictly grounded in verified student records and require teacher review."
        )

    def refresh_metadata_status(self):
        st = ai.get_ai_status_summary()
        prov = st.get("active_provider") or "Deterministic Engine"
        model = st.get("active_model") or "Offline Rule-Based"
        is_online = st.get("status") == "Online"

        self.info_provider.findChildren(QLabel)[-1].setText(prov)
        self.info_model.findChildren(QLabel)[-1].setText(model)
        self.info_fallback.findChildren(QLabel)[-1].setText("Available" if st.get("fallback_available") else "No")

        if is_online:
            self.status_badge.setText("● Online")
            self.status_badge.setStyleSheet(
                "background-color: rgba(48,196,141,0.15); color: #30C48D; border: 1px solid rgba(48,196,141,0.30); border-radius: 10px; padding: 3px 10px; font-size: 11px; font-weight: 700;"
            )
        else:
            self.status_badge.setText("○ Offline Engine")
            self.status_badge.setStyleSheet(
                "background-color: rgba(141,150,168,0.15); color: #8D96A8; border: 1px solid rgba(141,150,168,0.30); border-radius: 10px; padding: 3px 10px; font-size: 11px; font-weight: 700;"
            )

    def add_message(self, sender: str, text: str, is_loading: bool = False) -> QWidget:
        row = QWidget(self.chat_content)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        bubble = MessageBubble(row, sender, text, is_loading=is_loading)

        if sender in ["You", "You (Voice)"]:
            row_layout.addStretch(1)
            row_layout.addWidget(bubble)
        else:
            row_layout.addWidget(bubble)
            row_layout.addStretch(1)

        self.chat_layout.addWidget(row)
        QTimer.singleShot(10, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))
        return row

    def show_thinking(self):
        self.thinking_bubble = self.add_message("AI Copilot", "Analyzing grounded student records...", is_loading=True)

    def remove_thinking(self):
        if self.thinking_bubble:
            self.thinking_bubble.deleteLater()
            self.thinking_bubble = None

    def trigger_copilot_action(self, action_key: str):
        sid_raw = self.sid_entry.text().strip()
        sid = int(sid_raw) if sid_raw.isdigit() else None
        cmp_raw = self.compare_sid_entry.text().strip()
        cmp_sid = int(cmp_raw) if cmp_raw.isdigit() else None

        # Extract duration
        dur_text = self.duration_combo.currentText()
        duration_days = int(dur_text.split(" ")[0]) if " " in dur_text else 7

        if action_key not in ("class_summary",) and sid is None:
            self.add_message("System", "Please enter a valid Target Student ID above to run this action.")
            return

        if action_key == "compare_students" and (sid is None or cmp_sid is None):
            self.add_message("System", "Please specify both Target Student ID and Compare With ID.")
            return

        action_labels = {
            "explain_risk": f"Explain Learning Risk for Student #{sid}",
            "study_plan": f"Generate {duration_days}-Day Study Plan for Student #{sid}",
            "identify_weak_topics": f"Identify Critical Learning Gaps for Student #{sid}",
            "generate_intervention": f"Draft Official Intervention Plan for Student #{sid}",
            "class_summary": "Summarize Classroom Cohort Performance",
            "compare_students": f"Compare Student #{sid} vs Student #{cmp_sid}",
            "parent_summary": f"Draft Parent Progress Letter for Student #{sid}",
            "suggest_actions": f"Suggest Immediate Teacher Actions for Student #{sid}",
        }

        self.add_message("You", action_labels.get(action_key, action_key))
        self.show_thinking()

        params = {
            "student_id": sid,
            "duration_days": duration_days,
            "compare_student_id": cmp_sid,
            "class_name": "All",
            "section": "All"
        }

        worker = CopilotWorker(action_key, params)
        worker.finished.connect(self.on_copilot_finished)
        self.active_workers.append(worker)
        worker.start()

    def send_freeform_message(self):
        query = self.input_entry.text().strip()
        if not query:
            return

        self.input_entry.clear()
        self.add_message("You", query)
        self.show_thinking()

        sid_raw = self.sid_entry.text().strip()
        sid = int(sid_raw) if sid_raw.isdigit() else None

        params = {"query": query, "student_id": sid}
        worker = CopilotWorker("general_inquiry", params)
        worker.finished.connect(self.on_copilot_finished)
        self.active_workers.append(worker)
        worker.start()

    def trigger_voice_command(self):
        self.mic_btn.setEnabled(False)
        self.mic_btn.setText("Listening...")
        self.add_message("System", "Microphone listening active. Please speak clearly...")

        def on_voice_done(res):
            self.mic_btn.setEnabled(True)
            self.mic_btn.setText("🎤 Voice")
            if res.get("success"):
                cmd = res.get("command", "")
                self.input_entry.setText(cmd)
                self.send_freeform_message()
            else:
                self.add_message("System", res.get("response", "Voice recognition unavailable."))

        # Quick worker for voice
        class SimpleVoiceWorker(QThread):
            voice_finished = Signal(dict)
            def run(self):
                try:
                    from core import voice_service
                    cmd = voice_service.listen_for_command()
                    self.voice_finished.emit({"success": True, "command": cmd})
                except Exception as e:
                    self.voice_finished.emit({"success": False, "response": str(e)})

        vw = SimpleVoiceWorker(self)
        vw.voice_finished.connect(on_voice_done)
        self.active_workers.append(vw)
        vw.start()

    def on_copilot_finished(self, res_dict: dict):
        self.remove_thinking()

        response_text = res_dict.get("response", "No response generated.")
        self.add_message("AI Copilot", response_text)

        # Update metadata display
        provider = str(res_dict.get("provider") or "Deterministic Engine")
        model = str(res_dict.get("model") or "Offline Rule-Based")
        is_fallback = bool(res_dict.get("fallback_used", False))

        self.info_provider.findChildren(QLabel)[-1].setText(provider)
        self.info_model.findChildren(QLabel)[-1].setText(model)
        self.info_fallback.findChildren(QLabel)[-1].setText("Yes" if is_fallback else "No")

        if res_dict.get("is_offline_fallback"):
            self.status_badge.setText("○ Offline Engine")
            self.status_badge.setStyleSheet(
                "background-color: rgba(141,150,168,0.15); color: #8D96A8; border: 1px solid rgba(141,150,168,0.30); border-radius: 10px; padding: 3px 10px; font-size: 11px; font-weight: 700;"
            )
        else:
            self.status_badge.setText("● Online")
            self.status_badge.setStyleSheet(
                "background-color: rgba(48,196,141,0.15); color: #30C48D; border: 1px solid rgba(48,196,141,0.30); border-radius: 10px; padding: 3px 10px; font-size: 11px; font-weight: 700;"
            )

        # Speak if enabled
        if self.speech_cb.isChecked() and res_dict.get("success"):
            self.speak_worker = SpeakWorker(response_text)
            self.speak_worker.start()

    def closeEvent(self, event):
        for worker in self.active_workers:
            if worker.isRunning():
                worker.terminate()
                worker.wait()
        if self.speak_worker and self.speak_worker.isRunning():
            self.speak_worker.terminate()
            self.speak_worker.wait()
        super().closeEvent(event)
