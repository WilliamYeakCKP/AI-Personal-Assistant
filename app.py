from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import time

app = Flask(__name__)
CORS(app)

# ✅ 改这里也可以当 trigger deploy（改一个字就会触发）
APP_VERSION = "v1.0.1"

API_KEY = os.environ.get("GEMINI_API_KEY")


@app.route("/")
def home():
    return f"✅ AI Assistant Backend is running! ({APP_VERSION})"


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")

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

    try:
        result = None

        # ✅ retry机制（最多5次）
        for attempt in range(5):
            response = requests.post(url, json=payload)

            # ✅ 成功直接跳出
            if response.status_code == 200:
                result = response.json()
                break

            # ✅ 503（服务器忙）
            elif response.status_code == 503:
                print(f"⚠️ Gemini busy, retrying... attempt {attempt + 1}")
                time.sleep(3)  # 等3秒再试

            else:
                # ✅ 其他错误直接记录
                print(f"❌ Error status: {response.status_code}")
                result = response.json()
                break

        
        # ✅ ✅ 👇 放在这里（重要！！！）
        if not result:
            return jsonify({"reply": "AI is currently busy, please try again shortly 😅"})

        # ✅ 安全解析（不会再炸）
        try:
            reply = result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            reply = str(result)

    except Exception as e:
        reply = f"Error: {str(e)}"

    return jsonify({"reply": reply})


# ✅ UI 页面（避免 CORS）
@app.route("/ui")
def serve_ui():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)