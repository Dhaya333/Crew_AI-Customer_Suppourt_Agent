# Customer Support Agent (CrewAI + Gemini)

A two-agent CrewAI crew that resolves customer support inquiries:
1. **Senior Customer Support Representative** — drafts a full answer, using a
   website-scraping tool to ground the response in real docs.
2. **Support Quality Assurance Specialist** — reviews and polishes the draft
   before it's sent to the customer.

## Project Structure

```
customer_support_agent/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── main.py
└── src/
    └── customer_support/
        ├── crew.py
        ├── config/
        │   ├── agents.yaml
        │   └── tasks.yaml
        └── tools/
            └── custom_tools.py
```

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your Gemini API key:
   ```bash
   cp .env.example .env
   ```
   Get a key from [Google AI Studio](https://aistudio.google.com/app/apikey).

3. Run the crew:
   ```bash
   python main.py
   ```

## Customizing

- Edit `src/customer_support/config/agents.yaml` to change agent roles/goals.
- Edit `src/customer_support/config/tasks.yaml` to change task descriptions.
- Add tools in `src/customer_support/tools/custom_tools.py`.
- Change the model in `.env` via the `MODEL` variable (e.g.
  `gemini/gemini-1.5-pro` for a stronger model).
