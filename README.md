# Customer Support Agent (CrewAI + Gemini)

An automated customer support pipeline: a Google Form collects inquiries,
a two-agent CrewAI crew (support rep + QA reviewer) drafts and polishes
a response using Gemini, and the answer is emailed back automatically.
A Streamlit UI and a FastAPI backend sit on top so it can be triggered
manually or by anything else.

## How it fits together

```
Google Form  →  Google Sheet  →  google_form_reader.py  →  CrewAI Crew  →  Gmail
                                          ↑                       ↑
                                     api.py (FastAPI)  ←  streamlit_app.py (UI)
```

- **Google Form / Sheet** — where inquiries come in. Each response is a row:
  Category, Name, Inquiry, Registered Email_ID, and a Mail_status column
  the code writes back to once it's handled.
- **`google_form_reader.py`** — reads rows where `Mail_status` isn't
  `"sent"` yet, and can write `"sent"` back once an email goes out.
- **`crew.py`** — defines the two agents (support rep, QA reviewer) and
  the sequential process between them, using Gemini as the LLM.
- **`api.py`** — FastAPI server. Exposes endpoints to run the crew on a
  single manual request, or to process every pending form row in a
  loop (5s delay between each) and email each result.
- **`streamlit_app.py`** — simple browser UI on top of the API: one tab
  for typing a question manually, one tab with a button to process all
  pending form responses.
- **`main.py`** — a standalone script with hardcoded sample inputs, used
  only to sanity-check the crew itself works, independent of the
  Sheets/API/UI pipeline.

## Project structure

```
customer_support_agent/
├── .env.example
├── .gitignore
├── README.md                 ← this file
├── TESTING.md                ← manual check commands, one per piece
├── google_config.md          ← Sheets + SMTP setup instructions
├── requirements.txt
├── main.py                   ← standalone crew test script
├── api.py                    ← FastAPI backend
├── streamlit_app.py          ← Streamlit UI
├── service_account.json      ← Google service account key (you add this, gitignored)
└── src/
    └── customer_support/
        ├── crew.py
        ├── google_form_reader.py
        ├── email_utils.py
        ├── config/
        │   ├── agents.yaml
        │   └── tasks.yaml
        └── tools/
            └── custom_tools.py
```

## Installation

1. **Python version**: use Python 3.13 (not 3.14 — some dependencies don't
   have prebuilt wheels for it yet).

2. Create and activate a virtual environment:
   ```powershell
   py -3.13 -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and fill in the values:
   ```powershell
   cp .env.example .env
   ```
   You'll need a Gemini API key (from
   [Google AI Studio](https://aistudio.google.com/app/apikey)) at minimum
   to run the crew at all. For the Sheets/Gmail pieces, follow
   **`google_config.md`** — it covers the Google Cloud service account,
   sharing the Sheet, and the Gmail App Password setup.

5. Place your Google service account key as `service_account.json` in
   this **project root** (same folder as `main.py`, not inside `src/`).

## Running it

Everything below is run from the project root, with the venv active.

**Refer the Testing.md file for each functions Manual check and setup**

**1. Sanity-check the crew works at all** (no Sheets/API needed):
```powershell
python main.py
```

**2. Start the API:**
```powershell
uvicorn api:app --reload --port 8000
```
Interactive docs: http://127.0.0.1:8000/docs

**3. Start the UI** (separate terminal, API must stay running):
```powershell
streamlit run streamlit_app.py
```

For step-by-step commands to test each individual piece on its own
(Sheets reading, email sending, the crew, each API endpoint) before
running the whole pipeline together, see **`TESTING.md`**.

## Notes

- `CREW_MEMORY_ENABLED` in `.env` is currently unused — memory is
  disabled in `crew.py` (`memory=False`) due to an embedder/env-var
  conflict with CrewAI's default Chroma setup. Revisit later if needed.
- The four supported inquiry categories are: `Need support in code`,
  `Feedback`, `Report a Bug`, `Installation`. These are baked into the
  task prompt in `config/tasks.yaml` — add more there if needed.
- Gemini model versions get deprecated over time — if you start getting
  404 errors on a previously-working model, check the current active
  models and update `MODEL` in `.env`.