# import os
# import uuid
# import re
# import traceback
# from collections import defaultdict

# import httpx
# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware

# # ---------- 🔧 Configuration ----------
# GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
# HUME_API_KEY = os.getenv("HUME_API_KEY", "Xs2MM3Xx2Y13CRfLBiLNzsaY6niZrqRsoY5yEaVstPQmt0ZI")
# LLAMA3_MODEL = "llama3-8b-8192"
# VOICE_DESCRIPTION = "friendly, natural young assistant, warm, quick response, clear, enthusiastic"

# SYSTEM_PROMPT = """
# You are an expert Virtual Assistant for Dintannklinikk dental clinics. Your task is to answer concisely and clearly about the clinic. Use English for all responses, except prices, which should be given as in Norway (e.g., "fra 1400 kroner"). If asked for booking, collect name, phone, email, date, and time one by one. Otherwise, just answer. Always under 6 lines.
# """

# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
# )

# # Prices in Norwegian krone for TTS quality
# SERVICES = [
#     {"name": "Annual dental check-up (examination, x-rays, cleaning, hygiene)", "price": "fra 1 400 kroner"},
#     {"name": "Cleaning, polishing, and hygiene", "price": "fra 950 kroner"},
#     {"name": "Specialist examination/diagnostics", "price": "fra 1 290 kroner"},
#     {"name": "Acute/general dentist examination", "price": "770 kroner"},
#     {"name": "Consultation/comprehensive treatment plan", "price": "fra 1 070 kroner"},
#     {"name": "Tooth-colored fillings (various surfaces)", "price": "fra 1 150 kroner"},
#     {"name": "Crowns (metal-ceramic, all-ceramic)", "price": "fra 7 950 kroner"},
#     {"name": "Dental prosthetics (full and partial dentures)", "price": "fra 14 010 kroner"},
#     {"name": "Endodontics (root canal treatment)", "price": "2 600 kroner per time"},
#     {"name": "Tooth extraction (simple/complicated)", "price": "fra 1 350 kroner"},
#     {"name": "Surgical extraction", "price": "fra 3 440 kroner"},
#     {"name": "Periodontal treatment (subgingival)", "price": "fra 1 260 kroner"},
#     {"name": "Preventive treatment (hourly)", "price": "fra 1 600 kroner"},
#     {"name": "Bleaching (single jaw)", "price": "2 500 kroner"},
#     {"name": "Bleaching (upper/lower jaw)", "price": "3 500 kroner"},
#     {"name": "X-ray per image", "price": "160 kroner"},
#     {"name": "Panoramic x-ray", "price": "820 kroner"},
#     {"name": "Local anesthesia", "price": "210 kroner"},
#     {"name": "Hygiene supplement", "price": "170 kroner"},
#     {"name": "Core build-up with titanium post", "price": "3 140 kroner"},
#     {"name": "Surgical draping", "price": "570 kroner"},
#     {"name": "Journal printout by mail", "price": "150 kroner"},
# ]

# SERVICE_NAMES = [s["name"].lower() for s in SERVICES]
# sessions = defaultdict(dict)  # session_id -> {'history': [...], 'booking': {...}}

# PRICE_QUESTIONS = [
#     "price", "prices", "cost", "costs", "fee", "fees", "rate", "rates", "charge", "charges", "treatment cost", "pricelist"
# ]

# def extract_price_values(price_str):
#     # E.g. "fra 1 400 kroner", "2 600 kroner"
#     m = re.search(r'(\d[\d\s ]*)\s*kroner', price_str.replace('\xa0', ' '))
#     if m:
#         val = m.group(1)
#         val = val.replace(' ', '').replace('\xa0', '')
#         try:
#             return int(val)
#         except Exception:
#             return None
#     return None

# def get_price_range():
#     prices = []
#     for s in SERVICES:
#         p = extract_price_values(s["price"])
#         if p is not None:
#             prices.append(p)
#     if not prices:
#         return None, None
#     return min(prices), max(prices)

