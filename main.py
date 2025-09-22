import os
import re
import json
from openai import AzureOpenAI
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from db import init_db, insert_contract, insert_clause
from auth import get_access_token
from graph_fetch import list_user_onedrive_files, get_file_stream, get_file_download_url
from notify import send_email_notification
from cd import create_calendar_event


# --- Load env + init DB ---
load_dotenv()
init_db()

# --- Form Recognizer Setup ---
form_client = DocumentAnalysisClient(
    endpoint=os.getenv("AZURE_FORM_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_FORM_KEY"))
)

# --- OpenAI Setup ---
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2023-07-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Step 1: Parse contract with Document Intelligence
# with open("sample_contract.pdf", "rb") as f:
#     poller = form_client.begin_analyze_document("prebuilt-document", document=f)
#     result = poller.result()
access_token = get_access_token()
files = list_user_onedrive_files(access_token)
if not files:
    print("No files found in OneDrive.")
    exit()

# Pick the first file for now
valid_files = [f for f in files if "file" in f and f["name"].endswith(".pdf")]

if not valid_files:
    print("No valid PDF files found in OneDrive.")
    exit()

file = valid_files[0]
item_id = file["id"]
file_name = file["name"]
file_url = get_file_download_url(access_token, item_id)

if not file_url:
    print(f"Could not retrieve download URL for '{file_name}'")
    exit()

file_stream = get_file_stream(file_url)


file_stream = get_file_stream(file_url)

poller = form_client.begin_analyze_document("prebuilt-document", document=file_stream)
result = poller.result()

contract_text = "\n".join([p.content for p in result.paragraphs])


# Step 2: GPT Prompt (force JSON only)
prompt = f"""
Analyze this contract and return ONLY valid JSON in the format below, no extra text:

{{
  "summary": "",
  "key_clauses": {{
    "termination": "",
    "liability": "",
    "payment_terms": "",
    "renewal": ""
  }},
  "risky_terms": [],
  "important_dates": {{
    "renewal": "",
    "termination": ""
  }}
}}

Contract Text: {contract_text}
"""

response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    messages=[
        {"role": "system", "content": "You are a legal contract analysis assistant."},
        {"role": "user", "content": prompt}
    ]
)

raw_output = response.choices[0].message.content.strip()
print(raw_output)

# Extract only JSON (in case GPT adds extra text)
match = re.search(r"\{.*\}", raw_output, re.DOTALL)
if not match:
    raise ValueError(f"No valid JSON found in GPT output:\n{raw_output}")

json_str = match.group(0)
data = json.loads(json_str)

# Step 3: Insert into DB
contract_id = insert_contract(
    "SampleContract.pdf",
    data.get("summary", ""),
    data.get("important_dates", {}).get("renewal", ""),
    data.get("important_dates", {}).get("termination", ""),
    "Medium"  # You can refine risk level calculation
)

# Insert clauses
for clause_type, text in data.get("key_clauses", {}).items():
    insert_clause(contract_id, clause_type, text)

# Insert risky terms (requires db.py update)
# Add this function in db.py:
# def insert_risky_term(contract_id, text):
#     ...
if "risky_terms" in data:
    for term in data["risky_terms"]:
        print(f"Risky term: {term}")
        # insert_risky_term(contract_id, term)  # Uncomment after adding to db.py

risky_terms = data.get("risky_terms", [])
termination_clause = data.get("key_clauses", {}).get("termination", "")
renewal_date = data.get("important_dates", {}).get("renewal", "")
termination_date = data.get("important_dates", {}).get("termination", "")

should_notify = False

# Trigger notification if:
# - More than 2 risky terms
# - Termination clause is present
# - Termination or renewal date is within 30 days
from datetime import datetime, timedelta
import dateparser


try:
    today = datetime.today()
    if len(risky_terms) > 2:
        should_notify = True
    if termination_clause and len(termination_clause.strip()) > 0:
        should_notify = True
    if termination_date:
        term_dt = dateparser.parse(termination_date)
        if term_dt and (term_dt - today <= timedelta(days=30)):
            should_notify = True

    if renewal_date:
        renew_dt = dateparser.parse(renewal_date)
        if renew_dt and (renew_dt - today <= timedelta(days=30)):
            should_notify = True
    if term_dt:
        create_calendar_event(access_token, "Contract Termination Reminder", term_dt.strftime("%Y-%m-%d"))
    else:
        print("No valid termination date to create calendar event.")

    if renew_dt:
        create_calendar_event(access_token, "Contract Renewal Reminder", renew_dt.strftime("%Y-%m-%d"))
    else:
        print("No valid renewal date to create calendar event.")

except Exception as e:
    print("Date parsing error:", e)

# Send notification if needed
if should_notify:
    print("Triggering notification based on risk logic.")
    send_email_notification(access_token, os.getenv("USER_EMAIL"), data)
else:
    print("No notification needed — contract looks safe.")
