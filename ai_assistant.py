import os
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Read the secret key from the .env file
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-flash-latest"

# 2. A "Blueprint" = a separate part of the website (only for the AI)
ai_bp = Blueprint("ai", __name__)

# 3. Danger words -> we tell the owner to go to the clinic NOW
EMERGENCY_WORDS = [
    "poison", "seizure", "fit", "not breathing", "can't breathe",
    "bleeding a lot", "hit by", "accident", "collapsed", "unconscious",
    "can't pee", "cannot urinate", "swollen belly",
]

# 4. Instructions for the AI (prompt engineering)
SYSTEM_PROMPT = """
You are the Happy Pets Clinic AI Care Assistant in Sri Lanka.
You help pet owners with dogs and cats.

Rules:
- Give simple first-aid advice only. Never give a diagnosis.
- Never tell the owner to give human medicine.
- Use short, simple English.
- The FIRST line must be exactly one of these:
  URGENCY: Emergency
  URGENCY: Visit clinic soon
  URGENCY: Home care
- Then give 3 to 5 short tips.
- End with: "Please consult a veterinarian at Happy Pets Clinic."
"""

# 5. Show the chat page
@ai_bp.route("/ai-assistant")
@login_required
def ai_page():
    return render_template("ai_assistant.html")

# 6. Get the question, ask Gemini, send back the answer
@ai_bp.route("/ai-assistant/ask", methods=["POST"])
@login_required
def ask_ai():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify(error="Please type your pet's problem."), 400

    # Safety check first (works even if the AI is down)
    if any(word in message.lower() for word in EMERGENCY_WORDS):
        return jsonify(
            urgency="Emergency",
            reply="This sounds serious. Please come to Happy Pets Clinic "
                  "now or call 077 2303599.",
        )

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=message,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
        text = response.text or ""
        lines = text.strip().split("\n", 1)
        urgency = "Visit clinic soon"
        reply = text
        if lines[0].upper().startswith("URGENCY:"):
            urgency = lines[0].split(":", 1)[1].strip()
            reply = lines[1].strip() if len(lines) > 1 else ""
        return jsonify(urgency=urgency, reply=reply)

    except Exception as error:
        print("AI error:", error)
        return jsonify(error="The AI is not available now. Please try again "
                             "or call the clinic: 077 2303599."), 500
