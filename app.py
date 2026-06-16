from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ✅ 首页
@app.route("/")
def home():
    return "✅ AI Assistant Backend is running!"

# ✅ 聊天接口
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        return "Use POST to send a message"

    data = request.get_json(silent=True)
    user_message = data.get("message") if data else ""

    reply = f"AI reply: You said '{user_message}'"

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)