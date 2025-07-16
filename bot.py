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

# ---------- 🔧 Configuration ----------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
HUME_API_KEY = os.getenv("HUME_API_KEY", "qP6pf2ZKlzDnDJPEUBT0RXgYzX5P24MBAALbbTRaGANbf9Mz")
LLAMA3_MODEL = "llama3-8b-8192"
VOICE_DESCRIPTION = "friendly, natural young assistant, warm, quick response, clear, enthusiastic"

SYSTEM_PROMPT = """
You are an expert Virtual Assistant for Dintannklinikk dental clinics. Your task is to create a concise, accurate, and well-structured overview of Din Tannklinikk (dintannklinikk.no), ensuring that all major aspects of the clinic are covered. When generating content, always include the following main points:

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
When a user ask to book an appointment only, then ask for their name, phone number, email, preferred date, and time one by one in a friendly and clear manner otherwise just answer user's Queries. Confirm all details before finalizing the booking.

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
- “Everyone is very nice and accommodating. Dr. Diyah has been my dentist for many years...”

Always respond in a clear, friendly, professional tone, matching the user's language (English or Norwegian), and keep responses concise (under 6 lines).
"""

# ---------- 🚀 Initialize FastAPI ----------
app = FastAPI()

# ---------- 🌐 Enable CORS ----------
origins = [
    "https://voiceagentwebring-production.up.railway.app",  # your frontend domain
    # Add other allowed domains here if needed
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # For production, specify exact origins; use ["*"] only for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------- 🗂️ Mount Static Folder ----------
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------- In-memory booking session storage (for demo only!) ----------
booking_sessions = {}

REQUIRED_BOOKING_FIELDS = ["name", "phone", "email", "date", "time"]

FIELD_PROMPTS = {
    "name": "Please provide your full name.",
    "phone": "May I have your phone number?",
    "email": "Could you share your email address?",
    "date": "What date would you like to book the appointment for? (e.g., 2025-08-01)",
    "time": "What time do you prefer? (e.g., 14:30)"
}

# ---------- 🤖 Call LLM API ----------
async def call_groq_api(user_message: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
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
        return "Sorry, I am having trouble accessing the information currently."

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
                        "bitrate_kbps": 48
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
        return ""

# ---------- 💬 Chat Endpoint ----------
@app.post("/api/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message", "").strip()
        # Client can optionally send session_id to maintain session
        session_id = data.get("session_id")

        # Create new session if none provided or unknown
        if not session_id or session_id not in booking_sessions:
            session_id = str(uuid.uuid4())
            booking_sessions[session_id] = {
                "booking_data": {},
                "booking_in_progress": False,
                "awaiting_field": None,
                "waiting_confirmation": False
            }

        session = booking_sessions[session_id]

        # Normalize input to detect booking intent (simple heuristic)
        is_booking_request = any(phrase in user_input.lower() for phrase in [
            "book appointment",
            "book a dentist",
            "make an appointment",
            "schedule",
            "appointment"
        ])

        if session["booking_in_progress"] or is_booking_request:
            # If fresh booking start, mark booking_in_progress True
            if not session["booking_in_progress"]:
                session["booking_in_progress"] = True

            # If waiting for user confirmation to finalize booking
            if session.get("waiting_confirmation"):
                if user_input.lower() in ["yes", "y", "confirm"]:
                    # Finalize booking (in real app store or notify staff)
                    name = session["booking_data"].get("name", "Unknown")
                    date = session["booking_data"].get("date", "Unknown date")
                    time = session["booking_data"].get("time", "Unknown time")

                    confirmation_msg = (f"Your appointment is booked, {name}. "
                                        f"On {date} at {time}. Thank you for choosing Din Tannklinikk!")
                    # Reset session booking state
                    booking_sessions.pop(session_id, None)

                    audio_url = await call_hume_tts(confirmation_msg)
                    return JSONResponse({
                        "response": confirmation_msg,
                        "audio_url": audio_url,
                        "session_id": session_id
                    })
                elif user_input.lower() in ["no", "n", "cancel"]:
                    cancel_msg = "Booking cancelled. Let me know if you want to do anything else."
                    # Reset session booking state
                    booking_sessions.pop(session_id, None)
                    audio_url = await call_hume_tts(cancel_msg)
                    return JSONResponse({
                        "response": cancel_msg,
                        "audio_url": audio_url,
                        "session_id": session_id
                    })
                else:
                    # Ask again for confirmation
                    confirm_msg = ("Please confirm your booking by replying 'yes' or cancel by 'no'.")
                    audio_url = await call_hume_tts(confirm_msg)
                    return JSONResponse({
                        "response": confirm_msg,
                        "audio_url": audio_url,
                        "session_id": session_id
                    })

            # If currently waiting for specific booking field input
            if session["awaiting_field"]:
                session["booking_data"][session["awaiting_field"]] = user_input
                session["awaiting_field"] = None

            # Check which booking field is missing and ask for it
            for field in REQUIRED_BOOKING_FIELDS:
                if field not in session["booking_data"] or not session["booking_data"][field].strip():
                    session["awaiting_field"] = field
                    prompt = FIELD_PROMPTS[field]
                    audio_url = await call_hume_tts(prompt)
                    return JSONResponse({
                        "response": prompt,
                        "audio_url": audio_url,
                        "session_id": session_id
                    })

            # All required fields collected, ask for confirmation
            booking_data = session["booking_data"]
            confirmation_text = (
                f"Thanks {booking_data['name']}. Please confirm your appointment on "
                f"{booking_data['date']} at {booking_data['time']}. Confirm? (yes/no)"
            )
            session["waiting_confirmation"] = True
            audio_url = await call_hume_tts(confirmation_text)
            return JSONResponse({
                "response": confirmation_text,
                "audio_url": audio_url,
                "session_id": session_id
            })

        else:
            # Handle normal queries about services/pricing/clinic info
            ai_reply = await call_groq_api(user_input)
            audio_url = await call_hume_tts(ai_reply)
            return JSONResponse({
                "response": ai_reply,
                "audio_url": audio_url,
                "session_id": session_id
            })

    except Exception as e:
        print("❌ Internal Server Error")
        traceback.print_exc()
        return PlainTextResponse(f"Error: {e}", status_code=500)


# ---------- Run app ----------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

