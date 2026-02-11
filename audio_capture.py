"""
Módulo de captura e reprodução de áudio.
Captura do microfone em 16-bit PCM 16kHz mono.
Reproduz áudio de resposta a 24kHz.
"""

import asyncio
import pyaudio


class AudioCapture:
    """Gerencia entrada e saída de áudio com PyAudio."""

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    SEND_SAMPLE_RATE = 16000
    RECEIVE_SAMPLE_RATE = 24000
    CHUNK_SIZE = 1024

    def __init__(self):
        self.pya = pyaudio.PyAudio()
        self.mic_stream = None
        self.speaker_stream = None
        self.running = False
        self.mic_muted = False

    def _open_mic(self):
        """Abre o stream do microfone."""
        mic_info = self.pya.get_default_input_device_info()
        self.mic_stream = self.pya.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=self.CHUNK_SIZE,
        )

    def _open_speaker(self):
        """Abre o stream do alto-falante."""
        self.speaker_stream = self.pya.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RECEIVE_SAMPLE_RATE,
            output=True,
        )

    async def stream_mic(self, queue: asyncio.Queue):
        """Loop assíncrono que captura áudio do microfone e coloca na fila."""
        self.running = True
        await asyncio.to_thread(self._open_mic)
        while self.running:
            try:
                data = await asyncio.to_thread(
                    self.mic_stream.read, self.CHUNK_SIZE, exception_on_overflow=False
                )
                if not self.mic_muted:
                    msg = {"data": data, "mime_type": "audio/pcm"}
                    if queue.full():
                        try:
                            queue.get_nowait()
                        except asyncio.QueueEmpty:
                            pass
                    await queue.put(msg)
            except Exception as e:
                print(f"[AudioCapture] Erro mic: {e}")
                await asyncio.sleep(0.1)

    async def play_audio(self, queue: asyncio.Queue):
        """Loop assíncrono que reproduz áudio da fila no alto-falante."""
        await asyncio.to_thread(self._open_speaker)
        while True:
            try:
                audio_data = await queue.get()
                if audio_data is None:
                    break
                await asyncio.to_thread(self.speaker_stream.write, audio_data)
            except Exception as e:
                print(f"[AudioCapture] Erro speaker: {e}")

    def toggle_mic(self):
        """Liga/desliga o microfone."""
        self.mic_muted = not self.mic_muted
        return self.mic_muted

    def stop(self):
        """Fecha todos os streams de áudio."""
        self.running = False
        if self.mic_stream:
            try:
                self.mic_stream.stop_stream()
                self.mic_stream.close()
            except Exception:
                pass
        if self.speaker_stream:
            try:
                self.speaker_stream.stop_stream()
                self.speaker_stream.close()
            except Exception:
                pass
        self.pya.terminate()
