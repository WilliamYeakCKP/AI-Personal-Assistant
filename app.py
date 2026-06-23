from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import time
import random

app = Flask(__name__)
CORS(app)

APP_VERSION = "v1.1.0"

API_KEY = os.environ.get("GEMINI_API_KEY")

# ✅ ✅ ✅ 简单 chat history（server memory）
chat_history = []


@app.route("/")
def home():
    return f"✅ AI Assistant Backend running ({APP_VERSION})"


@app.route("/chat", methods=["POST"])
def chat():
    global chat_history

    data = request.get_json()
    user_message = data.get("message", "Tell me something interesting")

    # ✅ 把用户输入加入历史
    chat_history.append({"role": "user", "text": user_message})

    # ✅ 限制历史长度（避免太长）
    if len(chat_history) > 6:
        chat_history = chat_history[-6:]

    # ✅ 把历史拼成 prompt
    history_text = ""
    for item in chat_history:
        role = "User" if item["role"] == "user" else "AI"
        history_text += f"{role}: {item['text']}\n"

    # ✅ 加随机避免重复
    history_text += f"Respond differently each time. #{random.randint(1,10000)}"

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-3.5-flash:generateContent?key={API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [{"text": history_text}]
            }
        ],
        "generationConfig": {
            "temperature": 0.9,
            "topP": 0.9
        }
    }

    try:
        result = None

        # ✅ retry机制（最多3次）
        for attempt in range(3):
            try:
                response = requests.post(url, json=payload, timeout=20)
            except requests.exceptions.Timeout:
                print(f"⏳ Timeout, retry {attempt + 1}")
                time.sleep(2)
                continue

            if response.status_code == 200:
                result = response.json()
                break

            elif response.status_code == 503:
                print(f"⚠️ Busy, retry {attempt + 1}")
                time.sleep(2)

            elif response.status_code == 429:
                return jsonify({
                    "reply": "AI busy (limit reached), try again later 🚦"
                })

            else:
                print(f"❌ Error {response.status_code}")
                result = response.json()
                break

        # ✅ fallback
        if not result:
            return jsonify({
                "reply": "AI temporarily unavailable, please try again 😅"
            })

        # ✅ 安全解析
        try:
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            reply = str(result)

        # ✅ 保存 AI 回复到历史
        chat_history.append({"role": "ai", "text": reply})

    except Exception as e:
        reply = f"Error: {str(e)}"

    return jsonify({"reply": reply})


@app.route("/ui")
def serve_ui():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)