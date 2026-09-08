# Manual Testing Guide

Test each piece in isolation, in this order, before trusting the full
pipeline. Every command runs from the **project root**
(`D:\Customer Support Agent`), with the venv active, unless noted.

For Sheets/Gmail setup itself (service account, sharing permissions,
App Password), see `google_config.md` — this file assumes that setup
is already done and just verifies it works.

---

## 1. Crew works at all (Gemini connects, agents run)

**Where configured:** `.env` → `GEMINI_API_KEY`, `MODEL`

```powershell
python main.py
```

**Expect:** verbose agent output in the terminal, ending with a
`========== FINAL RESPONSE ==========` section containing a real
written answer.

**If it fails:** check `GEMINI_API_KEY` is set, and that `MODEL` in
`.env` is a currently-active Gemini model (deprecated model names
return a 404 — check Google's model list if unsure).

---

## 2. Google Sheet reading

**Where configured:** `.env` → `GOOGLE_SHEET_ID`,
`GOOGLE_SERVICE_ACCOUNT_FILE`; `service_account.json` in project root;
sheet shared with the service account's `client_email` (Editor access).

```powershell
$env:PYTHONPATH = "src"
python -m customer_support.google_form_reader
```

**Expect:** a printed Python list of dicts — one per row not yet
marked `"sent"` in the `Mail_status` column.

**If it fails:**
- `FileNotFoundError` on `service_account.json` → confirm it's in the
  project root, not `src/customer_support/`.
- Empty error after `SpreadsheetNotFound` → `GOOGLE_SHEET_ID` is wrong,
  or the sheet isn't shared with the service account's email.
- Empty list returned when you expect rows → check `COLUMN_MAP`,
  `EMAIL_COLUMN`, and `MAIL_STATUS_COLUMN` in `google_form_reader.py`
  match your sheet's actual header text exactly.

---

## 3. Gmail sending

**Where configured:** `.env` → `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`

Edit the test address inside `email_utils.py`'s `if __name__ == "__main__"`
block first, then:

```powershell
$env:PYTHONPATH = "src"
python -m customer_support.email_utils
```

**Expect:** `Email sent.` printed, and the test email actually arrives.

**If it fails:** confirm 2-Step Verification is on for the Gmail
account and you're using an App Password (16 characters, no spaces),
not your normal Gmail password.

---

## 4. Marking a sheet row as sent

**Where configured:** same as step 2, plus Editor (not just Viewer)
access on the sheet.

Quick one-off check from a Python shell:

```powershell
$env:PYTHONPATH = "src"
python
```
```python
from dotenv import load_dotenv; load_dotenv()
from customer_support.google_form_reader import mark_response_as_sent
mark_response_as_sent(2)   # row 2 = first data row after the header
```

**Expect:** no error. Refresh the Google Sheet in your browser — row
2's `Mail_status` column should now say `sent`.

**If it fails:** `ValueError` about the column not being found means
`MAIL_STATUS_COLUMN` in `google_form_reader.py` doesn't match your
sheet's header text. A permissions error means the sheet is still
shared as Viewer, not Editor.

---

## 5. API — single manual request

**Where configured:** nothing extra, just needs step 1 working.

```powershell
uvicorn api:app --reload --port 8000
```

Then open http://127.0.0.1:8000/docs, expand `POST /support-request`,
click "Try it out", and submit a body like:

```json
{
  "category": "Feedback",
  "name": "Test User",
  "inquiry": "Just checking this works.",
  "reply_to_email": ""
}
```

**Expect:** a 200 response with `"response"` containing the crew's
answer. Leave `reply_to_email` blank to skip the email step for this
check.

---

## 6. API — full pending-form-responses loop

**Where configured:** everything above must already work.

With uvicorn still running, in Swagger expand
`POST /process-pending-form-responses`, click "Try it out", then
Execute (no body needed).

**Expect:** a response like
`{"processed": 2, "results": [{"name": "...", "category": "...", "emailed": true}, ...]}`.
If you have more than one pending row, watch the uvicorn terminal —
there should be a ~5 second pause between each row's processing.

**Verify after:** refresh the Google Sheet — every processed row's
`Mail_status` should now say `sent`, and the emails should be in the
corresponding inboxes.

**If it fails:** check the uvicorn terminal for the full traceback —
the JSON error detail is often truncated. Most likely causes at this
stage are the same as step 2 or step 3, since this endpoint chains
both together.

---

## 7. Streamlit UI (end-to-end, both tabs)

**Where configured:** nothing extra — this just calls the API above.

With uvicorn still running, in a separate terminal:

```powershell
streamlit run streamlit_app.py
```

- **"Ask manually" tab** — fill in Category, Name, Inquiry, submit.
  Should show a response with no email involved.
- **"Process pending Google Form responses" tab** — click the button.
  Should show a per-row result list (name, category, sent/failed).

**If it fails:** "Could not reach the API" means uvicorn isn't running
or is on a different port than `API_BASE` in `streamlit_app.py`
(`http://localhost:8000` by default).