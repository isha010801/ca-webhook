# # list_onedrive_files_user.py
# import os
# import requests
# from msal import PublicClientApplication
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# def get_access_token():
#     app = PublicClientApplication(
#         client_id=os.getenv("AZURE_CLIENT_ID"),
#         authority="https://login.microsoftonline.com/common"
#     )
#     result = app.acquire_token_interactive(scopes=["Files.Read", "User.Read"])
#     if "access_token" in result:
#         return result["access_token"]
#     else:
#         print("Failed to acquire token:")
#         print("Error:", result.get("error"))
#         print("Description:", result.get("error_description"))
#         raise Exception("Token acquisition failed")

# def list_user_onedrive_files(access_token):
#     url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = requests.get(url, headers=headers)
#     if response.status_code != 200:
#         print("❌ Failed to list files:", response.text)
#         return []
#     return response.json().get("value", [])

# if __name__ == "__main__":
#     token = get_access_token()
#     files = list_user_onedrive_files(token)

#     if not files:
#         print("📂 No files found in your OneDrive.")
#     else:
#         print(f"📁 Found {len(files)} file(s):")
#         for f in files:
#             print(f" - {f['name']}")
