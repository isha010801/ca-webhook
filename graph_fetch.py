# graph_fetch_user.py
import requests

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
