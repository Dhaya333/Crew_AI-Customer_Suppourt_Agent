"""
Refer Google_Config.md for instructions on how to set up a Google Form and link it to a Google Sheet.

Reads pending (not-yet-emailed) responses from a Google Form's linked
Google Sheet and returns them as CrewAI-ready `inputs` dicts. Also
writes "sent" back into the sheet's Mail_Status column once an email
goes out.

"""

import os
import gspread
from google.oauth2.service_account import Credentials

# Needs write access now (not just read) so we can mark rows as sent.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")

# Map your Google Form's actual column headers (left) to the keys
# CrewAI expects (right). Edit the left-hand strings to match your form.
COLUMN_MAP = {
    "Category": "category",
    "Name": "name",
    "Inquiry": "inquiry",
}

# Edit these two to match your sheet's actual header text exactly.
EMAIL_COLUMN = "Registered Email_ID"
MAIL_STATUS_COLUMN = "Mail_Status"


def _get_sheet():
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        raise ValueError("GOOGLE_SHEET_ID is not set in .env")

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id).sheet1


def get_pending_form_responses() -> list[dict]:
    """Returns every row whose Mail_Status isn't 'sent' yet, each as an
    inputs dict (category/name/inquiry/reply_to_email) plus the row's
    actual sheet row number (needed later to mark it as sent)."""
    sheet = _get_sheet()
    records = sheet.get_all_records()  # list of dicts, keyed by header row

    pending = []
    for i, record in enumerate(records):
        row_number = i + 2  # +1 for the header row, +1 for 1-based indexing
        status = str(record.get(MAIL_STATUS_COLUMN, "")).strip().lower()
        if status == "sent":
            continue

        inputs = {crew_key: record.get(sheet_col, "") for sheet_col, crew_key in COLUMN_MAP.items()}
        inputs["reply_to_email"] = record.get(EMAIL_COLUMN, "")
        inputs["_row_number"] = row_number
        pending.append(inputs)

    return pending


def mark_response_as_sent(row_number: int) -> None:
    """Writes 'sent' into the Mail_status column for the given sheet row."""
    sheet = _get_sheet()
    header = sheet.row_values(1)
    if MAIL_STATUS_COLUMN not in header:
        raise ValueError(f"Column '{MAIL_STATUS_COLUMN}' not found in sheet headers: {header}")
    status_col_index = header.index(MAIL_STATUS_COLUMN) + 1  # gspread columns are 1-based
    sheet.update_cell(row_number, status_col_index, "sent")


if __name__ == "__main__":
    # Quick manual test: python -m customer_support.google_form_reader
    from dotenv import load_dotenv
    load_dotenv()
    print(get_pending_form_responses())