# def find_service_in_text(user_input):
#     input_lower = user_input.lower()
#     for s in SERVICES:
#         base_name = s["name"].split("(")[0].strip().lower()
#         if base_name in input_lower:
#             return s
#         words = base_name.replace('-', ' ').replace(',', '').split()
#         for w in words:
#             if w in input_lower and len(w) > 3:
#                 return s
#     return None

# # --- LLM CALL ---
# async def call_groq_api(user_message: str) -> str:
#     try:
#         async with httpx.AsyncClient(timeout=5.0) as client:
#             response = await client.post(
#                 "https://api.groq.com/openai/v1/chat/completions",
#                 headers={
#                     "Authorization": f"Bearer {GROQ_API_KEY}",
#                     "Content-Type": "application/json",
#                 },
#                 json={
#                     "model": LLAMA3_MODEL,
#                     "messages": [
#                         {"role": "system", "content": SYSTEM_PROMPT},
#                         {"role": "user", "content": f"{user_message}\nReply in 80 characters or less. No lists or formatting."},
#                     ],
#                     "temperature": 0.3,
#                     "max_tokens": 180,
#                 },
#             )
#             response.raise_for_status()
#             return response.json()["choices"][0]["message"]["content"].strip()
#     except Exception as e:
#         print("Groq API Error:", str(e))
#         traceback.print_exc()
#         return "Sorry, can't answer now."

# # --- TTS CALL ---
# async def call_hume_tts(text: str) -> str:
#     try:
#         audio_dir = "static/audio"
#         os.makedirs(audio_dir, exist_ok=True)
#         file_name = f"{uuid.uuid4().hex}.mp3"
#         file_path = os.path.join(audio_dir, file_name)
#         async with httpx.AsyncClient(timeout=10.0) as client:
#             response = await client.post(
#                 "https://api.hume.ai/v0/tts/file",
#                 headers={
#                     "X-Hume-Api-Key": HUME_API_KEY,
#                     "Content-Type": "application/json",
#                 },
#                 json={
#                     "utterances": [{"text": text, "description": VOICE_DESCRIPTION}],
#                     "format": {"type": "mp3", "bitrate_kbps": 48},
#                     "num_generations": 1,
#                 },
#             )
#             response.raise_for_status()
#             with open(file_path, "wb") as f:
#                 f.write(response.content)
#             return f"/static/audio/{file_name}"
#     except Exception as e:
#         print("Hume API Error:", str(e))
#         traceback.print_exc()
#         return ""

# @app.post("/api/chat")
# async def chat(request: Request):
#     try:
#         data = await request.json()
#         user_input = data.get("message", "").strip()
#         session_id = data.get("session_id") or str(uuid.uuid4())
#         session = sessions[session_id]
#         history = session.setdefault("history", [])
#         booking = session.setdefault("booking", {})
#         awaiting = booking.get("awaiting")
#         ai_reply = ""

