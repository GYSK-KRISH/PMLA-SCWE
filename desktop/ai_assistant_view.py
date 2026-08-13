"""CustomTkinter panel for AI Q&A consultation, recommendations, and speech toggles."""

from __future__ import annotations
import customtkinter as ctk

from core import ai_assistant, student_service


class AIAssistantFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Grid configuration
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header Section
        header_frame = ctk.CTkFrame(self, fg_color="#0F0F0F", border_color="#2A2A2A", border_width=1, corner_radius=12, height=80)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header_frame,
            text="AI DECISION-SUPPORT ASSISTANT",
            font=ctk.CTkFont(family="Outfit", size=24, weight="bold"),
            text_color="#FFFFFF"
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        # Controls Option Panel (e.g. binding Student ID)
        controls_frame = ctk.CTkFrame(self, fg_color="#1A1A1A", border_color="#2A2A2A", border_width=1, corner_radius=12)
        controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=10)

        sid_lbl = ctk.CTkLabel(
            controls_frame,
            text="Analyze Student ID:",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold"),
            text_color="#AAAAAA"
        )
        sid_lbl.grid(row=0, column=0, padx=(20, 5), pady=15, sticky="w")

        self.sid_entry = ctk.CTkEntry(
            controls_frame,
            placeholder_text="ID [optional]",
            width=100,
            fg_color="#181818",
            border_color="#303030",
            focused_border_color="#FF0000",
            placeholder_text_color="#717171",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=13)
        )
        self.sid_entry.grid(row=0, column=1, padx=10, pady=15, sticky="w")

        suggestions_btn = ctk.CTkButton(
            controls_frame,
            text="Generate AI Suggestions",
            command=self.load_ai_suggestions,
            fg_color="#E50914",
            hover_color="#CC0000",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Outfit", size=12, weight="bold")
        )
        suggestions_btn.grid(row=0, column=2, padx=10, pady=15, sticky="w")

        # Speech output checkbox
        self.speech_out_var = ctk.BooleanVar(value=True)
        self.speech_cb = ctk.CTkCheckBox(
            controls_frame,
            text="Speak AI Responses",
            variable=self.speech_out_var,
            border_color="#303030",
            checkmark_color="#FFFFFF",
            fg_color="#E50914",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=12)
        )
        self.speech_cb.grid(row=0, column=3, padx=(20, 20), pady=15, sticky="e")

        # Chat Log Panel
        self.chat_display = ctk.CTkTextbox(
            self,
            fg_color="#181818",
            border_color="#2A2A2A",
            border_width=1,
            corner_radius=12,
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#FFFFFF",
            wrap="word"
        )
        self.chat_display.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)
        self.chat_display.configure(state="disabled")

        # Bottom Input Bar
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=(10, 20))
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your question about student performance or cyber wellness here...",
            height=45,
            fg_color="#181818",
            border_color="#303030",
            focused_border_color="#FF0000",
            placeholder_text_color="#717171",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=13)
        )
        self.input_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.input_entry.bind("<Return>", lambda e: self.send_message())

        # Mic trigger button
        self.mic_btn = ctk.CTkButton(
            input_frame,
            text="🎤 Voice",
            command=self.trigger_voice_command,
            width=90,
            height=45,
            fg_color="#272727",
            hover_color="#333333",
            text_color="#FF0000",
            border_width=1,
            border_color="#3A3A3A",
            font=ctk.CTkFont(family="Outfit", size=12, weight="bold")
        )
        self.mic_btn.grid(row=0, column=1, padx=5, sticky="e")

        send_btn = ctk.CTkButton(
            input_frame,
            text="SEND",
            command=self.send_message,
            width=90,
            height=45,
            fg_color="#E50914",
            hover_color="#CC0000",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Outfit", size=13, weight="bold")
        )
        send_btn.grid(row=0, column=2, padx=(5, 0), sticky="e")

        # Initial greeting
        self.write_to_chat(
            "AI Assistant",
            "Welcome! I am the PMLA-SCWE explainable decision-support assistant.\n"
            "You can type questions like 'How is student 1 performing?' or request student suggestions using the selector above."
        )

    def write_to_chat(self, sender: str, text: str):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"[{sender}]:\n{text}\n\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def send_message(self):
        query = self.input_entry.get().strip()
        if not query:
            return

        self.input_entry.delete(0, "end")
        self.write_to_chat("You", query)

        # Check if student ID context was provided
        student_id = self.get_selected_student_id()

        self.write_to_chat("AI Assistant", "Thinking...")
        self.update()

        # Execute AI query in background/blocking (simple block is fine for this app)
        try:
            if student_id:
                response = ai_assistant.ask_ai_about_student(student_id, query)
            else:
                response = ai_assistant.ask_ai(query)
            
            # Remove "Thinking..." and replace with real response
            self.delete_last_lines(2)
            self.write_to_chat("AI Assistant", response)
            self.speak_if_enabled(response)
        except Exception as e:
            self.delete_last_lines(2)
            self.write_to_chat("AI Assistant", f"System Error: {e}")

    def load_ai_suggestions(self):
        student_id = self.get_selected_student_id()
        if not student_id:
            self.write_to_chat("System", "Please specify a valid Student ID to load suggestions.")
            return

        self.write_to_chat("You", f"Generate AI recommendations for Student ID {student_id}.")
        self.write_to_chat("AI Assistant", "Consulting service...")
        self.update()

        try:
            response = ai_assistant.get_ai_suggestions(student_id)
            self.delete_last_lines(2)
            self.write_to_chat("AI Assistant", response)
            self.speak_if_enabled(response)
        except Exception as e:
            self.delete_last_lines(2)
            self.write_to_chat("AI Assistant", f"System Error: {e}")

    def trigger_voice_command(self):
        # Dynamically import voice service to allow Phase 8/9 separation
        try:
            from core import voice_service
        except ImportError:
            self.write_to_chat("System", "Voice services are not fully compiled yet (scheduled for Phase 9).")
            return

        self.mic_btn.configure(state="disabled", text="Listening...")
        self.write_to_chat("System", "Microphone listening active. Please speak clearly...")
        self.update()

        try:
            command = voice_service.listen_for_command()
            self.mic_btn.configure(state="normal", text="🎤 Voice")
            self.delete_last_lines(2) # remove system message
            
            if command.startswith("[Error:"):
                self.write_to_chat("System", command)
                return

            self.write_to_chat("You (Voice)", command)
            self.write_to_chat("AI Assistant", "Thinking...")
            self.update()

            student_id = self.get_selected_student_id()
            if student_id:
                response = ai_assistant.ask_ai_about_student(student_id, command)
            else:
                response = ai_assistant.ask_ai(command)

            self.delete_last_lines(2)
            self.write_to_chat("AI Assistant", response)
            self.speak_if_enabled(response)

        except Exception as e:
            self.mic_btn.configure(state="normal", text="🎤 Voice")
            self.write_to_chat("System", f"Voice recording failed: {e}")

    def speak_if_enabled(self, text: str):
        if not self.speech_out_var.get():
            return

        # Check if voice service is active
        try:
            from core import voice_service
            voice_service.speak_response(text)
        except ImportError:
            pass

    def get_selected_student_id(self) -> int | None:
        raw = self.sid_entry.get().strip()
        if not raw:
            return None
        try:
            sid = int(raw)
            # Check existence
            res = student_service.search_students(str(sid))
            return sid if res else None
        except ValueError:
            return None

    def delete_last_lines(self, count: int):
        self.chat_display.configure(state="normal")
        # Textbox index structure: line.char
        # Delete last lines by extracting content, split lines, and rewriting
        content = self.chat_display.get("1.0", "end-1c")
        lines = content.split("\n")
        # Remove trailing empty strings from splits
        while lines and not lines[-1]:
            lines.pop()
        
        for _ in range(count):
            if lines:
                lines.pop()
        
        self.chat_display.delete("1.0", "end")
        self.chat_display.insert("1.0", "\n".join(lines) + "\n\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
