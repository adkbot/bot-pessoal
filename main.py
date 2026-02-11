"""
ADK AGENT — Ponto de entrada principal.
Conecta a GUI, captura de tela, áudio e o agente Gemini Live API.
"""

import asyncio
import threading
import os
import sys
import traceback
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

from gui import AgentGUI
from agent_core import AgentCore
from screen_capture import ScreenCapture
from audio_capture import AudioCapture


class ADKAgent:
    """Orquestrador principal do sistema."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.gui = AgentGUI()
        self.agent = None
        self.screen = ScreenCapture(fps=1.0)
        self.audio = AudioCapture()
        self.loop = None
        self._agent_thread = None

        # Conectar callbacks da GUI
        self.gui.on_connect = self._start_agent
        self.gui.on_disconnect = self._stop_agent
        self.gui.on_toggle_mic = self._toggle_mic
        self.gui.on_toggle_screen = self._toggle_screen
        self.gui.on_send_text = self._send_text

        # Mensagem inicial
        self.gui.add_chat_message(
            "🤖 ADK AGENT pronto! Clique em INICIAR para conectar.", "system"
        )
        self.gui.add_chat_message(
            "💡 Você pode falar pelo microfone ou digitar mensagens.", "system"
        )
        self.gui.add_chat_message(
            "🔧 18 Skills disponíveis: terminal, arquivos, instalação, "
            "processos, apps, busca e mais!", "system"
        )

    def _start_agent(self):
        """Inicia o agente em uma thread separada."""
        if not self.api_key:
            self.gui.update_status("❌ API Key não encontrada no .env")
            self.gui.add_chat_message(
                "❌ Configure sua GEMINI_API_KEY no arquivo .env", "system"
            )
            self.gui.set_connected(False)
            return

        # Recriar captura para novo ciclo
        self.screen = ScreenCapture(fps=1.0)
        self.audio = AudioCapture()

        self._agent_thread = threading.Thread(target=self._run_agent_loop, daemon=True)
        self._agent_thread.start()

    def _run_agent_loop(self):
        """Executa o loop assíncrono do agente."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_until_complete(self._agent_main())
        except Exception as e:
            print(f"[Main] Erro fatal: {e}")
            traceback.print_exc()
            self.gui.update_status(f"❌ Erro: {e}")
            self.gui.add_chat_message(f"❌ Erro: {e}", "system")
        finally:
            try:
                self.loop.close()
            except Exception:
                pass
            self.gui.set_connected(False)

    async def _agent_main(self):
        """Função principal assíncrona do agente."""
        # Criar agente com callbacks
        self.agent = AgentCore(
            api_key=self.api_key,
            on_text=self._on_agent_text,
            on_status=self._on_status,
            on_skill_log=self._on_skill_log
        )

        self.gui.set_connected(True)

        # Rodar tudo em paralelo: sessão Gemini + captura + preview
        try:
            async with asyncio.TaskGroup() as tg:
                # Sessão Gemini (contém send/receive loops internamente)
                tg.create_task(self.agent.run_with_reconnect())

                # Aguardar conexão antes de iniciar captura
                await asyncio.sleep(2)

                # Captura de áudio do microfone -> fila do agente
                tg.create_task(self.audio.stream_mic(self.agent.audio_input_queue))

                # Captura de tela -> fila do agente
                tg.create_task(self.screen.stream_frames(self.agent.screen_input_queue))

                # Reproduzir áudio de resposta
                tg.create_task(self.audio.play_audio(self.agent.audio_output_queue))

                # Preview da tela na GUI
                tg.create_task(self._update_preview_loop())

        except* Exception as eg:
            for e in eg.exceptions:
                if not isinstance(e, asyncio.CancelledError):
                    print(f"[Main] Task error: {e}")
                    self.gui.add_chat_message(f"⚠️ {e}", "system")

        self.gui.set_connected(False)

    async def _update_preview_loop(self):
        """Atualiza o preview da tela na GUI periodicamente."""
        while self.agent and self.agent.running:
            try:
                if self.gui.screen_enabled:
                    img = await asyncio.to_thread(self.screen.capture_frame_pil)
                    self.gui.update_preview(img)
            except Exception:
                pass
            await asyncio.sleep(2.0)

    def _stop_agent(self):
        """Para o agente."""
        self.gui.update_status("🔄 Desconectando...")

        if self.agent:
            self.agent.stop()
        self.screen.stop()
        self.audio.stop()

        self.gui.set_connected(False)
        self.gui.update_status("⚫ Desconectado")

    def _toggle_mic(self):
        """Alterna mute do microfone."""
        muted = self.audio.toggle_mic()
        self.gui.update_mic_state(muted)

    def _toggle_screen(self, enabled):
        """Alterna captura de tela."""
        self.screen.running = enabled

    def _send_text(self, text: str):
        """Envia texto digitado ao agente."""
        if self.agent and self.agent.session and self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.agent.send_text(text), self.loop
            )
        else:
            self.gui.add_chat_message(
                "⚠️ Agente não conectado! Clique em ▶ INICIAR AGENTE primeiro.", "system"
            )

    # ══════ Callbacks do AgentCore ══════

    def _on_agent_text(self, text: str):
        self.gui.add_chat_message(f"🤖 {text}", "agent")

    def _on_status(self, text: str):
        self.gui.update_status(text)

    def _on_skill_log(self, text: str):
        self.gui.add_skill_log(text)

    def run(self):
        """Inicia o aplicativo."""
        try:
            self.gui.run()
        except KeyboardInterrupt:
            pass
        finally:
            self._stop_agent()


if __name__ == "__main__":
    app = ADKAgent()
    app.run()
