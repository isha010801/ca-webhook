# auth.py
import os
from msal import PublicClientApplication
from dotenv import load_dotenv
load_dotenv()

def get_access_token():
    app = PublicClientApplication(
        client_id=os.getenv("AZURE_CLIENT_ID"),
        authority="https://login.microsoftonline.com/common"
    )
    result = app.acquire_token_interactive(scopes=["Mail.Read", "Mail.Send", "Calendars.ReadWrite", "Files.Read", "User.Read"])
    if "access_token" in result:
        return result["access_token"]
    else:
        print("Failed to acquire token:")
        print("Error:", result.get("error"))
        print("Description:", result.get("error_description"))
        raise Exception("Token acquisition failed")