#         # Booking flow (English)
#         if awaiting:
#             step = awaiting
#             value = user_input
#             if step == "name":
#                 booking["name"] = value
#                 booking["awaiting"] = "phone"
#                 ai_reply = "What is your phone number?"
#             elif step == "phone":
#                 booking["phone"] = value
#                 booking["awaiting"] = "email"
#                 ai_reply = "What is your email address?"
#             elif step == "email":
#                 booking["email"] = value
#                 booking["awaiting"] = "date"
#                 ai_reply = "Preferred date?"
#             elif step == "date":
#                 booking["date"] = value
#                 booking["awaiting"] = "time"
#                 ai_reply = "Preferred time?"
#             elif step == "time":
#                 booking["time"] = value
#                 booking["awaiting"] = None
#                 ai_reply = (
#                     f"Booking for {booking['date']} at {booking['time']}. "
#                     "You'll get a confirmation email soon. Thank you for booking."
#                 )
#             else:
#                 ai_reply = "There was a booking error. Please try again."
#         # Price queries (Norwegian kroner only for prices!)
#         elif any(q in user_input.lower() for q in PRICE_QUESTIONS):
#             found = find_service_in_text(user_input)
#             if found:
#                 ai_reply = f"{found['name']}: {found['price']}."
#             else:
#                 minp, maxp = get_price_range()
#                 if minp is not None and maxp is not None:
#                     ai_reply = f"Prices range from {minp} kroner to {maxp} kroner."
#                 else:
#                     ai_reply = "Please ask for a specific treatment price."
#         # Book appointment
#         elif any(word in user_input.lower() for word in ["book", "appointment", "reserve time", "møte", "bestill", "time"]):
#             booking.clear()
#             booking["awaiting"] = "name"
#             ai_reply = "What is your name?"
#         # Service queries
#         elif "service" in user_input.lower() or "tjeneste" in user_input.lower():
#             s_list = ", ".join(s["name"] for s in SERVICES[:3])
#             ai_reply = f"We offer {s_list}, and more."
#         elif any(name in user_input.lower() for name in SERVICE_NAMES):
#             found = next((s for s in SERVICES if s["name"].lower() in user_input.lower()), None)
#             if found:
#                 ai_reply = f"{found['name']}: {found['price']}."
#             else:
#                 ai_reply = "Service not found."
#         # Fallback: call LLM
#         else:
#             ai_reply = await call_groq_api(user_input)

#         history.append({"user": user_input, "bot": ai_reply})
#         audio_url = await call_hume_tts(ai_reply)

#         return JSONResponse(
#             {"response": ai_reply, "audio_url": audio_url, "session_id": session_id}
#         )
#     except Exception as e:
#         print("Internal Server Error")
#         traceback.print_exc()
#         # Always return JSON error to client
#         return JSONResponse({"error": str(e)}, status_code=500)

# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/", StaticFiles(directory=".", html=True), name="root")

# if __name__ == "__main__":
#     import uvicorn
#     port = int(os.environ.get("PORT", 8080))
#     uvicorn.run("main:app", host="0.0.0.0", port=port)




import os
import uuid
import re
import traceback
from collections import defaultdict

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# ---------- 🔧 Configuration ----------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
HUME_API_KEY = os.getenv("HUME_API_KEY", "PeS9OER7MSDnERrXgaziLFaOpWHlVsWzl7f4wBXQqBFuIaKE")
LLAMA3_MODEL = "llama3-8b-8192"
VOICE_DESCRIPTION = "friendly, natural young assistant, warm, quick response, clear, enthusiastic"

