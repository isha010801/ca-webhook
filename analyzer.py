import os
import re
import json
from datetime import datetime, timedelta
import dateparser
from openai import AzureOpenAI
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from db import insert_contract, insert_clause
from notify import send_email_notification
from cd import create_calendar_event

load_dotenv()

# Setup Form Recognizer
form_client = DocumentAnalysisClient(
    endpoint=os.getenv("AZURE_FORM_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_FORM_KEY"))
)

# Setup OpenAI
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2023-07-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def analyze_contract(file_stream, file_name="UploadedContract.pdf", access_token=None):
    try:
        # Step 1: Extract text using Form Recognizer
        poller = form_client.begin_analyze_document("prebuilt-document", document=file_stream)
        result = poller.result()
        contract_text = "\n".join([p.content for p in result.paragraphs])

        # Step 2: GPT prompt
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
        match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if not match:
            raise ValueError(f"No valid JSON found in GPT output:\n{raw_output}")

        data = json.loads(match.group(0))

        # Step 3: Insert into DB
        contract_id = insert_contract(
            file_name,
            data.get("summary", ""),
            data.get("important_dates", {}).get("renewal", ""),
            data.get("important_dates", {}).get("termination", ""),
            "Medium"
        )

        for clause_type, text in data.get("key_clauses", {}).items():
            insert_clause(contract_id, clause_type, text)

        # Step 4: Risk logic
        risky_terms = data.get("risky_terms", [])
        termination_clause = data.get("key_clauses", {}).get("termination", "")
        renewal_date = data.get("important_dates", {}).get("renewal", "")
        termination_date = data.get("important_dates", {}).get("termination", "")

        should_notify = False
        today = datetime.today()

        term_dt = dateparser.parse(termination_date) if termination_date else None
        renew_dt = dateparser.parse(renewal_date) if renewal_date else None

        if len(risky_terms) > 2 or (termination_clause and termination_clause.strip()):
            should_notify = True
        if term_dt and (term_dt - today <= timedelta(days=30)):
            should_notify = True
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

        if should_notify and access_token:
            print("Triggering notification based on risk logic.")
            send_email_notification(access_token, os.getenv("USER_EMAIL"), data)
        else:
            print("No notification needed — contract looks safe.")

    except Exception as e:
        print("Analysis failed:", e)