"""
FastAPI wrapper around the CustomerSupportCrew.

Run with:
    uvicorn api:app --reload --port 8000

Then POST to http://localhost:8000/support-request
"""

import sys
import os

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from customer_support.crew import CustomerSupportCrew
from customer_support.email_utils import send_email
from customer_support.google_form_reader import get_latest_form_response

app = FastAPI(title="Customer Support Agent API")


class SupportRequest(BaseModel):
    customer: str
    person: str
    inquiry: str
    reply_to_email: str = ""      # if set, emails the result too


class SupportResponse(BaseModel):
    response: str
    emailed: bool


def _run_crew_and_email(customer: str, person: str, inquiry: str, reply_to_email: str) -> SupportResponse:
    inputs = {"customer": customer, "person": person, "inquiry": inquiry}

    try:
        result = CustomerSupportCrew().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crew execution failed: {e}")

    result_text = str(result)
    emailed = False

    if reply_to_email:
        try:
            send_email(
                to_email=reply_to_email,
                subject=f"Re: Your inquiry to {customer} support",
                body=result_text,
            )
            emailed = True
        except Exception as e:
            # Don't fail the whole request just because email sending failed —
            # the customer still gets the answer back in the API response.
            print(f"Email sending failed: {e}")

    return SupportResponse(response=result_text, emailed=emailed)


@app.post("/support-request", response_model=SupportResponse)
def handle_support_request(payload: SupportRequest):
    return _run_crew_and_email(
        payload.customer, payload.person, payload.inquiry, payload.reply_to_email
    )


@app.post("/process-latest-form-response", response_model=SupportResponse)
def process_latest_form_response():
    """Pulls the newest Google Form submission from the linked Sheet and
    automatically emails the result to the address given in that same
    response — no manual email entry needed anywhere."""
    try:
        form_inputs = get_latest_form_response()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read form response: {e}")

    return _run_crew_and_email(
        form_inputs["customer"],
        form_inputs["person"],
        form_inputs["inquiry"],
        form_inputs["reply_to_email"],
    )


@app.get("/health")
def health():
    return {"status": "ok"}