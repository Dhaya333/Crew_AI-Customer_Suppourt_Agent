"""
Lightweight Streamlit UI for the Customer Support Agent.

Run with:
    streamlit run streamlit_app.py

Requires the FastAPI server to be running separately:
    uvicorn api:app --reload --port 8000
"""

import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Customer Support Agent", page_icon="🎧")
st.title("Customer Support Agent (Mail)")
st.caption("Developed by Udhaya A")

tab_manual, tab_form = st.tabs(["Ask manually", "Process pending Google Form responses"])

with tab_manual:
    with st.form("support_form"):
        category = st.selectbox(
            "Category",
            ["Need support in code", "Feedback", "Report a Bug", "Installation"],
        )
        name = st.text_input("Your name", placeholder="Jane Doe")
        inquiry = st.text_area("What do you need help with?", height=150)
        submitted = st.form_submit_button("Submit")

    if submitted:
        if not name or not inquiry:
            st.error("Please fill in your name and the inquiry field.")
        else:
            with st.spinner("Agents are working on your request..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/support-request",
                        json={"category": category, "name": name, "inquiry": inquiry},
                        timeout=300,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                except requests.exceptions.ConnectionError:
                    st.error(
                        "Could not reach the API. Is it running? "
                        "Start it with: uvicorn api:app --reload --port 8000"
                    )
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
                else:
                    st.success("Done!")
                    st.markdown("### Response")
                    st.write(data["response"])

with tab_form:
    st.write(
        "Processes every not-yet-sent submission in your linked Google "
        "Sheet, one after another with a short delay between each, and "
        "emails each answer to the address given in that response. Rows "
        "already marked 'sent' are skipped."
    )
    if st.button("Process pending form responses"):
        with st.spinner("Reading pending form responses and running the agents..."):
            try:
                resp = requests.post(f"{API_BASE}/process-pending-form-responses", timeout=600)
                resp.raise_for_status()
                data = resp.json()
            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not reach the API. Is it running? "
                    "Start it with: uvicorn api:app --reload --port 8000"
                )
            except Exception as e:
                st.error(f"Something went wrong: {e}")
            else:
                if data["processed"] == 0:
                    st.info("No pending responses — everything is already marked 'sent'.")
                else:
                    st.success(f"Processed {data['processed']} response(s).")
                    for item in data["results"]:
                        status = "✅ Emailed" if item["emailed"] else "⚠️ Email failed"
                        st.write(f"**{item['name']}** — {item['category']} — {status}")