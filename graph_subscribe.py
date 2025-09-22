import requests
from auth import get_access_token

def create_subscription():
    access_token = get_access_token()
    url = "https://graph.microsoft.com/v1.0/subscriptions"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "changeType": "created",
        "notificationUrl": "https://ca-webhook.onrender.com/listen",  # Replace with your public HTTPS endpoint
        "resource": "me/messages",
        "expirationDateTime": "2025-09-25T23:00:00.000Z",
        "clientState": "secret123"
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Subscription response:", response.json())

if __name__ == "__main__":
    create_subscription()