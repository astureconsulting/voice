import os
import uuid
import asyncio
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
import traceback
import json

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

# ---------- 🤖 Stream from Groq API ----------
async def call_groq_api_stream(user_message: str):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLAMA3_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "stream": True,
        "temperature": 0.5,
        "max_tokens": 120
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as response:
            partial_response = ""
            async for line in response.aiter_lines():
                if line.strip().startswith("data: "):
                    chunk = line.strip().replace("data: ", "")
                    if chunk == "[DONE]":
                        break
                    try:
                        content = json.loads(chunk)["choices"][0]["delta"].get("content", "")
                        partial_response += content
                        yield content, partial_response
                    except Exception:
                        continue

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
        async with httpx.AsyncClient(timeout=30.0) as client:
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

        full_response = ""
        sentence_end_reached = False
        first_sentence = ""
        quick_audio_url = ""
        full_audio_url = ""

        # Step 1: Stream Groq response
        async for token, accumulated in call_groq_api_stream(user_input):
            full_response += token
            if not sentence_end_reached and "." in accumulated:
                first_sentence = accumulated.split(".")[0] + "."
                print("🎯 Sending first sentence to TTS:", first_sentence)
                quick_audio_url = await call_hume_tts(first_sentence)
                sentence_end_reached = True

        # Step 2: Generate full TTS after full response
        print("🎧 Generating full TTS audio...")
        full_audio_url = await call_hume_tts(full_response)

        print("✅ Final response:", full_response)
        print("🔊 Quick audio path:", quick_audio_url)
        print("🔊 Full audio path:", full_audio_url)

        return JSONResponse({
            "response": full_response.strip(),
            "quick_audio_url": quick_audio_url,
            "full_audio_url": full_audio_url
        })

    except Exception as e:
        print("❌ Internal Error:")
        traceback.print_exc()
        return PlainTextResponse(f"Internal server error: {e}", status_code=500)

# ---------- 🗂️ Static File Mount ----------
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/", StaticFiles(directory=".", html=True), name="root")

# ---------- 🚀 Local Dev Server ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