SYSTEM_PROMPT = """
You are an expert Virtual Assistant for Dintannklinikk dental clinics. Your task is to answer concisely and clearly about the clinic. Use English for all responses, except prices, which should be given as in Norway (e.g., "fra 1400 kroner"). If asked for booking, collect name, phone, email, date, and time one by one. Otherwise, just answer. Always under 6 lines.

Clinic Introduction:
- Din Tannklinikk is located in Helsfyr, Oslo.
- Dedicated to providing comfortable and modern dental care with over 20 years of experience.

Team and Expertise:
- Multidisciplinary team including dentists, oral surgeons, and dental health secretaries.
- Specializations across various fields of dentistry.

Meet Our Team:
- Manzar Din – Dentist, expert in implant prosthetics and advanced restorative treatments.
- Naeem Khan – Dentist, known for skill, integrity, and patient-centered care.
- Areeb Raja – Dentist, provides comprehensive dental care with a gentle touch.
- Dhiya Alkassar – Dentist, experienced in broad dental treatments focusing on patient comfort.
- Jawad Afzal – Dentist, recognized for professionalism and thoroughness.
- Noor Alam – Dentist, committed to quality care and clear communication.
- Wei Qi Fang – Dentist, detail-oriented in general and preventive dentistry.
- Amer Ahmed – Dentist, specializes in implant prosthetics and advanced tooth replacement.
- Mohammed Moafi – Oral Surgeon, expert in oral surgery including extractions and implants.

Patient Care Philosophy:
- Focus on empathy, professionalism, and good communication.
- Takes time to understand patient needs and provide clear recommendations.

Modern Technology:
- Uses up-to-date equipment and methods for best possible treatment.

Services Offered (with starting prices):
- Annual dental check-up (examination, x-rays, cleaning, hygiene): from kr 1,400
- Cleaning, polishing, and hygiene: from kr 950
- Specialist examination/diagnostics: from kr 1,290
- Acute/general dentist examination: kr 770
- Consultation/comprehensive treatment plan: from kr 1,070
- Tooth-colored fillings (various surfaces): from kr 1,150
- Crowns (metal-ceramic, all-ceramic): from kr 7,950
- Dental prosthetics (full and partial dentures): from kr 14,010
- Endodontics (root canal treatment): kr 2,600 per hour
- Tooth extraction (simple/complicated): from kr 1,350
- Surgical extraction: from kr 3,440
- Periodontal treatment (subgingival): from kr 1,260
- Preventive treatment (hourly): from kr 1,600
- Bleaching (single jaw): kr 2,500
- Bleaching (upper/lower jaw): kr 3,500
- X-ray per image: kr 160
- Panoramic x-ray: kr 820
- Local anesthesia: kr 210
- Hygiene supplement: kr 170
- Core build-up with titanium post: kr 3,140
- Surgical draping: kr 570
- Journal printout by mail: kr 150

Prices:
- All prices are transparent and competitive.
- Detailed price lists are available on the website or upon request.

Payment and Insurance:
- Accepts NAV-guarantee.
- Offers direct settlement with Helfo.
- Provides flexible installment solutions.

Appointment Flexibility:
- Treatments adapted to fit patient schedules.
- Patients receive clear cost estimates and thorough explanations.

Commitment to Dental Health:
- Encourages prioritizing necessary dental treatment.
- Helps patients achieve good oral health and a radiant smile.

Contact and Booking Information:
- Email & info: https://dintannklinikk.no/
- To book an appointment, email us or call our 24/7 AI Receptionist (+123 456 7890) for immediate assistance.
- Timings: 9am to 6pm.
When a user ask to book an appointment only,then ask for their name, phone number, email, preferred date, and time one by one in a friendly and clear manner otherwise just answer user's Queries. Confirm all details before finalizing the booking.


Reputation:
- Positive patient reviews highlight skill, professionalism, and friendly care.

Patient Reviews:
- “I’ve had many dentists in Norway and I wasn’t happy until I found Dr. Naeem Khan...”
- “Best in Oslo… Trustworthy and highly skilled.”
- “I’m terrified of dentists, but I was so well taken care of...”
- “Professional services, best dentist.”
- “Really good doctor and very sincere.”
- “Quality is high and price is reasonable compared to other dentals in Oslo...”
- “Naeem is incredibly skilled, very professional and pleasant to talk to...”
- “Everyone is very nice and accommodating. Dr. Diyah has been my dentist for many years...
"""

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# Prices in Norwegian krone for TTS quality
SERVICES = [
    {"name": "Annual dental check-up (examination, x-rays, cleaning, hygiene)", "price": "fra 1 400 kroner"},
    {"name": "Cleaning, polishing, and hygiene", "price": "fra 950 kroner"},
    {"name": "Specialist examination/diagnostics", "price": "fra 1 290 kroner"},
    {"name": "Acute/general dentist examination", "price": "770 kroner"},
    {"name": "Consultation/comprehensive treatment plan", "price": "fra 1 070 kroner"},
    {"name": "Tooth-colored fillings (various surfaces)", "price": "fra 1 150 kroner"},
    {"name": "Crowns (metal-ceramic, all-ceramic)", "price": "fra 7 950 kroner"},
    {"name": "Dental prosthetics (full and partial dentures)", "price": "fra 14 010 kroner"},
    {"name": "Endodontics (root canal treatment)", "price": "2 600 kroner per time"},
    {"name": "Tooth extraction (simple/complicated)", "price": "fra 1 350 kroner"},
    {"name": "Surgical extraction", "price": "fra 3 440 kroner"},
    {"name": "Periodontal treatment (subgingival)", "price": "fra 1 260 kroner"},
    {"name": "Preventive treatment (hourly)", "price": "fra 1 600 kroner"},
    {"name": "Bleaching (single jaw)", "price": "2 500 kroner"},
    {"name": "Bleaching (upper/lower jaw)", "price": "3 500 kroner"},
    {"name": "X-ray per image", "price": "160 kroner"},
    {"name": "Panoramic x-ray", "price": "820 kroner"},
    {"name": "Local anesthesia", "price": "210 kroner"},
    {"name": "Hygiene supplement", "price": "170 kroner"},
    {"name": "Core build-up with titanium post", "price": "3 140 kroner"},
    {"name": "Surgical draping", "price": "570 kroner"},
    {"name": "Journal printout by mail", "price": "150 kroner"},
]

