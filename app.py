from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import time
import random  # ✅ 新增

app = Flask(__name__)
CORS(app)

APP_VERSION = "v1.0.3"  # ✅ 改版本触发 deploy

API_KEY = os.environ.get("GEMINI_API_KEY")


@app.route("/")
def home():
    return f"✅ AI Assistant Backend is running! ({APP_VERSION})"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    # ✅ 防止 None（更稳）
    user_message = data.get("message", "Tell me something interesting")

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-3.5-flash:generateContent?key={API_KEY}"

    # ✅ ✅ ✅ 核心：加入随机 + prompt强化
    payload = {
        "contents": [
            {
                "parts": [{
                    "text": f"{user_message}. Give a different answer each time and avoid repeating. #{random.randint(1,10000)}"
                }]
            }
        ],
        "generationConfig": {
            "temperature": 0.9,
            "topP": 0.9
        }
    }

    try:
        result = None

        # ✅ retry（建议用3次）
        for attempt in range(3):
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()
                break

            elif response.status_code == 503:
                print(f"⚠️ Gemini busy, retrying... attempt {attempt + 1}")
                time.sleep(2)

            elif response.status_code == 429:
                return jsonify({
                    "reply": "AI is busy (limit reached), try again later 🚦"
                })

            else:
                print(f"❌ Error status: {response.status_code}")
                result = response.json()
                break

        # ✅ fallback
        if not result:
            return jsonify({"reply": "AI is currently busy, please try again shortly 😅"})

        # ✅ 安全解析
        try:
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            reply = str(result)

    except Exception as e:
        reply = f"Error: {str(e)}"

    return jsonify({"reply": reply})


@app.route("/ui")
def serve_ui():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)