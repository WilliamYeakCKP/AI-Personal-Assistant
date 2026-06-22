from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from google import genai

app = Flask(__name__)
CORS(app)

# ✅ 初始化新版 Gemini
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/")
def home():
    return "✅ AI Assistant Backend is running!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=user_message
        )

        reply = response.text

    except Exception as e:
        reply = f"Error: {str(e)}"

    return jsonify({"reply": reply})