SERVICE_NAMES = [s["name"].lower() for s in SERVICES]
sessions = defaultdict(dict)  # session_id -> {'history': [...], 'booking': {...}}

PRICE_QUESTIONS = [
    "price", "prices", "cost", "costs", "fee", "fees", "rate", "rates", "charge", "charges", "treatment cost", "pricelist"
]

def extract_price_values(price_str):
    # E.g. "fra 1 400 kroner", "2 600 kroner"
    m = re.search(r'(\d[\d\s ]*)\s*kroner', price_str.replace('\xa0', ' '))
    if m:
        val = m.group(1)
        val = val.replace(' ', '').replace('\xa0', '')
        try:
            return int(val)
        except Exception:
            return None
    return None

def get_price_range():
    prices = []
    for s in SERVICES:
        p = extract_price_values(s["price"])
        if p is not None:
            prices.append(p)
    if not prices:
        return None, None
    return min(prices), max(prices)

def find_service_in_text(user_input):
    input_lower = user_input.lower()
    for s in SERVICES:
        base_name = s["name"].split("(")[0].strip().lower()
        if base_name in input_lower:
            return s
        words = base_name.replace('-', ' ').replace(',', '').split()
        for w in words:
            if w in input_lower and len(w) > 3:
                return s
    return None

# --- LLM CALL ---
async def call_groq_api(user_message: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": LLAMA3_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"{user_message}\nReply in 80 characters or less. No lists or formatting."},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 180,
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("Groq API Error:", str(e))
        traceback.print_exc()
        return "Sorry, can't answer now."

# --- TTS CALL ---
async def call_hume_tts(text: str) -> str:
    try:
        audio_dir = "static/audio"
        os.makedirs(audio_dir, exist_ok=True)
        file_name = f"{uuid.uuid4().hex}.mp3"
        file_path = os.path.join(audio_dir, file_name)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.hume.ai/v0/tts/file",
                headers={
                    "X-Hume-Api-Key": HUME_API_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "utterances": [{"text": text, "description": VOICE_DESCRIPTION}],
                    "format": {"type": "mp3", "bitrate_kbps": 32},  # reduced bitrate for speed
                    "num_generations": 1,
                },
            )
            response.raise_for_status()
            with open(file_path, "wb") as f:
                f.write(response.content)
            return f"/static/audio/{file_name}"
    except Exception as e:
        print("Hume API Error:", str(e))
        traceback.print_exc()
        return ""

@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message", "").strip()
        session_id = data.get("session_id") or str(uuid.uuid4())
        session = sessions[session_id]
        history = session.setdefault("history", [])
        booking = session.setdefault("booking", {})
        awaiting = booking.get("awaiting")
        ai_reply = ""
        follow_up = None

        user_lower = user_input.lower()

        def is_counter_question(msg: str) -> bool:
            return any(x in msg for x in ["what", "how", "which", "who", "where", "do you", "can you"])


