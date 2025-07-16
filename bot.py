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

SERVICES_LIST = [
    ("Annual dental check-up", "1,400"),
    ("Cleaning and polishing", "950"),
    ("Specialist diagnostics", "1,290"),
    ("Tooth-colored fillings", "1,150"),
    ("Crowns", "7,950"),
    ("Root canal (per hour)", "2,600"),
    ("Tooth extraction", "1,350"),
    ("Bleaching (jaw)", "2,500"),
    ("Dentures", "14,010"),
]

SERVICE_KEYWORDS = {
    "check": ("Annual dental check-up", "1,400"),
    "clean": ("Cleaning and polishing", "950"),
    "hygien": ("Cleaning and polishing", "950"),
    "diagnos": ("Specialist diagnostics", "1,290"),
    "acute": ("Acute/general dentist examination", "770"),
    "consult": ("Consultation/plan", "1,070"),
    "fill": ("Tooth-colored fillings", "1,150"),
    "crown": ("Crowns", "7,950"),
    "dentur": ("Dentures", "14,010"),
    "prosthetic": ("Dentures", "14,010"),
    "root": ("Root canal treatment (per hour)", "2,600"),
    "canal": ("Root canal treatment (per hour)", "2,600"),
    "extract": ("Tooth extraction", "1,350"),
    "surgic": ("Surgical extraction", "3,440"),
    "period": ("Periodontal treatment", "1,260"),
    "prevent": ("Preventive (hour)", "1,600"),
    "bleach": ("Bleaching (single jaw)", "2,500"),
    "x-ray": ("X-ray per image", "160"),
    "panorama": ("Panoramic x-ray", "820"),
    "anesth": ("Local anesthesia", "210"),
    "core": ("Core build-up with titanium post", "3,140"),
    "drap": ("Surgical draping", "570"),
    "journal": ("Journal printout by mail", "150"),
}

DOCTORS = [
    ("Manzar Din", "Implant prosthetics, advanced restorative"),
    ("Naeem Khan", "Patient-centered general dentistry"),
    ("Areeb Raja", "Comprehensive, gentle care"),
    ("Dhiya Alkassar", "Comfort-focused general dentistry"),
    ("Jawad Afzal", "Professional, thorough dentistry"),
    ("Noor Alam", "Quality, clear communication"),
    ("Wei Qi Fang", "Preventive, general dentistry"),
    ("Amer Ahmed", "Implants, tooth replacement"),
    ("Mohammed Moafi", "Oral surgery, implants"),
]

# --- Replies generator ---
def get_services_reply():
    lines = []
    for name, price in SERVICES_LIST[:4]:
        lines.append(f"{name}: kr {price}")
    return "\n".join(lines) + "\n…and more. Ask for a specific price."

def get_doctors_reply():
    snippet = "; ".join([f"{n} ({info})" for n, info in DOCTORS[:4]])
    return f"{snippet}\n…and more specialist dentists."

def lookup_service_price(user_msg: str):
    for k, (name, price) in SERVICE_KEYWORDS.items():
        if k in user_msg:
            return f"{name}: kr {price}."
    return None

def get_location_reply():
    return "Din Tannklinikk is at Helsfyr, Oslo. Open 9am–6pm. Website: dintannklinikk.no"

def get_booking_contact_reply():
    return "To book: Use https://dintannklinikk.no/ or call our 24/7 AI Receptionist +123 456 7890."

def get_payment_reply():
    return "We accept NAV, Helfo, and offer flexible installment solutions."

def get_reviews_reply():
    return "We are known for skilled, professional, friendly dentists and reasonable prices."

# --- API calls ---
async def call_groq_api_with_history(system_prompt: str, history: list):
    # Build messages for chat completion
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)  # user and assistant messages

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
        audio_dir = "static/audio"
        os.makedirs(audio_dir, exist_ok=True)
        fname = f"{uuid.uuid4().hex}.mp3"
        path = os.path.join(audio_dir, fname)
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(
                "https://api.hume.ai/v0/tts/file",
                headers={"X-Hume-Api-Key": HUME_API_KEY, "Content-Type": "application/json"},
                json={
                    "utterances": [{"text": text, "description": VOICE_DESCRIPTION}],
                    "format": {"type": "mp3", "bitrate_kbps": 48},
                    "num_generations": 1,
                }
            )
            response.raise_for_status()
            with open(path, "wb") as f:
                f.write(response.content)
        return f"/static/audio/{fname}"
    except Exception:
        traceback.print_exc()
        return ""

