from flask import Flask, request, jsonify
from graph_fetch import process_email

app = Flask(__name__)

@app.route("/listen", methods=["POST", "GET"])
def listen():
    # Handle Graph validation handshake
    validation_token = request.args.get("validationToken")
    if validation_token:
        print("✅ Validation handshake received")
        return validation_token, 200, {'Content-Type': 'text/plain'}

    # Ensure request is JSON
    if request.is_json:
        data = request.get_json()
        print("📩 Notification received:", data)
        for event in data.get("value", []):
            message_id = event["resourceData"]["id"]
            print("🔍 Processing message ID:", message_id)
            process_email(message_id)
        return "", 202
    else:
        print("❌ Unsupported Media Type")
        return jsonify({"error": "Unsupported Media Type"}), 415

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)