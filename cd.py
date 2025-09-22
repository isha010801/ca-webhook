import requests

def create_calendar_event(access_token, title, date):
    payload = {
        "subject": title,
        "start": {
            "dateTime": date + "T09:00:00",
            "timeZone": "India Standard Time"
        },
        "end": {
            "dateTime": date + "T10:00:00",
            "timeZone": "India Standard Time"
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://graph.microsoft.com/v1.0/me/events",
        headers=headers,
        json=payload
    )

    if response.status_code == 201:
        print("📅 Calendar event created.")
    else:
        print("❌ Failed to create calendar event:", response.text)