"""
Vision Utils — Visão Computacional para ADK Agent.
OCR, detecção de elementos, template matching e localização precisa.
"""

import os
import cv2
import numpy as np
import mss
from PIL import Image
from typing import Dict, List, Tuple, Optional, Any
import io
import base64


# ═══════════════════════════════════════════════════════════════════
#  OCR Engine — Detecção de Texto na Tela
# ═══════════════════════════════════════════════════════════════════

_easyocr_reader = None


def _get_easyocr_reader(languages=['pt', 'en']):
    """Singleton do EasyOCR Reader (carrega apenas uma vez)."""
    global _easyocr_reader
    if _easyocr_reader is None:
        try:
            import easyocr
            _easyocr_reader = easyocr.Reader(languages, gpu=False, verbose=False)
        except Exception as e:
            print(f"[VisionUtils] Erro ao inicializar EasyOCR: {e}")
            _easyocr_reader = None
    return _easyocr_reader


def capturar_tela_cv() -> np.ndarray:
    """Captura a tela inteira e retorna como array numpy (BGR)."""
    with mss.mss() as sct:
        monitor = sct.monitors[0]  # Tela inteira
        screenshot = sct.grab(monitor)
        # Converter para numpy array (BGR para OpenCV)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img


def detectar_texto_tela(regiao: Tuple[int, int, int, int] = None, idiomas: List[str] = None) -> Dict[str, Any]:
    """
    Detecta todo o texto visível na tela usando OCR.
    
    Args:
        regiao: (x, y, largura, altura) para região específica. Se None, usa tela inteira.
        idiomas: Lista de idiomas ['pt', 'en', 'es']. Padrão: ['pt', 'en']
    
    Returns:
        {
            "sucesso": bool,
            "textos": [{"texto": str, "confianca": float, "bbox": [x1,y1,x2,y2], "centro": [x,y]}],
            "total": int
        }
    """
    try:
        # Capturar tela
        img = capturar_tela_cv()
        
        # Aplicar região se especificada
        if regiao:
            x, y, w, h = regiao
            img = img[y:y+h, x:x+w]
        
        # Usar EasyOCR
        idiomas = idiomas or ['pt', 'en']
        reader = _get_easyocr_reader(idiomas)
        
        if reader is None:
            return {"sucesso": False, "mensagem": "EasyOCR não disponível. Instale: pip install easyocr"}
        
        # Detectar texto
        results = reader.readtext(img)
        
        # Processar resultados
        textos_detectados = []
        for (bbox, texto, confianca) in results:
            # bbox é lista de 4 pontos: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            x1 = int(min([p[0] for p in bbox]))
            y1 = int(min([p[1] for p in bbox]))
            x2 = int(max([p[0] for p in bbox]))
            y2 = int(max([p[1] for p in bbox]))
            
            # Ajustar coordenadas se for região
            if regiao:
                x1 += regiao[0]
                y1 += regiao[1]
                x2 += regiao[0]
                y2 += regiao[1]
            
            centro_x = (x1 + x2) // 2
            centro_y = (y1 + y2) // 2
            
            textos_detectados.append({
                "texto": texto,
                "confianca": round(confianca, 2),
                "bbox": [x1, y1, x2, y2],
                "centro": [centro_x, centro_y]
            })
        
        return {
            "sucesso": True,
            "textos": textos_detectados,
            "total": len(textos_detectados)
        }
    
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


def encontrar_texto(texto_procurado: str, regiao: Tuple[int, int, int, int] = None, 
                    idiomas: List[str] = None, case_sensitive: bool = False) -> Dict[str, Any]:
    """
    Procura por texto específico na tela e retorna suas coordenadas.
    
    Args:
        texto_procurado: Texto a procurar
        regiao: (x, y, largura, altura) para região específica
        idiomas: Lista de idiomas para OCR
        case_sensitive: Se deve diferenciar maiúsculas/minúsculas
    
    Returns:
        {
            "sucesso": bool,
            "encontrado": bool,
            "texto": str,
            "confianca": float,
            "bbox": [x1, y1, x2, y2],
            "centro": [x, y]
        }
    """
    try:
        resultado = detectar_texto_tela(regiao, idiomas)
        
        if not resultado["sucesso"]:
            return resultado
        
        # Buscar texto
        if not case_sensitive:
            texto_procurado = texto_procurado.lower()
        
        for item in resultado["textos"]:
            texto_detectado = item["texto"]
            if not case_sensitive:
                texto_detectado = texto_detectado.lower()
            
            if texto_procurado in texto_detectado:
                return {
                    "sucesso": True,
                    "encontrado": True,
                    "texto": item["texto"],
                    "confianca": item["confianca"],
                    "bbox": item["bbox"],
                    "centro": item["centro"]
                }
        
        return {
            "sucesso": True,
            "encontrado": False,
            "mensagem": f"Texto '{texto_procurado}' não encontrado na tela"
        }
    
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  Template Matching — Detecção de Elementos Visuais
# ═══════════════════════════════════════════════════════════════════

