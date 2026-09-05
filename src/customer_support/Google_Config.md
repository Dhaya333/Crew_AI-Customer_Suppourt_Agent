### Google sheet configuration :

Reads the most recent response from a Google Form's linked Google Sheet
and returns it as a CrewAI-ready `inputs` dict.
 
Setup required (one-time):
1. Google Cloud Console -> create a project -> enable "Google Sheets API".
2. Create a Service Account -> create a JSON key -> download it as
   service_account.json and place it in this project's root folder
   (make sure it's in .gitignore, never commit it).
3. Open your Google Form's linked response Sheet -> click Share ->
   paste the service account's "client_email" (found inside the JSON)
   -> give it Viewer access.
4. Set GOOGLE_SHEET_ID in .env (the long ID in the sheet's URL, between
   /d/ and /edit).
5. In response tab, click on "Link to new sheet"
 
Expected sheet columns (adjust COLUMN_MAP below to match your form's
actual question titles, which become the header row automatically, it is case sensitive so ensure the correct spelling without any addtional space in it):
| Timestamp (Auto-generated) | Customer | Person | Inquiry | Email Address

### Gmail SMTP configuration :

   Sends emails via Gmail SMTP using an App Password (not your real password).

Setup:
1. Enable 2-Step Verification on your Google account.
2. Verify Mobile number and Email address
3. Click *Manage Google Account* -> Security -> App Passwords (Search) -> generate one for "Mail".
4. Put the 16-character password in .env as GMAIL_APP_PASSWORD, and your
   Gmail address as GMAIL_ADDRESS.