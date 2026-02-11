"""
Test Script — Teste Básico do Sistema de Visão Computacional
Testa OCR e detecção de elementos na tela.
"""

import sys
import os

# Adicionar caminho do projeto
sys.path.insert(0, os.path.dirname(__file__))

from vision_utils import detectar_texto_tela, encontrar_texto, salvar_screenshot_anotado


def test_ocr_basico():
    """Teste 1: OCR básico - detectar textos na tela"""
    print("=" * 60)
    print("TESTE 1: Detecção de Texto (OCR)")
    print("=" * 60)
    
    print("\n📸 Capturando tela e detectando textos...")
    resultado = detectar_texto_tela()
    
    if resultado["sucesso"]:
        print(f"✅ Sucesso! {resultado['total']} textos detectados\n")
        
        # Mostrar primeiros 10 textos
        for i, item in enumerate(resultado["textos"][:10], 1):
            print(f"{i}. Texto: '{item['texto']}")
            print(f"   Confiança: {item['confianca']}")
            print(f"   Coordenadas: {item['centro']}\n")
    else:
        print(f"❌ Erro: {resultado.get('mensagem', 'Desconhecido')}")
    
    return resultado


def test_localizar_texto(texto_procurar):
    """Teste 2: Localizar texto específico"""
    print("=" * 60)
    print(f"TESTE 2: Localizar Texto Específico: '{texto_procurar}'")
    print("=" * 60)
    
    print(f"\n🔍 Procurando por '{texto_procurar}'...")
    resultado = encontrar_texto(texto_procurar)
    
    if resultado["sucesso"] and resultado.get("encontrado"):
        print(f"✅ Texto encontrado!")
        print(f"   Texto detectado: '{resultado['texto']}'")
        print(f"   Confiança: {resultado['confianca']}")
        print(f"   Centro: {resultado['centro']}")
        print(f"   Bbox: {resultado['bbox']}")
    elif resultado["sucesso"]:
        print(f"⚠️ Texto não encontrado na tela")
    else:
        print(f"❌ Erro: {resultado.get('mensagem', 'Desconhecido')}")
    
    return resultado


def test_screenshot_debug():
    """Teste 3: Salvar screenshot com anotações"""
    print("=" * 60)
    print("TESTE 3: Screenshot com Anotações de Debug")
    print("=" * 60)
    
    print("\n📸 Criando screenshot com anotações...")
    
    # Detectar textos
    resultado_ocr = detectar_texto_tela()
    
    if not resultado_ocr["sucesso"]:
        print(f"❌ Erro no OCR: {resultado_ocr.get('mensagem')}")
        return
    
    # Criar anotações
    anotacoes = []
    for item in resultado_ocr["textos"][:15]:  # Primeiros 15
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
    
    # Salvar
    caminho = os.path.join(os.path.expanduser("~"), "Downloads", "test_vision_debug.png")
    resultado = salvar_screenshot_anotado(caminho, anotacoes)
    
    if resultado["sucesso"]:
        print(f"✅ Screenshot salvo: {resultado['caminho']}")
    else:
        print(f"❌ Erro: {resultado.get('mensagem')}")
    
    return resultado


if __name__ == "__main__":
    print("\n🎯 ADK AGENT — Teste de Visão Computacional\n")
    
    # Teste 1: OCR básico
    test_ocr_basico()
    
    print("\n" + "=" * 60 + "\n")
    input("Pressione ENTER para continuar com o próximo teste...")
    
    # Teste 2: Localizar texto (você pode mudar o texto aqui)
    # Sugestão: abra o Notepad e escreva "Hello World"
    texto = input("\n🔍 Digite um texto para procurar na tela (ex: 'Hello'): ").strip()
    if texto:
        test_localizar_texto(texto)
    
    print("\n" + "=" * 60 + "\n")
    input("Pressione ENTER para criar screenshot de debug...")
    
    # Teste 3: Screenshot debug
    test_screenshot_debug()
    
    print("\n✅ Todos os testes concluídos!")
    print("📁 Verifique o screenshot em: Downloads/test_vision_debug.png\n")