# --- ROUTE ---
@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message", "").strip()
        session_id = data.get("session_id")
        user_input_lower = user_input.lower()

        # Create or retrieve session
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

        # --- Append user message to history ---
        session["history"].append({"role": "user", "content": user_input})

        is_booking_keyword = any(word in user_input_lower for word in ["book", "appointment", "schedule"])

        # -- Booking flow --
        if session["booking_in_progress"] or is_booking_keyword:
            if not session["booking_in_progress"]:
                session["booking_in_progress"] = True

            if session.get("waiting_confirmation"):
                if user_input_lower in ["yes", "y", "confirm"]:
                    d = session["booking_data"]
                    confirm_msg = f"Your appointment is booked, {d.get('name','')}, on {d.get('date','')} at {d.get('time','')}. Thank you!"
                    # Clear session data (can be improved to keep history if needed)
                    booking_sessions.pop(session_id, None)
                    audio_url = await call_hume_tts(confirm_msg)
                    # Append bot answer to history (not necessary, session cleared)
                    return JSONResponse({
                        "response": confirm_msg,
                        "audio_url": audio_url,
                        "session_id": session_id,
                    })
                elif user_input_lower in ["no", "n", "cancel"]:
                    cancel_msg = "Booking cancelled. Let me know if you want to book again."
                    booking_sessions.pop(session_id, None)
                    audio_url = await call_hume_tts(cancel_msg)
                    return JSONResponse({
                        "response": cancel_msg,
                        "audio_url": audio_url,
                        "session_id": session_id,
                    })
                else:
                    ask_confirm = "Please reply 'yes' to confirm or 'no' to cancel."
                    session["history"].append({"role": "assistant", "content": ask_confirm})
                    audio_url = await call_hume_tts(ask_confirm)
                    return JSONResponse({
                        "response": ask_confirm,
                        "audio_url": audio_url,
                        "session_id": session_id,
                    })

            # Gather booking fields one-by-one
            if session["awaiting_field"]:
                session["booking_data"][session["awaiting_field"]] = user_input
                session["awaiting_field"] = None
            for field in REQUIRED_BOOKING_FIELDS:
                if field not in session["booking_data"] or not session["booking_data"][field].strip():
                    session["awaiting_field"] = field
                    prompt = FIELD_PROMPTS[field]
                    session["history"].append({"role": "assistant", "content": prompt})
                    audio_url = await call_hume_tts(prompt)
                    return JSONResponse({
                        "response": prompt,
                        "audio_url": audio_url,
                        "session_id": session_id,
                    })

            d = session["booking_data"]
            conf_text = f"Thanks {d['name']}. Confirm appointment on {d['date']} at {d['time']}? (yes/no)"
            session["waiting_confirmation"] = True
            session["history"].append({"role": "assistant", "content": conf_text})
            audio_url = await call_hume_tts(conf_text)
            return JSONResponse({
                "response": conf_text,
                "audio_url": audio_url,
                "session_id": session_id,
            })

        # --- Quick shortcut replies before fallback to LLM ---
        if "service" in user_input_lower or "treatment" in user_input_lower:
            msg = get_services_reply()
            session["history"].append({"role": "assistant", "content": msg})
            audio_url = await call_hume_tts(msg)
            return JSONResponse({"response": msg, "audio_url": audio_url, "session_id": session_id})

        if "price" in user_input_lower or "cost" in user_input_lower:
            price_msg = lookup_service_price(user_input_lower)
            if price_msg:
                session["history"].append({"role": "assistant", "content": price_msg})
                audio_url = await call_hume_tts(price_msg)
                return JSONResponse({"response": price_msg, "audio_url": audio_url, "session_id": session_id})

        if any(k in user_input_lower for k in ["doctor", "dentist", "staff", "team"]):
            doc_msg = get_doctors_reply()
            session["history"].append({"role": "assistant", "content": doc_msg})
            audio_url = await call_hume_tts(doc_msg)
            return JSONResponse({"response": doc_msg, "audio_url": audio_url, "session_id": session_id})

        if any(k in user_input_lower for k in ["address", "where", "location", "open", "hour", "contact"]):
            loc_msg = get_location_reply()
            session["history"].append({"role": "assistant", "content": loc_msg})
            audio_url = await call_hume_tts(loc_msg)
            return JSONResponse({"response": loc_msg, "audio_url": audio_url, "session_id": session_id})

        if "book" in user_input_lower:
            book_msg = get_booking_contact_reply()
            session["history"].append({"role": "assistant", "content": book_msg})
            audio_url = await call_hume_tts(book_msg)
            return JSONResponse({"response": book_msg, "audio_url": audio_url, "session_id": session_id})

        if any(k in user_input_lower for k in ["nav", "insurance", "pay", "installment", "helfo"]):
            pay_msg = get_payment_reply()
            session["history"].append({"role": "assistant", "content": pay_msg})
            audio_url = await call_hume_tts(pay_msg)
            return JSONResponse({"response": pay_msg, "audio_url": audio_url, "session_id": session_id})

        if any(k in user_input_lower for k in ["review", "experience", "good", "best"]):
            rev_msg = get_reviews_reply()
            session["history"].append({"role": "assistant", "content": rev_msg})
            audio_url = await call_hume_tts(rev_msg)
            return JSONResponse({"response": rev_msg, "audio_url": audio_url, "session_id": session_id})

        # --- Fallback: Call LLM with full history ---
        ai_reply = await call_groq_api_with_history(SYSTEM_PROMPT, session["history"])
        session["history"].append({"role": "assistant", "content": ai_reply})
        audio_url = await call_hume_tts(ai_reply)

        return JSONResponse({
            "response": ai_reply,
            "audio_url": audio_url,
            "session_id": session_id
        })

    except Exception as e:
        traceback.print_exc()
        return PlainTextResponse(f"Error: {e}", status_code=500)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

