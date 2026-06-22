from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route("/")
def home():
    return "✅ AI Assistant Backend is running!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")

    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": user_message}
                    ]
                }
            ]
        }

        response = requests.post(url, json=payload)
        result = response.json()

        try:
    reply = result["candidates"][0]["content"]["parts"][0]["text"]
except Exception:
    reply = str(result)

    except Exception as e:
        reply = f"Error: {str(e)}"

    return jsonify({"reply": reply})