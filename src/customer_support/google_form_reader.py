"""Refer the Google_Console_Config.md file for instructions on 
how to set up a Google Form and link it to a Google Sheet. 
This script reads the latest response from the linked Google Sheet and maps it to 
the expected input format for CrewAI.
Make sure to set the following environment variables in your .env file"""

import os
import gspread
from google.oauth2.service_account import Credentials
 
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
 
# Map your Google Form's actual column headers (left) to the keys
# CrewAI expects (right). Edit the left-hand strings to match your form.
COLUMN_MAP = {
    "Category": "category",
    "Name": "name",
    "Inquiry": "inquiry"
}
 
# The form's email question — edit the left-hand string to match your
# form's actual column header (Google Forms' built-in email-collection
# question is usually titled "Email Address").
EMAIL_COLUMN = "Registered Email_ID"
 
 
def get_latest_form_response() -> dict:
    """Fetch the last row of the linked Google Sheet. Returns a dict
    with CrewAI's `inputs` keys (customer/person/inquiry) plus
    `reply_to_email` pulled straight from the form's email column."""
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        raise ValueError("GOOGLE_SHEET_ID is not set in .env")
 
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
 
    sheet = client.open_by_key(sheet_id).sheet1
    records = sheet.get_all_records()  # list of dicts, keyed by header row
 
    if not records:
        raise ValueError("No responses found in the sheet yet.")
 
    latest = records[-1]  # most recent submission
 
    inputs = {}
    for sheet_col, crew_key in COLUMN_MAP.items():
        inputs[crew_key] = latest.get(sheet_col, "")
 
    # Email comes straight from the form response — the user never types
    # it in manually anywhere else.
    inputs["reply_to_email"] = latest.get(EMAIL_COLUMN, "")
 
    return inputs
 
 
if __name__ == "__main__":
    # Quick manual test: python -m customer_support.google_form_reader
    from dotenv import load_dotenv
    load_dotenv()
    print(get_latest_form_response())
 