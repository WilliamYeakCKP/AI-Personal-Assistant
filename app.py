from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("GEMINI_API_KEY")


@app.route("/")
def home():
    return "✅ AI Assistant Backend is running!"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")

    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-3.5-flash:generateContent?key={API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [{"text": user_message}]
                }
            ],
            "generationConfig": {
                "temperature": 0.8,
                "topP": 0.9
            }
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


# ✅ 提供网页 UI（不会再有 CORS 问题）
@app.route("/ui")
def serve_ui():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)