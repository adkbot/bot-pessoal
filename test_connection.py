"""Test mínimo de conexão com Gemini Live API."""
import asyncio
from google import genai

print(f"google-genai version: {genai.__version__}")

async def test():
    client = genai.Client(api_key="AIzaSyALB9VL9av8TEEqdMciGyw4TrpgYYbDIus")
    
    config = {"response_modalities": ["AUDIO"]}
    model = "gemini-2.5-flash-native-audio-preview-12-2025"
    
    print(f"Tentando conectar em: {model}")
    try:
        async with client.aio.live.connect(model=model, config=config) as session:
            print("SUCESSO! Conectado ao Gemini Live API!")
            # enviar texto simples
            await session.send_client_content(
                turns=genai.types.Content(
                    role="user",
                    parts=[genai.types.Part(text="Diga apenas oi")]
                )
            )
            turn = session.receive()
            async for r in turn:
                print(f"Resposta tipo: {type(r).__name__}")
                if r.server_content and r.server_content.model_turn:
                    for part in r.server_content.model_turn.parts:
                        if part.text:
                            print(f"Texto: {part.text}")
                        if part.inline_data:
                            print(f"Áudio: {len(part.inline_data.data)} bytes")
                break
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
