import os
import uuid
import asyncio
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
import traceback
import uvicorn

from fastapi.middleware.cors import CORSMiddleware

# 👇 Add this to allow frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://voiceagentwebring-production.up.railway.app"],  # your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------- 🔧 Configuration ----------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
HUME_API_KEY = os.getenv("HUME_API_KEY", "qP6pf2ZKlzDnDJPEUBT0RXgYzX5P24MBAALbbTRaGANbf9Mz")
LLAMA3_MODEL = "llama3-8b-8192"
VOICE_DESCRIPTION = "friendly, natural young assistant, warm, quick response, clear, enthusiastic"

SYSTEM_PROMPT = (
    "You are a smart, friendly, helpful voice AI assistant. "
    "Respond briefly, clearly, and naturally in under 20 words. "
    "Be conversational and to the point. Avoid repeating or over-explaining."
)

# ---------- ⚡ FastAPI App ----------
app = FastAPI()

# ---------- 🤖 Async Call to Groq API ----------
async def call_groq_api(user_message: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": LLAMA3_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.5,
        "max_tokens": 120
    }

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("❌ Groq API Error:")
        traceback.print_exc()
        raise Exception("Groq API Error: " + str(e))

# ---------- 🔊 Async Call to Hume TTS ----------
async def call_hume_tts(text: str) -> str:
    audio_dir = "static/audio"
    os.makedirs(audio_dir, exist_ok=True)

    file_name = f"{uuid.uuid4().hex}.mp3"
    file_path = os.path.join(audio_dir, file_name)

    url = "https://api.hume.ai/v0/tts/file"
    headers = {
        "X-Hume-Api-Key": HUME_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "utterances": [
            {
                "text": text,
                "description": VOICE_DESCRIPTION
            }
        ],
        "format": {
            "type": "mp3"
        },
        "num_generations": 1
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            with open(file_path, "wb") as f:
                f.write(response.content)
            return f"/static/audio/{file_name}"
    except Exception as e:
        print("❌ Hume API Error:")
        traceback.print_exc()
        raise Exception("Hume API Error: " + str(e))

# ---------- 💬 Chat Endpoint ----------
@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message", "")

        if not user_input:
            return JSONResponse({"error": "No input provided"}, status_code=400)

        print("⚡ User said:", user_input)

        # Step 1: Generate bot response from LLaMA3
        bot_response = await call_groq_api(user_input)
        print("✅ Groq response:", bot_response)

        # Step 2: Generate TTS audio with Hume
        audio_url = await call_hume_tts(bot_response)
        print("🔊 Voice path:", audio_url)

        # Response
        return JSONResponse({
            "response": bot_response,
            "audio_url": audio_url
        })

    except Exception as e:
        print("❌ Internal Error:")
        traceback.print_exc()
        return PlainTextResponse(f"Internal server error: {e}", status_code=500)

# ---------- 🗂️ Static File Mount ----------
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/", StaticFiles(directory=".", html=True), name="root")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
