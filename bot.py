# import os
# import uuid
# import asyncio
# import httpx
# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse, PlainTextResponse
# from fastapi.staticfiles import StaticFiles
# import traceback
# import uvicorn
# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware



# # ---------- 🔧 Configuration ----------
# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
# HUME_API_KEY = os.getenv("HUME_API_KEY", "qP6pf2ZKlzDnDJPEUBT0RXgYzX5P24MBAALbbTRaGANbf9Mz")
# LLAMA3_MODEL = "llama3-8b-8192"
# VOICE_DESCRIPTION = "friendly, natural young assistant, warm, quick response, clear, enthusiastic"

# SYSTEM_PROMPT = (
#     "You are a smart, friendly, helpful voice AI assistant. "
#     "Respond briefly, clearly, and naturally in under 20 words. "
#     "Be conversational and to the point. Avoid repeating or over-explaining."
# )

# # ---------- 🚀 Initialize FastAPI ----------
# app = FastAPI()

# # ---------- 🌐 Enable CORS ----------
# origins = [
#     "https://voiceagentwebring-production.up.railway.app",  # your frontend domain
#     # Add other allowed domains here if needed
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,      # Set to ["*"] only for development
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# # ---------- 🤖 Call LLM API ----------
# async def call_groq_api(user_message: str) -> str:
#     try:
#         async with httpx.AsyncClient(timeout=5.0) as client:
#             response = await client.post(
#                 "https://api.groq.com/openai/v1/chat/completions",
#                 headers={
#                     "Authorization": f"Bearer {GROQ_API_KEY}",
#                     "Content-Type": "application/json"
#                 },
#                 json={
#                     "model": LLAMA3_MODEL,
#                     "messages": [
#                         {"role": "system", "content": SYSTEM_PROMPT},
#                         {"role": "user", "content": user_message}
#                     ],
#                     "temperature": 0.5,
#                     "max_tokens": 120
#                 }
#             )
#             response.raise_for_status()
#             return response.json()["choices"][0]["message"]["content"].strip()
#     except Exception as e:
#         print("❌ Groq API Error:")
#         traceback.print_exc()
#         raise Exception("Groq API Error: " + str(e))

# # ---------- 🔉 Call Hume TTS ----------
# async def call_hume_tts(text: str) -> str:
#     try:
#         audio_dir = "static/audio"
#         os.makedirs(audio_dir, exist_ok=True)
#         file_name = f"{uuid.uuid4().hex}.mp3"
#         file_path = os.path.join(audio_dir, file_name)

#         async with httpx.AsyncClient(timeout=60.0) as client:
#             response = await client.post(
#                 "https://api.hume.ai/v0/tts/file",
#                 headers={
#                     "X-Hume-Api-Key": HUME_API_KEY,
#                     "Content-Type": "application/json"
#                 },
#                 json={
#                     "utterances": [
#                         {
#                             "text": text,
#                             "description": VOICE_DESCRIPTION
#                         }
#                     ],
#                     "format": {
#                         "type": "mp3",
#                         "bitrate_kbps": 48  # useful for lower latency
#                     },
#                     "num_generations": 1
#                 }
#             )
#             response.raise_for_status()
#             with open(file_path, "wb") as f:
#                 f.write(response.content)
#             return f"/static/audio/{file_name}"
#     except Exception as e:
#         print("❌ Hume API Error:")
#         traceback.print_exc()
#         raise Exception("Hume API Error: " + str(e))

# # ---------- 💬 Chat Endpoint ----------
# @app.post("/api/chat")
# async def chat(request: Request):
#     try:
#         data = await request.json()
#         user_input = data.get("message", "")

#         if not user_input:
#             return JSONResponse({"error": "No input provided"}, status_code=400)

#         print("🧠 User input:", user_input)

#         # Call AI model
#         ai_reply = await call_groq_api(user_input)
#         print("✅ Text Response:", ai_reply)

#         # Convert to speech
#         audio_url = await call_hume_tts(ai_reply)
#         print("🔊 Audio URL:", audio_url)

#         return JSONResponse({
#             "response": ai_reply,
#             "audio_url": audio_url
#         })

#     except Exception as e:
#         print("❌ Internal Server Error")
#         traceback.print_exc()
#         return PlainTextResponse(f"Error: {e}", status_code=500)

# # ---------- 🗂️ Mount Static Folder ----------
# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/", StaticFiles(directory=".", html=True), name="root")

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 8080))
#     app.run(host='0.0.0.0', port=port)
import os
import uuid
import traceback
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# --- CONFIG ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
HUME_API_KEY = os.getenv("HUME_API_KEY", "qP6pf2ZKlzDnDJPEUBT0RXgYzX5P24MBAALbbTRaGANbf9Mz")
LLAMA3_MODEL = "llama3-8b-8192"
VOICE_DESCRIPTION = "friendly, natural young assistant, warm, quick response, clear, enthusiastic"

