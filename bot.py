import os
import uuid
import traceback
from collections import defaultdict

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware



# ---------- 🔧 Configuration ----------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
HUME_API_KEY = os.getenv("HUME_API_KEY", "Xs2MM3Xx2Y13CRfLBiLNzsaY6niZrqRsoY5yEaVstPQmt0ZI")
LLAMA3_MODEL = "llama3-8b-8192"
VOICE_DESCRIPTION = "friendly, natural young assistant, warm, quick response, clear, enthusiastic"

SYSTEM_PROMPT = """
You are an expert Virtual Assistant for Dintannklinikk dental clinics. Your task is to create a concise, accurate, and well-structured overview of Din Tannklinikk (dintannklinikk.no), ensuring that all major aspects of the clinic are covered. When generating content, always include the following main points:
Always answer in 80 characters or less. Write clearly with no special formatting.
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

app = FastAPI()
app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

SERVICES = [
{"name": "Annual dental check-up (examination, x-rays, cleaning, hygiene)", "price": "from kr 1,400"},
{"name": "Cleaning, polishing, and hygiene", "price": "from kr 950"},
{"name": "Specialist examination/diagnostics", "price": "from kr 1,290"},
{"name": "Acute/general dentist examination", "price": "kr 770"},
{"name": "Consultation/comprehensive treatment plan", "price": "from kr 1,070"},
{"name": "Tooth-colored fillings (various surfaces)", "price": "from kr 1,150"},
{"name": "Crowns (metal-ceramic, all-ceramic)", "price": "from kr 7,950"},
{"name": "Dental prosthetics (full and partial dentures)", "price": "from kr 14,010"},
{"name": "Endodontics (root canal treatment)", "price": "kr 2,600 per hour"},
{"name": "Tooth extraction (simple/complicated)", "price": "from kr 1,350"},
{"name": "Surgical extraction", "price": "from kr 3,440"},
{"name": "Periodontal treatment (subgingival)", "price": "from kr 1,260"},
{"name": "Preventive treatment (hourly)", "price": "from kr 1,600"},
{"name": "Bleaching (single jaw)", "price": "kr 2,500"},
{"name": "Bleaching (upper/lower jaw)", "price": "kr 3,500"},
{"name": "X-ray per image", "price": "kr 160"},
{"name": "Panoramic x-ray", "price": "kr 820"},
{"name": "Local anesthesia", "price": "kr 210"},
{"name": "Hygiene supplement", "price": "kr 170"},
{"name": "Core build-up with titanium post", "price": "kr 3,140"},
{"name": "Surgical draping", "price": "kr 570"},
{"name": "Journal printout by mail", "price": "kr 150"},
]

SERVICE_NAMES = [s["name"].lower() for s in SERVICES]

sessions = defaultdict(dict) # session_id -> {'history': [...], 'booking': {...}}

def extract_price_values(price_str):
# Extracts price as int from strings like "from kr 1,400" or "kr 400"
import re
matches = re.findall(r'(\d{1,3}(?:[.,]\d{3})*[.,]?\d*)', price_str.replace(' ', ''))
if matches:
val = matches[0].replace('.', '').replace(',', '')
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

PRICE_QUESTIONS = ["price", "prices", "cost", "costs", "fee", "fees", "rate", "rates", "charge", "charges", "treatment cost", "pricelist"]

def find_service_in_text(user_input):
input_lower = user_input.lower()
for s in SERVICES:
base_name = s["name"].split("(")[0].strip().lower()
if base_name in input_lower:
return s
# Also check for key nouns from service ("cleaning", "crown", "root canal", etc)
words = base_name.replace('-', ' ').replace(',', '').split()
for w in words:
if w in input_lower and len(w) > 3:
return s
return None

# --- LLM CALL ---
async def call_groq_api(user_message: str) -> str:
try:
async with httpx.AsyncClient(timeout=7.0) as client:
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
{
"role": "user",
"content": (
f"{user_message}\nReply in 80 characters or less. No lists or formatting."
),
},
],
"temperature": 0.3,
"max_tokens": 240,
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
async with httpx.AsyncClient(timeout=60.0) as client:
response = await client.post(
"https://api.hume.ai/v0/tts/file",
headers={
"X-Hume-Api-Key": HUME_API_KEY,
"Content-Type": "application/json",
},
json={
"utterances": [{"text": text, "description": VOICE_DESCRIPTION}],
"format": {"type": "mp3", "bitrate_kbps": 48},
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

# Booking flow
if awaiting:
step = awaiting
value = user_input
if step == "name":
booking["name"] = value
booking["awaiting"] = "phone"
ai_reply = "What is your phone number?"
elif step == "phone":
booking["phone"] = value
booking["awaiting"] = "email"
ai_reply = "Your email address?"
elif step == "email":
booking["email"] = value
booking["awaiting"] = "date"
ai_reply = "Preferred date?"
elif step == "date":
booking["date"] = value
booking["awaiting"] = "time"
ai_reply = "Preferred time?"
elif step == "time":
booking["time"] = value
booking["awaiting"] = None
ai_reply = (
f"Booking: {booking['date']} {booking['time']}. You will get the confirmation email soon. Thanks for booking."
)
else:
ai_reply = "Booking error. Try again."
# --- NEW Price/Service Logic order ---
elif any(q in user_input.lower() for q in PRICE_QUESTIONS):
found = find_service_in_text(user_input)
if found:
ai_reply = f"{found['name']}: {found['price']}."
else:
minp, maxp = get_price_range()
if minp is not None and maxp is not None:
ai_reply = f"Prices range from krone 950 (9 hundred & 50 krones) to krone 14010 (14 thousand 10 krones)."
else:
ai_reply = "Please ask for a specific treatment price."
elif any(word in user_input.lower() for word in ["book", "appointment", "reserve time", "møte"]):
booking.clear()
booking["awaiting"] = "name"
ai_reply = "Your name?"
elif "service" in user_input.lower():
sample = SERVICES[:3]
s_list = ", ".join(s["name"] for s in sample)
ai_reply = f"We offer {s_list}, and more."
elif any(name in user_input.lower() for name in SERVICE_NAMES):
found = next((s for s in SERVICES if s["name"].lower() in user_input.lower()), None)
if found:
ai_reply = f"{found['name']}: {found['price']}."
else:
ai_reply = "Service not found."
else:
ai_reply = await call_groq_api(user_input)

history.append({"user": user_input, "bot": ai_reply})
audio_url = await call_hume_tts(ai_reply)

return JSONResponse(
{
"response": ai_reply,
"audio_url": audio_url,
"session_id": session_id,
}
)
except Exception as e:
print("Internal Server Error")
traceback.print_exc()
return PlainTextResponse(f"Error: {e}", status_code=500)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/", StaticFiles(directory=".", html=True), name="root")

if __name__ == "__main__":
import uvicorn

port = int(os.environ.get("PORT", 8080))
uvicorn.run("main:app", host="0.0.0.0", port=port)