def is_valid_phone(text):
    return bool(re.fullmatch(r"[\d\+\-\s]{7,15}", text))

def is_valid_email(text):
    return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", text))

def is_valid_date(text):
    return bool(re.search(r"\d{1,2}[/\-\. ]\d{1,2}", text)) or any(word in text.lower() for word in ["today", "tomorrow", "monday", "tuesday", "wednesday", "thursday", "friday"])

def is_valid_time(text):
    return bool(re.search(r"\b\d{1,2}(:\d{2})?\s?(am|pm)?\b", text.lower())) or any(w in text.lower() for w in ["morning", "afternoon", "evening"])

# Inside the booking flow logic:
if awaiting:
    step = awaiting
    value = user_input

    if is_counter_question(user_lower):
        # Handle counter-questions as before...
        ...
    elif step == "name":
        booking["name"] = value
        booking["awaiting"] = "phone"
        ai_reply = "What is your phone number?"
    elif step == "phone":
        if not is_valid_phone(value):
            ai_reply = "Sorry, that doesn't look like a phone number. Please try again."
        else:
            booking["phone"] = value
            booking["awaiting"] = "email"
            ai_reply = "What is your email address?"
    elif step == "email":
        if not is_valid_email(value):
            ai_reply = "Hmm, that doesn't seem like a valid email. Please check and try again."
        else:
            booking["email"] = value
            booking["awaiting"] = "date"
            ai_reply = "Preferred date?"
    elif step == "date":
        if not is_valid_date(value):
            ai_reply = "Sorry, I didn’t catch a valid date. Could you please try again?"
        else:
            booking["date"] = value
            booking["awaiting"] = "time"
            ai_reply = "Preferred time?"
    elif step == "time":
        if not is_valid_time(value):
            ai_reply = "That doesn’t seem like a valid time. Could you tell me your preferred time again?"
        else:
            booking["time"] = value
            booking["awaiting"] = None
            ai_reply = (
                f"Booking for {booking['date']} at {booking['time']}. "
                "You'll get a confirmation email soon. Thank you for booking."
            )


        # Price queries (outside booking)
        elif any(q in user_lower for q in PRICE_QUESTIONS):
            found = find_service_in_text(user_input)
            if found:
                ai_reply = f"{found['name']}: {found['price']}."
            else:
                minp, maxp = get_price_range()
                if minp is not None and maxp is not None:
                    ai_reply = f"Prices range from {minp} to {maxp} kroner."
                else:
                    ai_reply = "Please ask for a specific treatment price."

        # Booking initiation
        elif any(word in user_lower for word in ["book", "appointment", "reserve time", "møte", "bestill", "time"]):
            booking.clear()
            booking["awaiting"] = "name"
            ai_reply = "What is your name?"

        # Services info
        elif "service" in user_lower or "tjeneste" in user_lower:
            s_list = ", ".join(s["name"] for s in SERVICES[:3])
            ai_reply = f"We offer {s_list}, and more."
        elif any(name in user_lower for name in SERVICE_NAMES):
            found = next((s for s in SERVICES if s["name"].lower() in user_lower), None)
            if found:
                ai_reply = f"{found['name']}: {found['price']}."
            else:
                ai_reply = "Service not found."

        # General fallback to LLM
        else:
            ai_reply = await call_groq_api(user_input)

        # Combine response and follow-up booking prompt
        final_response = ai_reply
        if follow_up:
            final_response += f" {follow_up}"

        # Add slight buffer before TTS to avoid first-word cut-off
        tts_input = f"\u200B{final_response}"  # \u200B = zero-width space


        history.append({"user": user_input, "bot": final_response})
        audio_url = await call_hume_tts(tts_input)

        return JSONResponse(
            {"response": final_response, "audio_url": audio_url, "session_id": session_id}
        )
    except Exception as e:
        print("Internal Server Error")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)



app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/", StaticFiles(directory=".", html=True), name="root")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