SYSTEM_PROMPT = """
You are Din Tannklinikk's expert digital assistant. 
Always reply in a warm, concise, professional style, under 6 lines. 

If asked about services, list 3–4 main services with prices, then say '…and more'.
If asked for price, give exact price for that service.
If asked about doctors/staff: list names and specialization briefly, mention more exist.
If asked about location, hours, contact, payment, or booking, reply directly.

Booking steps: ask for name, phone, email, date, time one by one in friendly tone.
Confirm all details before final booking.

Clinic location: Helsfyr, Oslo, 20+ years experience.
Doctors include Manzar Din (implants), Naeem Khan (patient-focused), Areeb Raja, Dhiya Alkassar, Jawad Afzal, Noor Alam, Wei Qi Fang, Amer Ahmed, Mohammed Moafi.
Services and prices: See below.

- Annual dental check-up: 1,400 NOK
- Cleaning: 950 NOK
- Specialist diagnostic: 1,290 NOK
- Acute/general exam: 770 NOK
- Consultation/treatment plan: 1,070 NOK
- Tooth-colored fillings: 1,150 NOK
- Crowns: 7,950 NOK
- Dentures: 14,010 NOK
- Root canal (per hour): 2,600 NOK
- Tooth extraction: 1,350 NOK
- Surgical extraction: 3,440 NOK
- Periodontal treatment: 1,260 NOK
- Preventive treatment (hourly): 1,600 NOK
- Bleaching (single jaw): 2,500 NOK
- Bleaching (upper/lower jaw): 3,500 NOK
- X-ray per image: 160 NOK
- Panoramic x-ray: 820 NOK
- Local anesthesia: 210 NOK
- Hygiene supplement: 170 NOK
- Core build-up with titanium post: 3,140 NOK
- Surgical draping: 570 NOK
- Journal printout by mail: 150 NOK

Payments: Accept NAV, Helfo; flexible installment options.
Booking: Use https://dintannklinikk.no/ or call +123 456 7890 24/7 AI receptionist.
Opening hours: 9am to 6pm.

Maintain a friendly, clear tone. Use Norwegian or English based on user input.
"""

app = FastAPI()

origins = ["https://voiceagentwebring-production.up.railway.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# --- STATE & CONSTANTS ----
booking_sessions = {}

REQUIRED_BOOKING_FIELDS = ["name", "phone", "email", "date", "time"]
FIELD_PROMPTS = {
    "name": "Please provide your full name.",
    "phone": "May I have your phone number?",
    "email": "Could you share your email address?",
    "date": "What date would you like to book? (e.g., 2025-08-01)",
    "time": "What time do you prefer? (e.g., 14:30)"
}

# (Include SERVICES_LIST, SERVICE_KEYWORDS, DOCTORS, etc., unchanged here)

# --- Replies generator and helper functions here ---
# (You can re-use your previous code unchanged)

# --- API calls ---
async def call_groq_api_with_history(system_prompt: str, history: list):
    messages = [{"role": "system", "content": system_prompt}] + history
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": LLAMA3_MODEL,
                    "messages": messages,
                    "temperature": 0.4,
                    "max_tokens": 80,
                }
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()
            return content
    except Exception:
        traceback.print_exc()
        return "Sorry, I could not access the clinic info right now."

async def call_hume_tts(text: str) -> str:
    try:
        text = text.strip()
        if not text:
            return ""
        if len(text) > 500:
            text = text[:500]

        audio_dir = "static/audio"
        os.makedirs(audio_dir, exist_ok=True)
        file_name = f"{uuid.uuid4().hex}.mp3"
        file_path = os.path.join(audio_dir, file_name)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.hume.ai/v0/tts/file",
                headers={
                    "X-Hume-Api-Key": HUME_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "utterances": [{"text": text, "description": VOICE_DESCRIPTION}],
                    "format": {"type": "mp3", "bitrate_kbps": 48},
                    "num_generations": 1
                }
            )
            response.raise_for_status()
            data = response.json()
            audio_url = data.get("generations", [{}])[0].get("url")
            if not audio_url:
                print("No audio URL returned from Hume TTS API:", data)
                return ""

            # Download the actual MP3 file from audio_url
            audio_resp = await client.get(audio_url)
            audio_resp.raise_for_status()
            with open(file_path, "wb") as f:
                f.write(audio_resp.content)

        return f"/static/audio/{file_name}"

    except httpx.HTTPStatusError as e:
        print(f"Hume TTS HTTP error ({e.response.status_code}): {e.response.text}")
        return ""
    except Exception as e:
        print(f"Hume TTS error: {e}")
        return ""

@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message", "").strip()
        session_id = data.get("session_id")
        user_input_lower = user_input.lower()

        if not session_id or session_id not in booking_sessions:
            session_id = str(uuid.uuid4())
            booking_sessions[session_id] = {
                "booking_data": {},
                "booking_in_progress": False,
                "awaiting_field": None,
                "waiting_confirmation": False,
                "history": []
            }
        session = booking_sessions[session_id]

        session["history"].append({"role": "user", "content": user_input})

        # Implement your booking logic and shortcuts similarly here...

        # Quick answers shortcuts etc.
        # (Use your existing logic here as you already defined)

        # Fallback - call LLM with conversation history
        llm_reply = await call_groq_api_with_history(SYSTEM_PROMPT, session["history"])
        session["history"].append({"role": "assistant", "content": llm_reply})
        audio_url = await call_hume_tts(llm_reply)

        return JSONResponse({
            "response": llm_reply,
            "audio_url": audio_url,
            "session_id": session_id,
        })

    except Exception as e:
        traceback.print_exc()
        return PlainTextResponse(f"Error: {e}", status_code=500)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
