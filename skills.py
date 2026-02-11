"""
Skills do Agente — 30+ Skills de Controle Total.
Cada skill é uma função que o agente pode chamar via function calling do Gemini.
Inclui: terminal, arquivos, internet, código, memória, PC control, mouse/teclado.
"""

import os
import subprocess
import shutil
import glob
import psutil
import json
import time
import tempfile
from datetime import datetime

# Import memória
from memory import (
    salvar_nota, buscar_notas, listar_notas, deletar_nota,
    salvar_tarefa, concluir_tarefa, listar_tarefas,
    salvar_aprendizado, buscar_aprendizados, obter_historico
)


# ═══════════════════════════════════════════════════════════════════
#  SKILL 1: Executar comandos no terminal
# ═══════════════════════════════════════════════════════════════════

def executar_comando(comando: str, diretorio: str = None) -> dict:
    """Executa um comando no terminal (PowerShell/CMD)."""
    try:
        result = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            cwd=diretorio,
            timeout=120
        )
        return {
            "sucesso": result.returncode == 0,
            "saida": result.stdout[:5000] if result.stdout else "",
            "erro": result.stderr[:2000] if result.stderr else "",
            "codigo": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"sucesso": False, "saida": "", "erro": "Timeout (120s)", "codigo": -1}
    except Exception as e:
        return {"sucesso": False, "saida": "", "erro": str(e), "codigo": -1}


# ═══════════════════════════════════════════════════════════════════
#  SKILL 2-8: Gerenciamento de arquivos
# ═══════════════════════════════════════════════════════════════════

def criar_arquivo(caminho: str, conteudo: str) -> dict:
    """Cria ou sobrescreve um arquivo."""
    try:
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(conteudo)
        return {"sucesso": True, "mensagem": f"Arquivo criado: {caminho}"}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


def ler_arquivo(caminho: str) -> dict:
    """Lê conteúdo de um arquivo."""
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()
        return {"sucesso": True, "conteudo": conteudo[:10000], "tamanho": len(conteudo)}
    except Exception as e:
        return {"sucesso": False, "conteudo": "", "mensagem": str(e)}


def editar_arquivo(caminho: str, texto_antigo: str, texto_novo: str) -> dict:
    """Edita arquivo substituindo texto."""
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()
        if texto_antigo not in conteudo:
            return {"sucesso": False, "mensagem": "Texto não encontrado no arquivo"}
        conteudo = conteudo.replace(texto_antigo, texto_novo)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(conteudo)
        return {"sucesso": True, "mensagem": f"Arquivo editado: {caminho}"}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


def deletar_arquivo(caminho: str) -> dict:
    """Deleta um arquivo ou pasta."""
    try:
        if os.path.isfile(caminho):
            os.remove(caminho)
            return {"sucesso": True, "mensagem": f"Arquivo deletado: {caminho}"}
        elif os.path.isdir(caminho):
            shutil.rmtree(caminho)
            return {"sucesso": True, "mensagem": f"Pasta deletada: {caminho}"}
        else:
            return {"sucesso": False, "mensagem": "Caminho não encontrado"}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


def listar_arquivos(diretorio: str, padrao: str = "*") -> dict:
    """Lista arquivos em um diretório."""
    try:
        caminho = os.path.join(diretorio, padrao)
        arquivos = glob.glob(caminho, recursive=True)
        itens = []
        for arq in arquivos[:100]:
            info = {
                "nome": os.path.basename(arq),
                "caminho": arq,
                "tipo": "pasta" if os.path.isdir(arq) else "arquivo",
                "tamanho_kb": round(os.path.getsize(arq) / 1024, 1) if os.path.isfile(arq) else 0
            }
            itens.append(info)
        return {"sucesso": True, "itens": itens, "total": len(itens)}
    except Exception as e:
        return {"sucesso": False, "itens": [], "mensagem": str(e)}


def mover_arquivo(origem: str, destino: str) -> dict:
    """Move ou renomeia arquivo/pasta."""
    try:
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.move(origem, destino)
        return {"sucesso": True, "mensagem": f"Movido: {origem} → {destino}"}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


def copiar_arquivo(origem: str, destino: str) -> dict:
    """Copia arquivo/pasta."""
    try:
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        if os.path.isdir(origem):
            shutil.copytree(origem, destino)
        else:
            shutil.copy2(origem, destino)
        return {"sucesso": True, "mensagem": f"Copiado: {origem} → {destino}"}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


def criar_pasta(caminho: str) -> dict:
    """Cria pasta e subpastas."""
    try:
        os.makedirs(caminho, exist_ok=True)
        return {"sucesso": True, "mensagem": f"Pasta criada: {caminho}"}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  SKILL 9-10: Instalar pacotes e programas
# ═══════════════════════════════════════════════════════════════════

def instalar_pacote_pip(pacote: str) -> dict:
    """Instala pacote Python via pip."""
    return executar_comando(f"pip install {pacote}")


def instalar_programa(comando_instalacao: str) -> dict:
    """Instala programa usando qualquer comando."""
    return executar_comando(comando_instalacao)


# ═══════════════════════════════════════════════════════════════════
#  SKILL 11-13: Sistema e processos
# ═══════════════════════════════════════════════════════════════════

