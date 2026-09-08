"""
FastAPI wrapper around the CustomerSupportCrew.

Run with:
    uvicorn api:app --reload --port 8000

Then POST to http://localhost:8000/support-request
"""

import sys
import os
import time

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from customer_support.crew import CustomerSupportCrew
from customer_support.email_utils import send_email
from customer_support.google_form_reader import (
    get_pending_form_responses,
    mark_response_as_sent,
)

app = FastAPI(title="Customer Support Agent API")

DELAY_BETWEEN_RESPONSES_SECONDS = 5


class SupportRequest(BaseModel):
    category: str
    name: str
    inquiry: str
    reply_to_email: str = ""      # if set, emails the result too


class SupportResponse(BaseModel):
    response: str
    emailed: bool


class PendingResult(BaseModel):
    name: str
    category: str
    emailed: bool


class PendingBatchResponse(BaseModel):
    processed: int
    results: list[PendingResult]


def _run_crew_and_email(category: str, name: str, inquiry: str, reply_to_email: str) -> SupportResponse:
    inputs = {"category": category, "name": name, "inquiry": inquiry}

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
                subject=f"Your {category} request",
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
        payload.category, payload.name, payload.inquiry, payload.reply_to_email
    )


@app.post("/process-pending-form-responses", response_model=PendingBatchResponse)
def process_pending_form_responses():
    """Pulls every not-yet-sent Google Form submission from the linked
    Sheet, runs the crew and emails each one in turn (5s delay between
    each), and marks each row's Mail_status as 'sent' once its email
    goes out."""
    try:
        pending = get_pending_form_responses()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read form responses: {e}")

    results = []
    for i, item in enumerate(pending):
        support_response = _run_crew_and_email(
            item["category"], item["name"], item["inquiry"], item["reply_to_email"]
        )

        if support_response.emailed:
            try:
                mark_response_as_sent(item["_row_number"])
            except Exception as e:
                # Email went out but we couldn't update the sheet — log it,
                # don't crash the whole batch over a status-write failure.
                print(f"Could not update Mail_status for row {item['_row_number']}: {e}")

        results.append(
            PendingResult(name=item["name"], category=item["category"], emailed=support_response.emailed)
        )

        if i < len(pending) - 1:
            time.sleep(DELAY_BETWEEN_RESPONSES_SECONDS)

    return PendingBatchResponse(processed=len(results), results=results)


@app.get("/health")
def health():
    return {"status": "ok"}