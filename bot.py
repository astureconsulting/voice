import os
import uuid
import asyncio
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
import traceback
import uvicorn
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



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

# ---------- 🚀 Initialize FastAPI ----------
app = FastAPI()

# ---------- 🌐 Enable CORS ----------
origins = [
    "https://voiceagentwebring-production.up.railway.app",  # your frontend domain
    # Add other allowed domains here if needed
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Set to ["*"] only for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------- 🤖 Call LLM API ----------
async def call_groq_api(user_message: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": LLAMA3_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 120
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("❌ Groq API Error:")
        traceback.print_exc()
        raise Exception("Groq API Error: " + str(e))

# ---------- 🔉 Call Hume TTS ----------
async def call_hume_tts(text: str) -> str:
    try:
        audio_dir = "static/audio"
        os.makedirs(audio_dir, exist_ok=True)
        file_name = f"{uuid.uuid4().hex}.mp3"
        file_path = os.path.join(audio_dir, file_name)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.hume.ai/v0/tts/file",
                headers={
                    "X-Hume-Api-Key": HUME_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "utterances": [
                        {
                            "text": text,
                            "description": VOICE_DESCRIPTION
                        }
                    ],
                    "format": {
                        "type": "mp3",
                        "bitrate_kbps": 48  # useful for lower latency
                    },
                    "num_generations": 1
                }
            )
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

        print("🧠 User input:", user_input)

        # Call AI model
        ai_reply = await call_groq_api(user_input)
        print("✅ Text Response:", ai_reply)

        # Convert to speech
        audio_url = await call_hume_tts(ai_reply)
        print("🔊 Audio URL:", audio_url)

        return JSONResponse({
            "response": ai_reply,
            "audio_url": audio_url
        })

    except Exception as e:
        print("❌ Internal Server Error")
        traceback.print_exc()
        return PlainTextResponse(f"Error: {e}", status_code=500)

# ---------- 🗂️ Mount Static Folder ----------
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/", StaticFiles(directory=".", html=True), name="root")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
