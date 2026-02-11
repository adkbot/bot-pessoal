"""
Sistema de Memória Persistente do ADK Agent.
Salva conversas, notas e tarefas em JSON para que o agente
NUNCA esqueça nada, mesmo após desligar o PC.
"""

import os
import json
import time
from datetime import datetime

# Diretório de memória
MEMORIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memoria")
os.makedirs(MEMORIA_DIR, exist_ok=True)

CONVERSAS_FILE = os.path.join(MEMORIA_DIR, "conversas.json")
NOTAS_FILE = os.path.join(MEMORIA_DIR, "notas.json")
TAREFAS_FILE = os.path.join(MEMORIA_DIR, "tarefas.json")
APRENDIZADOS_FILE = os.path.join(MEMORIA_DIR, "aprendizados.json")


def _carregar_json(filepath: str, default=None):
    """Carrega um arquivo JSON."""
    if default is None:
        default = []
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[Memória] Erro ao carregar {filepath}: {e}")
    return default


def _salvar_json(filepath: str, data):
    """Salva dados em JSON."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Memória] Erro ao salvar {filepath}: {e}")


# ═══════════════════════════════════════════════════════════════════
#  CONVERSAS — Histórico persistente
# ═══════════════════════════════════════════════════════════════════

def salvar_mensagem(role: str, conteudo: str):
    """Salva uma mensagem no histórico de conversas."""
    conversas = _carregar_json(CONVERSAS_FILE, [])
    conversas.append({
        "role": role,
        "conteudo": conteudo[:2000],
        "timestamp": datetime.now().isoformat()
    })
    # Manter últimas 200 mensagens
    if len(conversas) > 200:
        conversas = conversas[-200:]
    _salvar_json(CONVERSAS_FILE, conversas)


def obter_historico(n: int = 50) -> list:
    """Retorna as últimas N mensagens."""
    conversas = _carregar_json(CONVERSAS_FILE, [])
    return conversas[-n:]


def obter_resumo_contexto() -> str:
    """Gera um resumo do contexto anterior para o system instruction."""
    notas = _carregar_json(NOTAS_FILE, [])
    tarefas = _carregar_json(TAREFAS_FILE, [])
    aprendizados = _carregar_json(APRENDIZADOS_FILE, [])
    historico = obter_historico(20)

    partes = []

    if notas:
        partes.append("📝 NOTAS SALVAS:")
        for nota in notas[-15:]:
            partes.append(f"  - [{nota.get('titulo', 'sem título')}]: {nota.get('conteudo', '')[:200]}")

    tarefas_pendentes = [t for t in tarefas if not t.get("concluida")]
    if tarefas_pendentes:
        partes.append("\n📋 TAREFAS PENDENTES:")
        for t in tarefas_pendentes[-10:]:
            partes.append(f"  - #{t.get('id', '?')}: {t.get('descricao', '')[:200]}")

    if aprendizados:
        partes.append("\n🧠 APRENDIZADOS:")
        for a in aprendizados[-10:]:
            partes.append(f"  - {a.get('conteudo', '')[:200]}")

    if historico:
        partes.append("\n💬 ÚLTIMAS MENSAGENS:")
        for msg in historico[-10:]:
            role = "👤" if msg.get("role") == "user" else "🤖"
            partes.append(f"  {role} {msg.get('conteudo', '')[:150]}")

    return "\n".join(partes) if partes else "Sem memória anterior."


# ═══════════════════════════════════════════════════════════════════
#  NOTAS — Informações importantes que o agente salva
# ═══════════════════════════════════════════════════════════════════

def salvar_nota(titulo: str, conteudo: str) -> dict:
    """Salva uma nota na memória persistente."""
    notas = _carregar_json(NOTAS_FILE, [])
    nota = {
        "id": len(notas) + 1,
        "titulo": titulo,
        "conteudo": conteudo,
        "criada_em": datetime.now().isoformat()
    }
    notas.append(nota)
    _salvar_json(NOTAS_FILE, notas)
    return {"sucesso": True, "mensagem": f"Nota #{nota['id']} salva: {titulo}"}


def buscar_notas(termo: str) -> dict:
    """Busca notas que contêm o termo."""
    notas = _carregar_json(NOTAS_FILE, [])
    encontradas = [
        n for n in notas
        if termo.lower() in n.get("titulo", "").lower()
        or termo.lower() in n.get("conteudo", "").lower()
    ]
    return {"sucesso": True, "notas": encontradas, "total": len(encontradas)}


def listar_notas() -> dict:
    """Lista todas as notas salvas."""
    notas = _carregar_json(NOTAS_FILE, [])
    return {"sucesso": True, "notas": notas, "total": len(notas)}


def deletar_nota(nota_id: int) -> dict:
    """Deleta uma nota pelo ID."""
    notas = _carregar_json(NOTAS_FILE, [])
    notas = [n for n in notas if n.get("id") != nota_id]
    _salvar_json(NOTAS_FILE, notas)
    return {"sucesso": True, "mensagem": f"Nota #{nota_id} deletada"}


# ═══════════════════════════════════════════════════════════════════
#  TAREFAS — To-do list persistente
# ═══════════════════════════════════════════════════════════════════

def salvar_tarefa(descricao: str) -> dict:
    """Salva uma nova tarefa."""
    tarefas = _carregar_json(TAREFAS_FILE, [])
    tarefa = {
        "id": len(tarefas) + 1,
        "descricao": descricao,
        "concluida": False,
        "criada_em": datetime.now().isoformat()
    }
    tarefas.append(tarefa)
    _salvar_json(TAREFAS_FILE, tarefas)
    return {"sucesso": True, "mensagem": f"Tarefa #{tarefa['id']} criada: {descricao}"}


def concluir_tarefa(tarefa_id: int) -> dict:
    """Marca uma tarefa como concluída."""
    tarefas = _carregar_json(TAREFAS_FILE, [])
    for t in tarefas:
        if t.get("id") == tarefa_id:
            t["concluida"] = True
            t["concluida_em"] = datetime.now().isoformat()
            _salvar_json(TAREFAS_FILE, tarefas)
            return {"sucesso": True, "mensagem": f"Tarefa #{tarefa_id} concluída!"}
    return {"sucesso": False, "mensagem": f"Tarefa #{tarefa_id} não encontrada"}


def listar_tarefas(apenas_pendentes: bool = True) -> dict:
    """Lista tarefas."""
    tarefas = _carregar_json(TAREFAS_FILE, [])
    if apenas_pendentes:
        tarefas = [t for t in tarefas if not t.get("concluida")]
    return {"sucesso": True, "tarefas": tarefas, "total": len(tarefas)}


# ═══════════════════════════════════════════════════════════════════
#  APRENDIZADOS — O agente salva o que aprendeu
# ═══════════════════════════════════════════════════════════════════

def salvar_aprendizado(conteudo: str, fonte: str = "") -> dict:
    """Salva algo que o agente aprendeu (de vídeos, pesquisas, etc)."""
    aprendizados = _carregar_json(APRENDIZADOS_FILE, [])
    aprendizado = {
        "id": len(aprendizados) + 1,
        "conteudo": conteudo,
        "fonte": fonte,
        "aprendido_em": datetime.now().isoformat()
    }
    aprendizados.append(aprendizado)
    _salvar_json(APRENDIZADOS_FILE, aprendizados)
    return {"sucesso": True, "mensagem": f"Aprendizado #{aprendizado['id']} salvo"}


def buscar_aprendizados(termo: str) -> dict:
    """Busca nos aprendizados."""
    aprendizados = _carregar_json(APRENDIZADOS_FILE, [])
    encontrados = [
        a for a in aprendizados
        if termo.lower() in a.get("conteudo", "").lower()
        or termo.lower() in a.get("fonte", "").lower()
    ]
    return {"sucesso": True, "aprendizados": encontrados, "total": len(encontrados)}
