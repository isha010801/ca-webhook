from flask import Flask, request
from graph_fetch import process_email
app = Flask(__name__)

@app.route("/listen", methods=["POST", "GET"])
def listen():
    # Handle Graph validation handshake
    validation_token = request.args.get("validationToken")
    if validation_token:
        return validation_token, 200, {'Content-Type': 'text/plain'}

    # Handle actual notifications
    data = request.json
    for event in data.get("value", []):
        message_id = event["resourceData"]["id"]
        process_email(message_id)
    return "", 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)