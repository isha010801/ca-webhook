import requests

def send_email_notification(access_token, user_email, contract_data):
    subject = f"Risk Alert: Contract Analysis for {contract_data.get('title', 'Unknown')}"
    body = f"""
Summary: {contract_data.get('summary', 'No summary available')}

Risky Terms: {', '.join(contract_data.get('risky_terms', [])) or 'None detected'}

Termination Date: {contract_data.get('important_dates', {}).get('termination', 'Not found')}
Renewal Date: {contract_data.get('important_dates', {}).get('renewal', 'Not found')}
"""

    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": [
                {"emailAddress": {"address": user_email}}
            ]
        },
        "saveToSentItems": "true"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://graph.microsoft.com/v1.0/me/sendMail",
        headers=headers,
        json=payload
    )

    if response.status_code == 202:
        print("Email sent successfully.")
    else:
        print("Failed to send email:", response.text)