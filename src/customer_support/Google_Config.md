# Google Configuration

This document contains the configuration steps required for integrating **Google Sheets** and **Gmail SMTP**.

---

## Google Sheets Configuration

Reads the most recent response from a Google Form's linked Google Sheet and returns it as a CrewAI-ready `inputs` dict.

### One-Time Setup

1. **Create and configure a Google Cloud project**
   - Open **Google Cloud Console**.
   - Create a project.
   - Enable the **Google Sheets API**.

2. **Create a Service Account**
   - Create a Service Account.
   - Create a JSON key.
   - Download it as `service_account.json`.
   - Place `service_account.json` in the project's root folder.
   - Add it to `.gitignore` and **never commit it to the repository**.

3. **Grant the Service Account access to the response Sheet**
   - Open the Google Form's linked response Sheet.
   - Click **Share**.
   - Paste the Service Account's `client_email` from the JSON credentials.
   - Grant **Viewer** access.

4. **Configure the Sheet ID**
   - Set `GOOGLE_SHEET_ID` in `.env`.
   - Use the long ID from the Sheet URL between `/d/` and `/edit`.

5. **Link the response tab**
   - In the response tab, click **Link to new sheet**.

### Expected Sheet Columns

Adjust `COLUMN_MAP` to match the actual question titles in your form.

> **Important:** The column names are generated automatically from the form's question titles and are **case-sensitive**. Ensure the spelling is exact and do not include additional spaces.

| Timestamp (Auto-generated) | Name | Category | Inquiry | Registered Email_ID |
|---|---|---|---|---|

---

## Gmail SMTP Configuration

Sends emails via **Gmail SMTP** using an **App Password** instead of the actual Gmail account password.

### Setup

1. **Enable 2-Step Verification**
   - Enable **2-Step Verification** on your Google account.

2. **Verify account details**
   - Verify your mobile number and email address.

3. **Generate a Gmail App Password**
   - Open **Manage Google Account**.
   - Go to **Security**.
   - Open **App Passwords** using the search option.
   - Generate an App Password for **Mail**.

4. **Configure environment variables**
   - Add the 16-character App Password to `.env` as `GMAIL_APP_PASSWORD`.
   - Add your Gmail address to `.env` as `GMAIL_ADDRESS`.

---

## Security Notes

- Keep `service_account.json` out of version control.
- Never commit Google service-account credentials to GitHub.
- Never use your actual Gmail password for SMTP authentication.
- Store credentials and secrets in `.env` and ensure `.env` is included in `.gitignore`.
