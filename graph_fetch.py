# graph_fetch_user.py
import requests
import requests, base64, io
from auth import get_access_token
from analyzer import analyze_contract


def list_user_onedrive_files(access_token):
    url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json().get("value", [])

def get_file_stream(file_url):
    response = requests.get(file_url)
    return response.content

def get_file_download_url(access_token, item_id):
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to get file metadata:", response.text)
        return None
    metadata = response.json()
    return metadata.get("@microsoft.graph.downloadUrl")

def process_email(message_id):
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    msg = requests.get(f"https://graph.microsoft.com/v1.0/me/messages/{message_id}", headers=headers).json()

    if msg.get("hasAttachments"):
        attachments = requests.get(f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/attachments", headers=headers).json()
        for att in attachments["value"]:
            if att["name"].endswith(".pdf"):
                file_bytes = base64.b64decode(att["contentBytes"])
                file_stream = io.BytesIO(file_bytes)
                analyze_contract(file_stream, att["name"])
