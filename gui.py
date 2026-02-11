"""
GUI Premium — Interface do Agente Pessoal ADK AGENT.
Dark theme com Tkinter, auto-falante, microfone, preview da tela e chat.
"""

import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import asyncio
import os
import sys
from PIL import Image, ImageTk


class AgentGUI:
    """Interface gráfica premium para o agente multimodal."""

    # ═════════════════ CORES DO TEMA ═════════════════
    BG_DARK = "#0D1117"
    BG_CARD = "#161B22"
    BG_INPUT = "#21262D"
    BG_HOVER = "#30363D"
    TEXT_PRIMARY = "#E6EDF3"
    TEXT_SECONDARY = "#8B949E"
    ACCENT_BLUE = "#58A6FF"
    ACCENT_GREEN = "#3FB950"
    ACCENT_RED = "#F85149"
    ACCENT_PURPLE = "#BC8CFF"
    ACCENT_ORANGE = "#F0883E"
    BORDER = "#30363D"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 ADK AGENT — Agente Pessoal Multimodal")
        self.root.configure(bg=self.BG_DARK)
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)

        # Estado
        self.is_connected = False
        self.mic_muted = False
        self.screen_enabled = True
        self.preview_image = None

        # Callbacks (serão preenchidos pelo main.py)
        self.on_connect = None
        self.on_disconnect = None
        self.on_toggle_mic = None
        self.on_toggle_screen = None
        self.on_send_text = None

        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        """Configura estilos ttk."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Dark.TFrame", background=self.BG_DARK)
        self.style.configure("Card.TFrame", background=self.BG_CARD)
        self.style.configure(
            "Dark.TLabel",
            background=self.BG_DARK,
            foreground=self.TEXT_PRIMARY,
            font=("Segoe UI", 10)
        )
        self.style.configure(
            "Title.TLabel",
            background=self.BG_DARK,
            foreground=self.ACCENT_BLUE,
            font=("Segoe UI", 18, "bold")
        )
        self.style.configure(
            "Subtitle.TLabel",
            background=self.BG_DARK,
            foreground=self.TEXT_SECONDARY,
            font=("Segoe UI", 9)
        )
        self.style.configure(
            "Card.TLabel",
            background=self.BG_CARD,
            foreground=self.TEXT_PRIMARY,
            font=("Segoe UI", 10)
        )

    def _build_ui(self):
        """Constrói a interface."""
        # ─── Header ────────────────────────────
        header_frame = tk.Frame(self.root, bg=self.BG_DARK, pady=10, padx=20)
        header_frame.pack(fill="x")

        tk.Label(
            header_frame, text="🤖 ADK AGENT",
            bg=self.BG_DARK, fg=self.ACCENT_BLUE,
            font=("Segoe UI", 22, "bold")
        ).pack(side="left")

        tk.Label(
            header_frame, text="  Agente Pessoal Multimodal — Gemini Live API",
            bg=self.BG_DARK, fg=self.TEXT_SECONDARY,
            font=("Segoe UI", 11)
        ).pack(side="left", padx=(5, 0))

        # Status indicator
        self.status_label = tk.Label(
            header_frame, text="⚫ Desconectado",
            bg=self.BG_DARK, fg=self.TEXT_SECONDARY,
            font=("Segoe UI", 10)
        )
        self.status_label.pack(side="right")

        # Separator
        tk.Frame(self.root, bg=self.BORDER, height=1).pack(fill="x")

        # ─── Main Container ────────────────────
        main_frame = tk.Frame(self.root, bg=self.BG_DARK)
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Left Panel (Controls + Preview)
        left_panel = tk.Frame(main_frame, bg=self.BG_DARK, width=350)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)

        self._build_controls(left_panel)
        self._build_preview(left_panel)
        self._build_skills_log(left_panel)

        # Right Panel (Chat)
        right_panel = tk.Frame(main_frame, bg=self.BG_DARK)
        right_panel.pack(side="right", fill="both", expand=True)

        self._build_chat(right_panel)

    def _build_controls(self, parent):
        """Constrói painel de controles."""
        # Card frame
        card = tk.Frame(parent, bg=self.BG_CARD, bd=0, highlightthickness=1,
                       highlightbackground=self.BORDER, highlightcolor=self.BORDER)
        card.pack(fill="x", pady=(0, 10))

        inner = tk.Frame(card, bg=self.BG_CARD, padx=15, pady=12)
        inner.pack(fill="x")

        tk.Label(
            inner, text="⚡ Controles",
            bg=self.BG_CARD, fg=self.ACCENT_PURPLE,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        # Botão Conectar/Desconectar
        btn_frame = tk.Frame(inner, bg=self.BG_CARD, pady=8)
        btn_frame.pack(fill="x")

        self.connect_btn = tk.Button(
            btn_frame, text="▶  INICIAR AGENTE",
            bg=self.ACCENT_GREEN, fg="#FFFFFF",
            font=("Segoe UI", 11, "bold"),
            activebackground="#2EA043", activeforeground="#FFFFFF",
            relief="flat", cursor="hand2", pady=8,
            command=self._toggle_connection
        )
        self.connect_btn.pack(fill="x")

        # Botões Mic e Tela
        toggle_frame = tk.Frame(inner, bg=self.BG_CARD, pady=4)
        toggle_frame.pack(fill="x")

        self.mic_btn = tk.Button(
            toggle_frame, text="🎤 Mic ON",
            bg=self.BG_INPUT, fg=self.ACCENT_GREEN,
            font=("Segoe UI", 10), relief="flat",
            cursor="hand2", pady=5,
            command=self._toggle_mic
        )
        self.mic_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.screen_btn = tk.Button(
            toggle_frame, text="🖥️ Tela ON",
            bg=self.BG_INPUT, fg=self.ACCENT_GREEN,
            font=("Segoe UI", 10), relief="flat",
            cursor="hand2", pady=5,
            command=self._toggle_screen
        )
        self.screen_btn.pack(side="right", fill="x", expand=True, padx=(4, 0))

    def _build_preview(self, parent):
        """Constrói preview da tela."""
        card = tk.Frame(parent, bg=self.BG_CARD, bd=0, highlightthickness=1,
                       highlightbackground=self.BORDER, highlightcolor=self.BORDER)
        card.pack(fill="x", pady=(0, 10))

        inner = tk.Frame(card, bg=self.BG_CARD, padx=15, pady=12)
        inner.pack(fill="x")

        tk.Label(
            inner, text="👁️ Visão do Agente",
            bg=self.BG_CARD, fg=self.ACCENT_ORANGE,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 8))

        self.preview_canvas = tk.Canvas(
            inner, width=320, height=180,
            bg="#000000", highlightthickness=0
        )
        self.preview_canvas.pack()
        self.preview_canvas.create_text(
            160, 90, text="Aguardando conexão...",
            fill=self.TEXT_SECONDARY, font=("Segoe UI", 10)
        )

    def _build_skills_log(self, parent):
        """Constrói log de skills executadas."""
        card = tk.Frame(parent, bg=self.BG_CARD, bd=0, highlightthickness=1,
                       highlightbackground=self.BORDER, highlightcolor=self.BORDER)
        card.pack(fill="both", expand=True)

        inner = tk.Frame(card, bg=self.BG_CARD, padx=15, pady=12)
        inner.pack(fill="both", expand=True)

        tk.Label(
            inner, text="🔧 Skills Executadas",
            bg=self.BG_CARD, fg=self.ACCENT_BLUE,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 8))

        self.skills_log = scrolledtext.ScrolledText(
            inner, width=35, height=8,
            bg="#0D1117", fg=self.TEXT_SECONDARY,
            font=("Cascadia Code", 8),
            relief="flat", insertbackground=self.TEXT_PRIMARY,
            selectbackground=self.ACCENT_BLUE,
            wrap="word", state="disabled"
        )
        self.skills_log.pack(fill="both", expand=True)

    def _build_chat(self, parent):
        """Constrói área de chat."""
        # Card frame
        card = tk.Frame(parent, bg=self.BG_CARD, bd=0, highlightthickness=1,
                       highlightbackground=self.BORDER, highlightcolor=self.BORDER)
        card.pack(fill="both", expand=True)

        inner = tk.Frame(card, bg=self.BG_CARD, padx=15, pady=12)
        inner.pack(fill="both", expand=True)

        # Header do chat
        chat_header = tk.Frame(inner, bg=self.BG_CARD)
        chat_header.pack(fill="x", pady=(0, 10))

        tk.Label(
            chat_header, text="💬 Chat — Respostas do Agente",
            bg=self.BG_CARD, fg=self.ACCENT_GREEN,
            font=("Segoe UI", 13, "bold")
        ).pack(side="left")

        # Área de texto do chat
        self.chat_display = scrolledtext.ScrolledText(
            inner, width=50, height=20,
            bg=self.BG_DARK, fg=self.TEXT_PRIMARY,
            font=("Segoe UI", 11),
            relief="flat", insertbackground=self.TEXT_PRIMARY,
            selectbackground=self.ACCENT_BLUE,
            wrap="word", state="disabled",
            padx=10, pady=10
        )
        self.chat_display.pack(fill="both", expand=True)

        # Tags para formatação
        self.chat_display.tag_config("agent", foreground=self.ACCENT_GREEN)
        self.chat_display.tag_config("user", foreground=self.ACCENT_BLUE)
        self.chat_display.tag_config("system", foreground=self.ACCENT_ORANGE)
        self.chat_display.tag_config("timestamp", foreground=self.TEXT_SECONDARY)

        # Input frame
        input_frame = tk.Frame(inner, bg=self.BG_CARD, pady=10)
        input_frame.pack(fill="x")

        self.text_input = tk.Entry(
            input_frame,
            bg=self.BG_INPUT, fg=self.TEXT_PRIMARY,
            font=("Segoe UI", 11),
            relief="flat", insertbackground=self.TEXT_PRIMARY,
            selectbackground=self.ACCENT_BLUE
        )
        self.text_input.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.text_input.bind("<Return>", self._send_text)
        self.text_input.insert(0, "Digite uma mensagem ou fale pelo microfone...")
        self.text_input.bind("<FocusIn>", self._clear_placeholder)
        self.text_input.bind("<FocusOut>", self._restore_placeholder)

        send_btn = tk.Button(
            input_frame, text="📤 Enviar",
            bg=self.ACCENT_BLUE, fg="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            activebackground="#1F6FEB", activeforeground="#FFFFFF",
            relief="flat", cursor="hand2", padx=15, pady=5,
            command=lambda: self._send_text(None)
        )
        send_btn.pack(side="right")

    # ═══════════════════════════════════════════════════
    # Callbacks e ações
    # ═══════════════════════════════════════════════════

    def _toggle_connection(self):
        """Alterna entre conectar e desconectar."""
        if not self.is_connected:
            self.connect_btn.config(text="⏳ Conectando...", bg=self.ACCENT_ORANGE, state="disabled")
            if self.on_connect:
                self.on_connect()
        else:
            if self.on_disconnect:
                self.on_disconnect()

    def _toggle_mic(self):
        """Alterna mute do microfone."""
        if self.on_toggle_mic:
            self.on_toggle_mic()

    def _toggle_screen(self):
        """Alterna captura de tela."""
        self.screen_enabled = not self.screen_enabled
        if self.screen_enabled:
            self.screen_btn.config(text="🖥️ Tela ON", fg=self.ACCENT_GREEN)
        else:
            self.screen_btn.config(text="🖥️ Tela OFF", fg=self.ACCENT_RED)
        if self.on_toggle_screen:
            self.on_toggle_screen(self.screen_enabled)

    def _send_text(self, event):
        """Envia texto digitado."""
        text = self.text_input.get().strip()
        placeholder = "Digite uma mensagem ou fale pelo microfone..."
        if text and text != placeholder:
            self.add_chat_message(f"Você: {text}", "user")
            self.text_input.delete(0, "end")
            if self.on_send_text:
                self.on_send_text(text)

    def _clear_placeholder(self, event):
        placeholder = "Digite uma mensagem ou fale pelo microfone..."
        if self.text_input.get() == placeholder:
            self.text_input.delete(0, "end")
            self.text_input.config(fg=self.TEXT_PRIMARY)

    def _restore_placeholder(self, event):
        if not self.text_input.get():
            self.text_input.insert(0, "Digite uma mensagem ou fale pelo microfone...")
            self.text_input.config(fg=self.TEXT_SECONDARY)

    # ═══════════════════════════════════════════════════
    # Métodos públicos (thread-safe)
    # ═══════════════════════════════════════════════════

    def set_connected(self, connected: bool):
        """Atualiza estado de conexão (thread-safe)."""
        def _update():
            self.is_connected = connected
            if connected:
                self.connect_btn.config(
                    text="⏹  PARAR AGENTE",
                    bg=self.ACCENT_RED, state="normal"
                )
                self.status_label.config(text="🟢 Conectado", fg=self.ACCENT_GREEN)
            else:
                self.connect_btn.config(
                    text="▶  INICIAR AGENTE",
                    bg=self.ACCENT_GREEN, state="normal"
                )
                self.status_label.config(text="⚫ Desconectado", fg=self.TEXT_SECONDARY)
        self.root.after(0, _update)

    def update_status(self, text: str):
        """Atualiza o status (thread-safe)."""
        def _update():
            self.status_label.config(text=text)
        self.root.after(0, _update)

    def add_chat_message(self, message: str, tag: str = "agent"):
        """Adiciona mensagem ao chat (thread-safe)."""
        def _update():
            self.chat_display.config(state="normal")
            self.chat_display.insert("end", message + "\n", tag)
            self.chat_display.see("end")
            self.chat_display.config(state="disabled")
        self.root.after(0, _update)

    def add_skill_log(self, message: str):
        """Adiciona log de skill (thread-safe)."""
        def _update():
            self.skills_log.config(state="normal")
            self.skills_log.insert("end", message + "\n")
            self.skills_log.see("end")
            self.skills_log.config(state="disabled")
        self.root.after(0, _update)

    def update_mic_state(self, muted: bool):
        """Atualiza estado visual do microfone."""
        def _update():
            self.mic_muted = muted
            if muted:
                self.mic_btn.config(text="🎤 Mic OFF", fg=self.ACCENT_RED)
            else:
                self.mic_btn.config(text="🎤 Mic ON", fg=self.ACCENT_GREEN)
        self.root.after(0, _update)

    def update_preview(self, pil_image):
        """Atualiza preview da tela (thread-safe)."""
        def _update():
            try:
                self.preview_image = ImageTk.PhotoImage(pil_image)
                self.preview_canvas.delete("all")
                self.preview_canvas.create_image(0, 0, anchor="nw", image=self.preview_image)
            except Exception:
                pass
        self.root.after(0, _update)

    def run(self):
        """Inicia o loop principal do Tkinter."""
        self.root.mainloop()

    def destroy(self):
        """Fecha a janela."""
        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass
