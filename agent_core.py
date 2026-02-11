"""
Agent Core — Conexão com Gemini Multimodal Live API.
Com auto-reconnect e tratamento de sessão expirada.
"""

import asyncio
import base64
import json
import traceback
from google import genai
from google.genai import types
from skills import TOOL_DECLARATIONS, executar_skill
from memory import salvar_mensagem, obter_resumo_contexto


class AgentCore:
    """Agente multimodal com Gemini Live API + auto-reconnect."""

    MAX_RECONNECT_ATTEMPTS = 10
    RECONNECT_DELAY = 3  # segundos

    def __init__(self, api_key: str, on_text=None, on_status=None, on_skill_log=None):
        self.client = genai.Client(api_key=api_key)
        self.on_text = on_text or (lambda t: None)
        self.on_status = on_status or (lambda s: None)
        self.on_skill_log = on_skill_log or (lambda s: None)

        self.session = None
        self.running = False
        self._session_alive = False

        # Filas
        self.audio_input_queue = asyncio.Queue(maxsize=5)
        self.screen_input_queue = asyncio.Queue(maxsize=2)
        self.audio_output_queue = asyncio.Queue()

        # Modelo
        self.model = "gemini-2.5-flash-native-audio-preview-12-2025"

        # Tools
        self._tool_declarations = TOOL_DECLARATIONS

        # System instruction base
        self._system_base = (
            "Você é o ADK AGENT — o agente pessoal SUPREMO com controle TOTAL do computador. "
            "Você fala português do Brasil. "
            "\n\nSUAS CAPACIDADES:\n"
            "- Controle TOTAL do PC: terminal, arquivos, apps, processos, desligar/reiniciar\n"
            "- MOUSE e TECLADO: clicar, digitar, pressionar teclas, interagir com qualquer app\n"
            "- 🎯 VISÃO COMPUTACIONAL: OCR (ler texto na tela), localizar elementos, clicar automaticamente\n"
            "- INTERNET: pesquisar no Google, ler páginas web, baixar arquivos\n"
            "- CÓDIGO: escrever e executar código em QUALQUER linguagem (Python, JS, MQL5, HTML, etc)\n"
            "- VÍDEOS: você VÊ a tela em tempo real. Para assistir vídeos, use controlar_mouse_teclado para clicar no play, pausar, avançar. Assista quantas vezes precisar para entender completamente.\n"
            "- MEMÓRIA PERMANENTE: salve TUDO que aprender com salvar_nota e salvar_aprendizado. Você NUNCA esquece.\n"
            "- TAREFAS: salve tarefas pendentes. Mesmo que o PC desligue, você lembra ao reconectar.\n"
            "\n\n🎯 NOVO! VISÃO COMPUTACIONAL:\n"
            "- detectar_texto_tela: Vê TODOS os textos na tela com OCR\n"
            "- localizar_texto: Encontra texto específico e retorna coordenadas EXATAS\n"
            "- localizar_elemento: Encontra ícones/botões por imagem template\n"
            "- clicar_em_texto: COMBO! Localiza texto via OCR + clica automaticamente\n"
            "- salvar_screenshot_debug: Salva screenshot com anotações para debug\n"
            "\n\nREGRAS:\n"
            "1. SEMPRE que aprender algo novo (de vídeo, pesquisa, ou conversa), use salvar_aprendizado\n"
            "2. SEMPRE que o usuário pedir para lembrar algo, use salvar_nota\n"
            "3. Quando tiver dúvida, pesquise na internet AUTOMATICAMENTE antes de responder\n"
            "4. Para vídeos: assista pela tela, pause, analise frame por frame se precisar\n"
            "5. Execute ações DE VERDADE, não apenas descreva\n"
            "6. Para ações destrutivas, confirme com o usuário primeiro\n"
            "7. Use historico_conversa quando o usuário pedir para continuar algo anterior\n"
            "8. Seja proativo: se algo falhar, busque soluções online e tente novamente\n"
            "\n\n🎯 REGRAS DE INTERAÇÃO COM APLICATIVOS (CRÍTICO!):\n"
            "9. NUNCA adivinhe coordenadas de clique! SEMPRE use localizar_texto ou detectar_texto_tela primeiro\n"
            "10. Para clicar em botões/campos: use clicar_em_texto('nome do botão') - é automático!\n"
            "11. Para enviar mensagens em apps: (1) localizar_texto para achar campo, (2) clicar, (3) digitar\n"
            "12. Para gráficos/trading: use localizar_elemento com imagem da ferramenta como template\n"
            "13. Se não encontrar elemento, use detectar_texto_tela para ver TUDO na tela e ajustar busca\n"
            "14. Sempre confirme se encontrou o elemento ANTES de clicar (verificar 'encontrado': true)\n"
        )

    def _build_system_instruction(self):
        """Constrói system instruction com contexto da memória."""
        contexto = obter_resumo_contexto()
        return self._system_base + f"\n\n═══ MEMÓRIA DO AGENTE ═══\n{contexto}"

    def _build_config(self):
        """Constrói config como dict — formato oficial Google."""
        config = {
            "response_modalities": ["AUDIO"],
            "system_instruction": self._build_system_instruction(),
        }

        # Adicionar tools
        if self._tool_declarations:
            try:
                func_decls = []
                for decl in self._tool_declarations:
                    func_decls.append(types.FunctionDeclaration(
                        name=decl["name"],
                        description=decl["description"],
                        parameters=decl.get("parameters")
                    ))
                config["tools"] = [types.Tool(function_declarations=func_decls)]
            except Exception as e:
                print(f"[AgentCore] Aviso tools: {e}")

        return config

    def _clear_queues(self):
        """Limpa todas as filas."""
        for q in [self.audio_input_queue, self.screen_input_queue, self.audio_output_queue]:
            while not q.empty():
                try:
                    q.get_nowait()
                except asyncio.QueueEmpty:
                    break

    async def run_with_reconnect(self):
        """Loop principal com auto-reconnect."""
        self.running = True
        attempt = 0

        while self.running and attempt < self.MAX_RECONNECT_ATTEMPTS:
            try:
                if attempt > 0:
                    self.on_status(f"🔄 Reconectando (tentativa {attempt + 1})...")
                    self.on_text(f"🔄 Reconectando ao Gemini... (tentativa {attempt + 1})")
                    await asyncio.sleep(self.RECONNECT_DELAY)
                else:
                    self.on_status("🔄 Conectando ao Gemini...")

                await self._run_single_session()

                # Se saiu normalmente (stop chamado), não reconectar
                if not self.running:
                    break

                # Sessão expirou, reconectar
                attempt += 1
                self._clear_queues()
                self.on_text("⚠️ Sessão expirou. Reconectando automaticamente...")
                print(f"[AgentCore] Sessão expirou, reconectando (tentativa {attempt})")

            except Exception as e:
                attempt += 1
                print(f"[AgentCore] Erro fatal sessão: {e}")
                if self.running:
                    self.on_text(f"⚠️ Erro: {str(e)[:100]}. Reconectando...")
                    await asyncio.sleep(self.RECONNECT_DELAY)

        if attempt >= self.MAX_RECONNECT_ATTEMPTS:
            self.on_text("❌ Número máximo de reconexões atingido. Clique em INICIAR para reconectar manualmente.")
            self.on_status("❌ Desconectado — reconexões esgotadas")

        self.running = False
        self._session_alive = False
        self.session = None

    async def _run_single_session(self):
        """Roda uma única sessão Live API."""
        config = self._build_config()

        async with self.client.aio.live.connect(
            model=self.model,
            config=config
        ) as session:
            self.session = session
            self._session_alive = True
            self.on_status("🟢 Conectado ao Gemini!")
            self.on_text("✅ Conectado! Fale ou digite suas mensagens.")
            print("[AgentCore] Sessão Live API conectada!")

            try:
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(self._send_audio_loop())
                    tg.create_task(self._send_screen_loop())
                    tg.create_task(self._receive_loop())
            except* Exception as eg:
                for e in eg.exceptions:
                    if not isinstance(e, asyncio.CancelledError):
                        print(f"[AgentCore] Task error: {e}")
            finally:
                self._session_alive = False
                self.session = None
                self.on_status("⚫ Sessão encerrada")

    async def _send_audio_loop(self):
        """Envia áudio do mic para o Gemini."""
        while self.running and self._session_alive:
            try:
                msg = await asyncio.wait_for(self.audio_input_queue.get(), timeout=1.0)
                if self.session and self._session_alive:
                    await self.session.send_realtime_input(audio=msg)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                if self.running and self._session_alive:
                    print(f"[AgentCore] Erro áudio: {e}")
                    self._session_alive = False  # Sinaliza reconexão
                    return

    async def _send_screen_loop(self):
        """Envia frames da tela para o Gemini."""
        while self.running and self._session_alive:
            try:
                frame_b64 = await asyncio.wait_for(self.screen_input_queue.get(), timeout=2.0)
                if self.session and self._session_alive:
                    raw_bytes = base64.b64decode(frame_b64)
                    await self.session.send_realtime_input(
                        media=types.Blob(data=raw_bytes, mime_type="image/jpeg")
                    )
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                if self.running and self._session_alive:
                    print(f"[AgentCore] Erro tela: {e}")
                    self._session_alive = False
                    return

    async def _receive_loop(self):
        """Recebe respostas do Gemini."""
        while self.running and self._session_alive:
            try:
                if not self.session:
                    await asyncio.sleep(0.5)
                    continue

                turn = self.session.receive()
                async for response in turn:
                    if not self._session_alive:
                        return
                    try:
                        # Content do modelo
                        if response.server_content and response.server_content.model_turn:
                            for part in response.server_content.model_turn.parts:
                                if part.inline_data and isinstance(part.inline_data.data, bytes):
                                    self.audio_output_queue.put_nowait(part.inline_data.data)
                                if part.text:
                                    self.on_text(part.text)
                                    salvar_mensagem("agent", part.text)

                        # Function calls
                        if response.tool_call:
                            await self._handle_tool_calls(response.tool_call)

                        # Interrupção
                        if response.server_content and response.server_content.interrupted:
                            while not self.audio_output_queue.empty():
                                self.audio_output_queue.get_nowait()
                    except Exception as inner_e:
                        print(f"[AgentCore] Erro processando: {inner_e}")

            except Exception as e:
                if self.running and self._session_alive:
                    print(f"[AgentCore] Erro recebendo: {e}")
                    self._session_alive = False  # Sinaliza reconexão
                    return

    async def _handle_tool_calls(self, tool_call):
        """Executa function calls do Gemini."""
        function_responses = []
        for fc in tool_call.function_calls:
            nome = fc.name
            params = dict(fc.args) if fc.args else {}

            self.on_skill_log(f"🔧 {nome}({json.dumps(params, ensure_ascii=False)[:200]})")

            try:
                resultado = await asyncio.to_thread(executar_skill, nome, params)
                self.on_skill_log(f"✅ {resultado[:300]}")
            except Exception as e:
                resultado = json.dumps({"sucesso": False, "mensagem": str(e)})
                self.on_skill_log(f"❌ Erro: {e}")

            # Incluir o ID do function call (obrigatório na API)
            fr_kwargs = {"name": nome, "response": {"result": resultado}}
            if hasattr(fc, "id") and fc.id:
                fr_kwargs["id"] = fc.id
            function_responses.append(types.FunctionResponse(**fr_kwargs))

        if self.session and self._session_alive and function_responses:
            try:
                await self.session.send_tool_response(
                    function_responses=function_responses
                )
            except Exception as e:
                print(f"[AgentCore] Erro tool response: {e}")
                self._session_alive = False

    async def send_text(self, text: str):
        """Envia texto ao Gemini."""
        if self.session and self._session_alive:
            try:
                await self.session.send_client_content(
                    turns=types.Content(
                        role="user",
                        parts=[types.Part(text=text)]
                    )
                )
                salvar_mensagem("user", text)
            except Exception as e:
                self.on_text(f"⚠️ Sessão expirou. Reconectando...")
                print(f"[AgentCore] Erro send_text: {e}")
                self._session_alive = False  # Sinaliza reconexão
        else:
            self.on_text("⚠️ Não conectado! Aguarde a reconexão ou clique INICIAR.")

    def stop(self):
        """Para o agente e previne reconexão."""
        self.running = False
        self._session_alive = False