def localizar_elemento_visual(imagem_template: str, confianca_minima: float = 0.8, 
                               regiao: Tuple[int, int, int, int] = None) -> Dict[str, Any]:
    """
    Localiza elemento visual (ícone, botão) usando template matching.
    
    Args:
        imagem_template: Caminho para imagem do template (PNG/JPG)
        confianca_minima: Confiança mínima (0.0 a 1.0)
        regiao: (x, y, largura, altura) para busca em região específica
    
    Returns:
        {
            "sucesso": bool,
            "encontrado": bool,
            "confianca": float,
            "bbox": [x1, y1, x2, y2],
            "centro": [x, y]
        }
    """
    try:
        # Carregar template
        if not os.path.exists(imagem_template):
            return {"sucesso": False, "mensagem": f"Template não encontrado: {imagem_template}"}
        
        template = cv2.imread(imagem_template)
        if template is None:
            return {"sucesso": False, "mensagem": "Erro ao carregar template"}
        
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        h, w = template_gray.shape
        
        # Capturar tela
        img = capturar_tela_cv()
        
        # Aplicar região se especificada
        offset_x, offset_y = 0, 0
        if regiao:
            x, y, rw, rh = regiao
            img = img[y:y+rh, x:x+rw]
            offset_x, offset_y = x, y
        
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Template matching
        result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confianca_minima:
            x1 = max_loc[0] + offset_x
            y1 = max_loc[1] + offset_y
            x2 = x1 + w
            y2 = y1 + h
            centro_x = (x1 + x2) // 2
            centro_y = (y1 + y2) // 2
            
            return {
                "sucesso": True,
                "encontrado": True,
                "confianca": round(max_val, 2),
                "bbox": [x1, y1, x2, y2],
                "centro": [centro_x, centro_y]
            }
        else:
            return {
                "sucesso": True,
                "encontrado": False,
                "confianca": round(max_val, 2),
                "mensagem": f"Elemento não encontrado (confiança: {max_val:.2f} < {confianca_minima})"
            }
    
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  Debugging — Screenshots Anotados
# ═══════════════════════════════════════════════════════════════════

def salvar_screenshot_anotado(caminho: str, anotacoes: List[Dict] = None) -> Dict[str, Any]:
    """
    Salva screenshot da tela com anotações visuais (caixas, textos).
    
    Args:
        caminho: Caminho para salvar a imagem
        anotacoes: Lista de {"tipo": "box"/"text", "bbox": [x1,y1,x2,y2], "texto": str, "cor": (B,G,R)}
    
    Returns:
        {"sucesso": bool, "caminho": str}
    """
    try:
        img = capturar_tela_cv()
        
        if anotacoes:
            for anotacao in anotacoes:
                tipo = anotacao.get("tipo", "box")
                bbox = anotacao.get("bbox", [])
                cor = anotacao.get("cor", (0, 255, 0))  # Verde padrão
                
                if tipo == "box" and len(bbox) == 4:
                    x1, y1, x2, y2 = bbox
                    cv2.rectangle(img, (x1, y1), (x2, y2), cor, 2)
                
                if tipo == "text" or anotacao.get("texto"):
                    texto = anotacao.get("texto", "")
                    x, y = bbox[0] if len(bbox) >= 2 else (10, 30)
                    cv2.putText(img, texto, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.6, cor, 2)
        
        # Salvar
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        cv2.imwrite(caminho, img)
        
        return {"sucesso": True, "caminho": caminho, "mensagem": f"Screenshot salvo: {caminho}"}
    
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  PyAutoGUI Integration — Localização Visual
# ═══════════════════════════════════════════════════════════════════

def localizar_na_tela_pyautogui(imagem_template: str, confianca: float = 0.8) -> Dict[str, Any]:
    """
    Wrapper do pyautogui.locateOnScreen para consistência.
    Mais rápido que OpenCV mas menos flexível.
    
    Args:
        imagem_template: Caminho para imagem
        confianca: Confiança mínima (0.0 a 1.0)
    
    Returns:
        {"sucesso": bool, "encontrado": bool, "centro": [x, y]}
    """
    try:
        import pyautogui
        
        location = pyautogui.locateOnScreen(imagem_template, confidence=confianca)
        
        if location:
            centro = pyautogui.center(location)
            return {
                "sucesso": True,
                "encontrado": True,
                "centro": [centro.x, centro.y],
                "bbox": [location.left, location.top, location.left + location.width, location.top + location.height]
            }
        else:
            return {
                "sucesso": True,
                "encontrado": False,
                "mensagem": "Elemento não encontrado na tela"
            }
    
    except Exception as e:
        return {"sucesso": False, "mensagem": str(e)}
