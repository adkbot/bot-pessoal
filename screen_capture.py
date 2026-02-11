"""
Screen Capture — Captura a tela usando MSS.
Converte para JPEG base64 para enviar ao Gemini.
NOTA: MSS é thread-local no Windows, então criamos instância por captura.
"""

import asyncio
import base64
import io
from PIL import Image


class ScreenCapture:
    """Captura de tela com redimensionamento para 768x768 JPEG."""

    def __init__(self, fps: float = 1.0, resolution: int = 768):
        self.fps = fps
        self.resolution = resolution
        self.running = False

    def capture_frame(self) -> str:
        """Captura um frame da tela e retorna como base64 JPEG.
        Cria nova instância MSS a cada chamada (thread-safety no Windows).
        """
        import mss
        with mss.mss() as sct:
            monitor = sct.monitors[0]  # Tela inteira
            screenshot = sct.grab(monitor)

            # Converter para PIL Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            img = img.resize((self.resolution, self.resolution), Image.LANCZOS)

            # Converter para JPEG base64
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=60)
            return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def capture_frame_pil(self) -> Image.Image:
        """Captura frame e retorna como PIL Image (para preview GUI).
        Cria nova instância MSS a cada chamada.
        """
        import mss
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            return img.resize((320, 200), Image.LANCZOS)

    async def stream_frames(self, queue: asyncio.Queue):
        """Loop assíncrono que coloca frames na fila."""
        self.running = True
        interval = 1.0 / self.fps
        while self.running:
            try:
                frame_b64 = await asyncio.to_thread(self.capture_frame)
                # Descarta frame antigo se fila cheia
                if queue.full():
                    try:
                        queue.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                await queue.put(frame_b64)
            except Exception as e:
                print(f"[ScreenCapture] Erro: {e}")
            await asyncio.sleep(interval)

    def stop(self):
        """Para a captura."""
        self.running = False