def info_sistema() -> dict:
    """Informações do sistema."""
    try:
        return {
            "sucesso": True,
            "cpu_percent": psutil.cpu_percent(interval=1),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
            "ram_usada_gb": round(psutil.virtual_memory().used / (1024**3), 1),
            "ram_percent": psutil.virtual_memory().percent,
            "disco_total_gb": round(psutil.disk_usage('C:\\').total / (1024**3), 1),
            "disco_usado_gb": round(psutil.disk_usage('C:\\').used / (1024**3), 1),
            "disco_percent": psutil.disk_usage('C:\\').percent,
            "processos_ativos": len(psutil.pids()),
            "usuario": os.getlogin(),
            "diretorio_atual": os.getcwd()
        }
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


def listar_processos(filtro: str = None) -> dict:
    """Lista processos em execução."""
    try:
        processos = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                if filtro and filtro.lower() not in info['name'].lower():
                    continue
                processos.append({
                    "pid": info['pid'],
                    "nome": info['name'],
                    "cpu": info['cpu_percent'],
                    "memoria": round(info['memory_percent'], 1)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        processos.sort(key=lambda x: x.get('cpu', 0), reverse=True)
        return {"sucesso": True, "processos": processos[:50], "total": len(processos)}
    except Exception as e:
        return {"sucesso": False, "processos": [], "mensagem": str(e)}


def finalizar_processo(pid: int = None, nome: str = None) -> dict:
    """Finaliza processo por PID ou nome."""
    try:
        if pid:
            proc = psutil.Process(pid)
            proc.terminate()
            return {"sucesso": True, "mensagem": f"Processo {pid} finalizado"}
        elif nome:
            count = 0
            for proc in psutil.process_iter(['name']):
                if nome.lower() in proc.info['name'].lower():
                    proc.terminate()
                    count += 1
            return {"sucesso": True, "mensagem": f"{count} processo(s) '{nome}' finalizados"}
        return {"sucesso": False, "mensagem": "Forneça PID ou nome"}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  SKILL 14-15: Abrir apps e URLs
# ═══════════════════════════════════════════════════════════════════

def abrir_aplicativo(caminho_ou_nome: str) -> dict:
    """Abre um aplicativo ou arquivo."""
    try:
        os.startfile(caminho_ou_nome)
        return {"sucesso": True, "mensagem": f"Abrindo: {caminho_ou_nome}"}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


def abrir_url(url: str) -> dict:
    """Abre URL no navegador."""
    try:
        import webbrowser
        webbrowser.open(url)
        return {"sucesso": True, "mensagem": f"URL aberta: {url}"}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  SKILL 16-17: Pesquisa de arquivos
# ═══════════════════════════════════════════════════════════════════

def pesquisar_arquivos(diretorio: str, termo: str, extensoes: str = None) -> dict:
    """Pesquisa arquivos por nome."""
    try:
        resultados = []
        ext_list = extensoes.split(",") if extensoes else None
        for root, dirs, files in os.walk(diretorio):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            for name in files:
                if termo.lower() in name.lower():
                    if ext_list and not any(name.endswith(e.strip()) for e in ext_list):
                        continue
                    caminho = os.path.join(root, name)
                    resultados.append({
                        "nome": name,
                        "caminho": caminho,
                        "tamanho_kb": round(os.path.getsize(caminho) / 1024, 1)
                    })
                    if len(resultados) >= 50:
                        break
            if len(resultados) >= 50:
                break
        return {"sucesso": True, "resultados": resultados, "total": len(resultados)}
    except Exception as e:
        return {"sucesso": False, "resultados": [], "mensagem": str(e)}


def pesquisar_conteudo(diretorio: str, texto: str, extensao: str = ".py") -> dict:
    """Pesquisa texto dentro de arquivos."""
    try:
        resultados = []
        for root, dirs, files in os.walk(diretorio):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            for name in files:
                if not name.endswith(extensao):
                    continue
                caminho = os.path.join(root, name)
                try:
                    with open(caminho, "r", encoding="utf-8", errors="ignore") as f:
                        for i, linha in enumerate(f, 1):
                            if texto.lower() in linha.lower():
                                resultados.append({
                                    "arquivo": caminho,
                                    "linha": i,
                                    "conteudo": linha.strip()[:200]
                                })
                                if len(resultados) >= 30:
                                    break
                except Exception:
                    pass
                if len(resultados) >= 30:
                    break
            if len(resultados) >= 30:
                break
        return {"sucesso": True, "resultados": resultados, "total": len(resultados)}
    except Exception as e:
        return {"sucesso": False, "resultados": [], "mensagem": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  SKILL 18: Pesquisar na Internet
# ═══════════════════════════════════════════════════════════════════

def pesquisar_internet(query: str, num_resultados: int = 5) -> dict:
    """Pesquisa na internet usando Google. Retorna títulos, URLs e descrições."""
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        url = f"https://www.google.com/search?q={requests.utils.quote(query)}&num={num_resultados}&hl=pt-BR"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        resultados = []

        for g in soup.select("div.g"):
            titulo_elem = g.select_one("h3")
            link_elem = g.select_one("a[href]")
            desc_elem = g.select_one("div.VwiC3b")

            if titulo_elem and link_elem:
                href = link_elem.get("href", "")
                if href.startswith("/url?q="):
                    href = href.split("/url?q=")[1].split("&")[0]
                resultados.append({
                    "titulo": titulo_elem.get_text(),
                    "url": href,
                    "descricao": desc_elem.get_text()[:300] if desc_elem else ""
                })

        return {"sucesso": True, "resultados": resultados[:num_resultados], "query": query}
    except ImportError:
        return {"sucesso": False, "mensagem": "Instale: pip install requests beautifulsoup4"}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  SKILL 19: Baixar arquivo da internet
# ═══════════════════════════════════════════════════════════════════

def baixar_arquivo(url: str, destino: str = None) -> dict:
    """Baixa um arquivo de uma URL para o disco."""
    try:
        import requests

        if not destino:
            nome = url.split("/")[-1].split("?")[0] or "download"
            destino = os.path.join(os.path.expanduser("~"), "Downloads", nome)

        os.makedirs(os.path.dirname(destino), exist_ok=True)

        resp = requests.get(url, timeout=60, stream=True)
        resp.raise_for_status()

        with open(destino, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        tamanho_kb = round(os.path.getsize(destino) / 1024, 1)
        return {"sucesso": True, "mensagem": f"Baixado: {destino} ({tamanho_kb}KB)", "caminho": destino}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  SKILL 20: Ler conteúdo de página web
# ═══════════════════════════════════════════════════════════════════

def ler_pagina_web(url: str) -> dict:
    """Lê e extrai o conteúdo texto de uma página web."""
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remover scripts e estilos
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        texto = soup.get_text(separator="\n", strip=True)
        # Limpar linhas vazias
        linhas = [l.strip() for l in texto.split("\n") if l.strip()]
        texto_limpo = "\n".join(linhas)

        return {"sucesso": True, "conteudo": texto_limpo[:8000], "titulo": soup.title.string if soup.title else "", "url": url}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  SKILL 21: Escrever e executar código
# ═══════════════════════════════════════════════════════════════════

def escrever_e_executar_codigo(linguagem: str, codigo: str, salvar_em: str = None) -> dict:
    """
    Escreve código em qualquer linguagem e opcionalmente executa.
    Suporta: python, javascript, html, bat, powershell, etc.
    """
    try:
        extensoes = {
            "python": ".py", "py": ".py",
            "javascript": ".js", "js": ".js",
            "html": ".html",
            "css": ".css",
            "bat": ".bat", "batch": ".bat",
            "powershell": ".ps1", "ps1": ".ps1",
            "mql5": ".mq5",
            "c": ".c", "cpp": ".cpp",
            "java": ".java",
            "typescript": ".ts", "ts": ".ts",
            "json": ".json",
            "yaml": ".yaml", "yml": ".yml",
            "xml": ".xml",
            "sql": ".sql",
            "sh": ".sh", "bash": ".sh",
        }

        ext = extensoes.get(linguagem.lower(), f".{linguagem}")

        if salvar_em:
            caminho = salvar_em
        else:
            caminho = os.path.join(tempfile.gettempdir(), f"adk_temp{ext}")

        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(codigo)

        resultado = {"sucesso": True, "arquivo": caminho, "mensagem": f"Código {linguagem} salvo em: {caminho}"}

        # Executar automaticamente para linguagens suportadas
        executaveis = {
            ".py": f"python \"{caminho}\"",
            ".js": f"node \"{caminho}\"",
            ".bat": f"\"{caminho}\"",
            ".ps1": f"powershell -ExecutionPolicy Bypass -File \"{caminho}\"",
        }

        if ext in executaveis and not salvar_em:
            exec_result = executar_comando(executaveis[ext])
            resultado["execucao"] = exec_result
            resultado["mensagem"] += f" | Executado!"

        return resultado
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  SKILL 22: Screenshot da tela
# ═══════════════════════════════════════════════════════════════════

def capturar_screenshot(destino: str = None) -> dict:
    """Captura print da tela e salva como imagem."""
    try:
        import mss
        from PIL import Image

        if not destino:
            destino = os.path.join(
                os.path.expanduser("~"), "Downloads",
                f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )

        os.makedirs(os.path.dirname(destino), exist_ok=True)

        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[0])
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            img.save(destino)

        return {"sucesso": True, "mensagem": f"Screenshot salvo: {destino}", "caminho": destino}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  SKILL 23-24: Controle de energia do PC
# ═══════════════════════════════════════════════════════════════════

def desligar_pc(tempo_segundos: int = 30) -> dict:
    """Programa o desligamento do PC."""
    try:
        resultado = executar_comando(f"shutdown /s /t {tempo_segundos}")
        return {"sucesso": True, "mensagem": f"PC será desligado em {tempo_segundos} segundos. Para cancelar: shutdown /a"}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


def reiniciar_pc(tempo_segundos: int = 30) -> dict:
    """Reinicia o PC."""
    try:
        resultado = executar_comando(f"shutdown /r /t {tempo_segundos}")
        return {"sucesso": True, "mensagem": f"PC será reiniciado em {tempo_segundos} segundos. Para cancelar: shutdown /a"}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  SKILL 25: Controle de mouse e teclado
# ═══════════════════════════════════════════════════════════════════

def controlar_mouse_teclado(acao: str, x: int = None, y: int = None, texto: str = None, tecla: str = None) -> dict:
    """
    Controla mouse e teclado do computador.

    Ações disponíveis:
    - "clicar": clica na posição (x, y)
    - "duplo_clique": duplo clique na posição (x, y)
    - "clique_direito": clique direito na posição (x, y)
    - "mover": move mouse para (x, y)
    - "digitar": digita o texto fornecido
    - "teclar": pressiona uma tecla (enter, tab, esc, space, etc)
    - "hotkey": combinação de teclas (ex: "ctrl+c", "alt+tab")
    - "scroll": scroll para cima (y>0) ou baixo (y<0)
    - "posicao": retorna posição atual do mouse
    """
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.1

        if acao == "clicar" and x is not None and y is not None:
            pyautogui.click(x, y)
            return {"sucesso": True, "mensagem": f"Clique em ({x}, {y})"}

        elif acao == "duplo_clique" and x is not None and y is not None:
            pyautogui.doubleClick(x, y)
            return {"sucesso": True, "mensagem": f"Duplo clique em ({x}, {y})"}

        elif acao == "clique_direito" and x is not None and y is not None:
            pyautogui.rightClick(x, y)
            return {"sucesso": True, "mensagem": f"Clique direito em ({x}, {y})"}

        elif acao == "mover" and x is not None and y is not None:
            pyautogui.moveTo(x, y, duration=0.3)
            return {"sucesso": True, "mensagem": f"Mouse movido para ({x}, {y})"}

        elif acao == "digitar" and texto:
            pyautogui.typewrite(texto, interval=0.02) if texto.isascii() else pyautogui.write(texto)
            return {"sucesso": True, "mensagem": f"Digitado: {texto[:50]}"}

        elif acao == "teclar" and tecla:
            pyautogui.press(tecla)
            return {"sucesso": True, "mensagem": f"Tecla pressionada: {tecla}"}

        elif acao == "hotkey" and tecla:
            keys = tecla.split("+")
            pyautogui.hotkey(*keys)
            return {"sucesso": True, "mensagem": f"Hotkey: {tecla}"}

        elif acao == "scroll":
            amount = y or -3
            pyautogui.scroll(amount)
            return {"sucesso": True, "mensagem": f"Scroll: {amount}"}

        elif acao == "posicao":
            pos = pyautogui.position()
            return {"sucesso": True, "x": pos.x, "y": pos.y, "mensagem": f"Mouse em ({pos.x}, {pos.y})"}

        else:
            return {"sucesso": False, "mensagem": f"Ação '{acao}' não reconhecida ou parâmetros faltando"}
    except ImportError:
        return {"sucesso": False, "mensagem": "Instale: pip install pyautogui"}
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  SKILL 26-30: Memória persistente (usam memory.py)
# ═══════════════════════════════════════════════════════════════════

def skill_salvar_nota(titulo: str, conteudo: str) -> dict:
    """Salva uma nota na memória persistente do agente."""
    return salvar_nota(titulo, conteudo)


def skill_buscar_notas(termo: str) -> dict:
    """Busca nas notas salvas pela memória."""
    return buscar_notas(termo)


def skill_listar_notas() -> dict:
    """Lista todas as notas salvas."""
    return listar_notas()


def skill_salvar_tarefa(descricao: str) -> dict:
    """Salva uma tarefa pendente."""
    return salvar_tarefa(descricao)


def skill_concluir_tarefa(tarefa_id: int) -> dict:
    """Marca tarefa como concluída."""
    return concluir_tarefa(tarefa_id)


def skill_listar_tarefas() -> dict:
    """Lista tarefas pendentes."""
    return listar_tarefas(apenas_pendentes=True)


def skill_salvar_aprendizado(conteudo: str, fonte: str = "") -> dict:
    """Salva algo aprendido (de vídeo, pesquisa, etc)."""
    return salvar_aprendizado(conteudo, fonte)


def skill_buscar_aprendizados(termo: str) -> dict:
    """Busca nos aprendizados salvos."""
    return buscar_aprendizados(termo)


def skill_historico_conversa(quantidade: int = 20) -> dict:
    """Recupera histórico de conversas anteriores."""
    historico = obter_historico(quantidade)
    return {"sucesso": True, "mensagens": historico, "total": len(historico)}


# ═══════════════════════════════════════════════════════════════════
#  SKILL 31-35: Visão Computacional (usam vision_utils.py)
# ═══════════════════════════════════════════════════════════════════

def skill_detectar_texto_tela(regiao: list = None, idiomas: list = None) -> dict:
    """Detecta todo o texto visível na tela usando OCR."""
    from vision_utils import detectar_texto_tela
    regiao_tuple = tuple(regiao) if regiao else None
    return detectar_texto_tela(regiao_tuple, idiomas)


def skill_localizar_texto(texto: str, regiao: list = None, idiomas: list = None, case_sensitive: bool = False) -> dict:
    """Procura texto específico na tela e retorna coordenadas precisas."""
    from vision_utils import encontrar_texto
    regiao_tuple = tuple(regiao) if regiao else None
    return encontrar_texto(texto, regiao_tuple, idiomas, case_sensitive)


def skill_localizar_elemento(imagem_template: str, confianca: float = 0.8, regiao: list = None) -> dict:
    """Localiza elemento visual (ícone, botão) usando template matching."""
    from vision_utils import localizar_elemento_visual
    regiao_tuple = tuple(regiao) if regiao else None
    return localizar_elemento_visual(imagem_template, confianca, regiao_tuple)


def skill_clicar_em_texto(texto: str, tipo_clique: str = "clicar", idiomas: list = None) -> dict:
    """Localiza texto via OCR e clica nele automaticamente."""
    from vision_utils import encontrar_texto
    import pyautogui
    
    # Encontrar texto
    resultado = encontrar_texto(texto, None, idiomas, False)
    
    if not resultado.get("sucesso"):
        return resultado
    
    if not resultado.get("encontrado"):
        return {"sucesso": False, "mensagem": f"Texto '{texto}' não encontrado na tela"}
    
    # Obter coordenadas
    centro = resultado["centro"]
    x, y = centro[0], centro[1]
    
    # Executar clique
    try:
        pyautogui.FAILSAFE = False
        if tipo_clique == "clicar":
            pyautogui.click(x, y)
        elif tipo_clique == "duplo_clique":
            pyautogui.doubleClick(x, y)
        elif tipo_clique == "clique_direito":
            pyautogui.rightClick(x, y)
        else:
            return {"sucesso": False, "mensagem": f"Tipo de clique inválido: {tipo_clique}"}
        
        return {
            "sucesso": True,
            "mensagem": f"{tipo_clique} executado em '{texto}' na posição ({x}, {y})",
            "texto": resultado["texto"],
            "coordenadas": [x, y]
        }
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


def skill_salvar_screenshot_debug(caminho: str = None, mostrar_texto: bool = True) -> dict:
    """Salva screenshot com anotações de debug (textos detectados via OCR)."""
    from vision_utils import detectar_texto_tela, salvar_screenshot_anotado
    import os
    from datetime import datetime
    
    if not caminho:
        caminho = os.path.join(
            os.path.expanduser("~"), "Downloads",
            f"debug_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
    
    anotacoes = []
    
    if mostrar_texto:
        # Detectar textos
        resultado = detectar_texto_tela()
        if resultado.get("sucesso") and resultado.get("textos"):
            for item in resultado["textos"][:20]:  # Limitar a 20 para não poluir
                anotacoes.append({
                    "tipo": "box",
                    "bbox": item["bbox"],
                    "cor": (0, 255, 0)
                })
                anotacoes.append({
                    "tipo": "text",
                    "bbox": [item["bbox"][0], item["bbox"][1]],
                    "texto": item["texto"][:30],
                    "cor": (0, 255, 0)
                })
    
    return salvar_screenshot_anotado(caminho, anotacoes)


# ═══════════════════════════════════════════════════════════════════
#  REGISTRO DE TODAS AS SKILLS
# ═══════════════════════════════════════════════════════════════════

SKILLS_MAP = {
    # Arquivos e terminal
    "executar_comando": executar_comando,
    "criar_arquivo": criar_arquivo,
    "ler_arquivo": ler_arquivo,
    "editar_arquivo": editar_arquivo,
    "deletar_arquivo": deletar_arquivo,
    "listar_arquivos": listar_arquivos,
    "mover_arquivo": mover_arquivo,
    "copiar_arquivo": copiar_arquivo,
    "criar_pasta": criar_pasta,
    # Instalar
    "instalar_pacote_pip": instalar_pacote_pip,
    "instalar_programa": instalar_programa,
    # Sistema
    "info_sistema": info_sistema,
    "listar_processos": listar_processos,
    "finalizar_processo": finalizar_processo,
    # Apps e URLs
    "abrir_aplicativo": abrir_aplicativo,
    "abrir_url": abrir_url,
    # Pesquisa
    "pesquisar_arquivos": pesquisar_arquivos,
    "pesquisar_conteudo": pesquisar_conteudo,
    # ═══ NOVAS SKILLS ═══
    "pesquisar_internet": pesquisar_internet,
    "baixar_arquivo": baixar_arquivo,
    "ler_pagina_web": ler_pagina_web,
    "escrever_e_executar_codigo": escrever_e_executar_codigo,
    "capturar_screenshot": capturar_screenshot,
    "desligar_pc": desligar_pc,
    "reiniciar_pc": reiniciar_pc,
    "controlar_mouse_teclado": controlar_mouse_teclado,
    # Memória
    "salvar_nota": skill_salvar_nota,
    "buscar_notas": skill_buscar_notas,
    "listar_notas": skill_listar_notas,
    "salvar_tarefa": skill_salvar_tarefa,
    "concluir_tarefa": skill_concluir_tarefa,
    "listar_tarefas": skill_listar_tarefas,
    "salvar_aprendizado": skill_salvar_aprendizado,
    "buscar_aprendizados": skill_buscar_aprendizados,
    "historico_conversa": skill_historico_conversa,
    # Visão Computacional
    "detectar_texto_tela": skill_detectar_texto_tela,
    "localizar_texto": skill_localizar_texto,
    "localizar_elemento": skill_localizar_elemento,
    "clicar_em_texto": skill_clicar_em_texto,
    "salvar_screenshot_debug": skill_salvar_screenshot_debug,
}


def executar_skill(nome: str, params: dict) -> str:
    """Executa uma skill pelo nome e retorna JSON."""
    if nome in SKILLS_MAP:
        func = SKILLS_MAP[nome]
        resultado = func(**params)
        return json.dumps(resultado, ensure_ascii=False, default=str)
    return json.dumps({"sucesso": False, "mensagem": f"Skill '{nome}' não encontrada"})


# ═══════════════════════════════════════════════════════════════════
#  DECLARAÇÕES DAS TOOLS (function calling do Gemini)
# ═══════════════════════════════════════════════════════════════════

TOOL_DECLARATIONS = [
    {
        "name": "executar_comando",
        "description": "Executa comando no terminal Windows (PowerShell/CMD). Use para rodar scripts, compilar, instalar, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "comando": {"type": "string", "description": "O comando a executar"},
                "diretorio": {"type": "string", "description": "Diretório de trabalho (opcional)"}
            },
            "required": ["comando"]
        }
    },
    {
        "name": "criar_arquivo",
        "description": "Cria ou sobrescreve um arquivo com conteúdo. Códigos, scripts, configs, HTML, qualquer coisa.",
        "parameters": {
            "type": "object",
            "properties": {
                "caminho": {"type": "string", "description": "Caminho completo do arquivo"},
                "conteudo": {"type": "string", "description": "Conteúdo do arquivo"}
            },
            "required": ["caminho", "conteudo"]
        }
    },
    {
        "name": "ler_arquivo",
        "description": "Lê conteúdo de um arquivo.",
        "parameters": {"type": "object", "properties": {"caminho": {"type": "string", "description": "Caminho do arquivo"}}, "required": ["caminho"]}
    },
    {
        "name": "editar_arquivo",
        "description": "Edita arquivo substituindo texto.",
        "parameters": {
            "type": "object",
            "properties": {
                "caminho": {"type": "string", "description": "Caminho do arquivo"},
                "texto_antigo": {"type": "string", "description": "Texto a substituir"},
                "texto_novo": {"type": "string", "description": "Novo texto"}
            },
            "required": ["caminho", "texto_antigo", "texto_novo"]
        }
    },
    {
        "name": "deletar_arquivo",
        "description": "Deleta arquivo ou pasta.",
        "parameters": {"type": "object", "properties": {"caminho": {"type": "string", "description": "Caminho"}}, "required": ["caminho"]}
    },
    {
        "name": "listar_arquivos",
        "description": "Lista arquivos e pastas em um diretório.",
        "parameters": {
            "type": "object",
            "properties": {
                "diretorio": {"type": "string", "description": "Caminho do diretório"},
                "padrao": {"type": "string", "description": "Padrão glob (*.py, *.txt)"}
            },
            "required": ["diretorio"]
        }
    },
    {
        "name": "mover_arquivo",
        "description": "Move ou renomeia arquivo/pasta.",
        "parameters": {
            "type": "object",
            "properties": {
                "origem": {"type": "string", "description": "Caminho origem"},
                "destino": {"type": "string", "description": "Caminho destino"}
            },
            "required": ["origem", "destino"]
        }
    },
    {
        "name": "copiar_arquivo",
        "description": "Copia arquivo ou pasta.",
        "parameters": {
            "type": "object",
            "properties": {
                "origem": {"type": "string", "description": "Caminho origem"},
                "destino": {"type": "string", "description": "Caminho destino"}
            },
            "required": ["origem", "destino"]
        }
    },
    {
        "name": "criar_pasta",
        "description": "Cria pasta e subpastas.",
        "parameters": {"type": "object", "properties": {"caminho": {"type": "string", "description": "Caminho da pasta"}}, "required": ["caminho"]}
    },
    {
        "name": "instalar_pacote_pip",
        "description": "Instala pacote Python via pip.",
        "parameters": {"type": "object", "properties": {"pacote": {"type": "string", "description": "Nome do pacote"}}, "required": ["pacote"]}
    },
    {
        "name": "instalar_programa",
        "description": "Instala programa via comando (winget, choco, etc).",
        "parameters": {"type": "object", "properties": {"comando_instalacao": {"type": "string", "description": "Comando de instalação"}}, "required": ["comando_instalacao"]}
    },
    {
        "name": "info_sistema",
        "description": "Informações do sistema: CPU, RAM, disco, processos.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "listar_processos",
        "description": "Lista processos em execução.",
        "parameters": {"type": "object", "properties": {"filtro": {"type": "string", "description": "Filtro por nome"}}}
    },
    {
        "name": "finalizar_processo",
        "description": "Finaliza processo por PID ou nome.",
        "parameters": {
            "type": "object",
            "properties": {
                "pid": {"type": "integer", "description": "PID do processo"},
                "nome": {"type": "string", "description": "Nome do processo"}
            }
        }
    },
    {
        "name": "abrir_aplicativo",
        "description": "Abre aplicativo, arquivo ou pasta no Windows.",
        "parameters": {"type": "object", "properties": {"caminho_ou_nome": {"type": "string", "description": "Caminho do executável"}}, "required": ["caminho_ou_nome"]}
    },
    {
        "name": "abrir_url",
        "description": "Abre URL no navegador padrão.",
        "parameters": {"type": "object", "properties": {"url": {"type": "string", "description": "URL completa"}}, "required": ["url"]}
    },
    {
        "name": "pesquisar_arquivos",
        "description": "Pesquisa arquivos por nome em diretório.",
        "parameters": {
            "type": "object",
            "properties": {
                "diretorio": {"type": "string", "description": "Diretório raiz"},
                "termo": {"type": "string", "description": "Termo de busca"},
                "extensoes": {"type": "string", "description": "Extensões (.py,.txt)"}
            },
            "required": ["diretorio", "termo"]
        }
    },
    {
        "name": "pesquisar_conteudo",
        "description": "Pesquisa texto dentro de arquivos.",
        "parameters": {
            "type": "object",
            "properties": {
                "diretorio": {"type": "string", "description": "Diretório raiz"},
                "texto": {"type": "string", "description": "Texto a buscar"},
                "extensao": {"type": "string", "description": "Extensão (.py)"}
            },
            "required": ["diretorio", "texto"]
        }
    },
    # ═══ NOVAS SKILLS ═══
    {
        "name": "pesquisar_internet",
        "description": "Pesquisa no Google. Use quando tiver dúvida, precisar de informação atualizada, buscar tutoriais, documentação, soluções para erros, bibliotecas, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "O que pesquisar"},
                "num_resultados": {"type": "integer", "description": "Número de resultados (padrão: 5)"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "baixar_arquivo",
        "description": "Baixa arquivo de qualquer URL para o disco local.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL do arquivo"},
                "destino": {"type": "string", "description": "Caminho local para salvar (opcional)"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "ler_pagina_web",
        "description": "Lê e extrai o conteúdo texto de uma página web. Use para ler documentação, artigos, tutoriais, fóruns, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL da página"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "escrever_e_executar_codigo",
        "description": "Escreve código em QUALQUER linguagem (Python, JavaScript, HTML, MQL5, C, Java, TypeScript, SQL, etc) e opcionalmente executa. Pode salvar em arquivo permanente ou temporário.",
        "parameters": {
            "type": "object",
            "properties": {
                "linguagem": {"type": "string", "description": "Linguagem: python, javascript, html, mql5, java, etc"},
                "codigo": {"type": "string", "description": "O código fonte completo"},
                "salvar_em": {"type": "string", "description": "Caminho para salvar (opcional, se omitido usa arquivo temp e auto-executa)"}
            },
            "required": ["linguagem", "codigo"]
        }
    },
    {
        "name": "capturar_screenshot",
        "description": "Captura print da tela inteira e salva como imagem PNG.",
        "parameters": {
            "type": "object",
            "properties": {
                "destino": {"type": "string", "description": "Caminho para salvar (opcional)"}
            }
        }
    },
    {
        "name": "desligar_pc",
        "description": "Programa o desligamento do PC (padrão 30s). Pode cancelar com shutdown /a.",
        "parameters": {
            "type": "object",
            "properties": {
                "tempo_segundos": {"type": "integer", "description": "Segundos até desligar (padrão: 30)"}
            }
        }
    },
    {
        "name": "reiniciar_pc",
        "description": "Reinicia o PC (padrão 30s). Pode cancelar com shutdown /a.",
        "parameters": {
            "type": "object",
            "properties": {
                "tempo_segundos": {"type": "integer", "description": "Segundos até reiniciar (padrão: 30)"}
            }
        }
    },
    {
        "name": "controlar_mouse_teclado",
        "description": "Controla mouse e teclado do PC. Ações: clicar, duplo_clique, clique_direito, mover, digitar, teclar, hotkey, scroll, posicao. Use para interagir com qualquer app ou site: clicar em vídeos, botões, digitar texto, pressionar teclas, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "acao": {"type": "string", "description": "Ação: clicar, duplo_clique, clique_direito, mover, digitar, teclar, hotkey, scroll, posicao"},
                "x": {"type": "integer", "description": "Coordenada X do mouse"},
                "y": {"type": "integer", "description": "Coordenada Y do mouse"},
                "texto": {"type": "string", "description": "Texto para digitar"},
                "tecla": {"type": "string", "description": "Tecla ou combinação (enter, tab, ctrl+c, alt+tab)"}
            },
            "required": ["acao"]
        }
    },
    # Memória
    {
        "name": "salvar_nota",
        "description": "Salva uma informação importante na memória permanente. Use SEMPRE que aprender algo novo, receber uma instrução importante, ou quando o usuário pedir para lembrar algo. NUNCA esqueça de salvar aprendizados!",
        "parameters": {
            "type": "object",
            "properties": {
                "titulo": {"type": "string", "description": "Título da nota"},
                "conteudo": {"type": "string", "description": "Conteúdo detalhado"}
            },
            "required": ["titulo", "conteudo"]
        }
    },
    {
        "name": "buscar_notas",
        "description": "Busca nas notas salvas na memória. Use quando precisar lembrar algo.",
        "parameters": {
            "type": "object",
            "properties": {"termo": {"type": "string", "description": "Termo de busca"}},
            "required": ["termo"]
        }
    },
    {
        "name": "listar_notas",
        "description": "Lista todas as notas salvas na memória.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "salvar_tarefa",
        "description": "Salva uma tarefa pendente que precisa ser feita.",
        "parameters": {
            "type": "object",
            "properties": {"descricao": {"type": "string", "description": "Descrição da tarefa"}},
            "required": ["descricao"]
        }
    },
    {
        "name": "concluir_tarefa",
        "description": "Marca tarefa como concluída.",
        "parameters": {
            "type": "object",
            "properties": {"tarefa_id": {"type": "integer", "description": "ID da tarefa"}},
            "required": ["tarefa_id"]
        }
    },
    {
        "name": "listar_tarefas",
        "description": "Lista tarefas pendentes.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "salvar_aprendizado",
        "description": "Salva algo que você aprendeu (de vídeo, pesquisa, análise). SEMPRE salve quando assistir vídeos, ler documentação, ou descobrir algo novo.",
        "parameters": {
            "type": "object",
            "properties": {
                "conteudo": {"type": "string", "description": "O que aprendeu (detalhado)"},
                "fonte": {"type": "string", "description": "De onde aprendeu (URL, vídeo, etc)"}
            },
            "required": ["conteudo"]
        }
    },
    {
        "name": "buscar_aprendizados",
        "description": "Busca nos aprendizados salvos.",
        "parameters": {
            "type": "object",
            "properties": {"termo": {"type": "string", "description": "Termo de busca"}},
            "required": ["termo"]
        }
    },
    {
        "name": "historico_conversa",
        "description": "Recupera mensagens de conversas anteriores. Use quando o usuário pedir para continuar ou revisar algo que falaram antes.",
        "parameters": {
            "type": "object",
            "properties": {"quantidade": {"type": "integer", "description": "Número de mensagens (padrão: 20)"}}
        }
    },
    # ═══ VISÃO COMPUTACIONAL ═══
    {
        "name": "detectar_texto_tela",
        "description": "Detecta TODOS os textos visíveis na tela usando OCR. Retorna lista com texto, coordenadas e confiança. Use para ver o que está escrito na tela atual.",
        "parameters": {
            "type": "object",
            "properties": {
                "regiao": {"type": "array", "description": "[x, y, largura, altura] para região específica (opcional)", "items": {"type": "integer"}},
                "idiomas": {"type": "array", "description": "Idiomas: ['pt', 'en', 'es'] (padrão: ['pt', 'en'])", "items": {"type": "string"}}
            }
        }
    },
    {
        "name": "localizar_texto",
        "description": "LOCALIZA um texto específico na tela e retorna suas COORDENADAS EXATAS. SEMPRE use esta skill ANTES de clicar em algo! Use para encontrar botões, campos, labels.",
        "parameters": {
            "type": "object",
            "properties": {
                "texto": {"type": "string", "description": "Texto a procurar (ex: 'Enviar', 'Login', 'Campo de mensagem')"},
                "regiao": {"type": "array", "description": "[x, y, largura, altura] (opcional)", "items": {"type": "integer"}},
                "idiomas": {"type": "array", "description": "Idiomas para OCR (opcional)", "items": {"type": "string"}},
                "case_sensitive": {"type": "boolean", "description": "Diferenciar maiúsculas (padrão: false)"}
            },
            "required": ["texto"]
        }
    },
    {
        "name": "localizar_elemento",
        "description": "Localiza elemento VISUAL (ícone, botão, imagem) usando template matching. Requer imagem do elemento como referência.",
        "parameters": {
            "type": "object",
            "properties": {
                "imagem_template": {"type": "string", "description": "Caminho da imagem template (PNG/JPG)"},
                "confianca": {"type": "number", "description": "Confiança mínima 0.0-1.0 (padrão: 0.8)"},
                "regiao": {"type": "array", "description": "[x, y, largura, altura] (opcional)", "items": {"type": "integer"}}
            },
            "required": ["imagem_template"]
        }
    },
    {
        "name": "clicar_em_texto",
        "description": "COMBO PODEROSO: Localiza texto via OCR e CLICA AUTOMATICAMENTE! Use para clicar em botões, links, campos. Exemplo: clicar_em_texto('Enviar') ou clicar_em_texto('Campo de mensagem')",
        "parameters": {
            "type": "object",
            "properties": {
                "texto": {"type": "string", "description": "Texto do elemento a clicar"},
                "tipo_clique": {"type": "string", "description": "Tipo: 'clicar', 'duplo_clique', 'clique_direito' (padrão: 'clicar')"},
                "idiomas": {"type": "array", "description": "Idiomas para OCR (opcional)", "items": {"type": "string"}}
            },
            "required": ["texto"]
        }
    },
    {
        "name": "salvar_screenshot_debug",
        "description": "Salva screenshot da tela com anotações visuais mostrando textos detectados via OCR. Útil para debug e verificação.",
        "parameters": {
            "type": "object",
            "properties": {
                "caminho": {"type": "string", "description": "Onde salvar (opcional, padrão: Downloads)"},
                "mostrar_texto": {"type": "boolean", "description": "Mostrar textos detectados (padrão: true)"}
            }
        }
    },
]
