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
st.title("🎧 Customer Support Agent")
st.caption("Powered by CrewAI + Gemini")

tab_manual, tab_form = st.tabs(["Ask manually", "Process latest Google Form response"])

with tab_manual:
    with st.form("support_form"):
        category = st.text_input("Category", placeholder="e.g., Report a bug")
        name = st.text_input("Your name", placeholder="Jane Doe")
        inquiry = st.text_area("What do you need help with?", height=150)
        submitted = st.form_submit_button("Submit")

    if submitted:
        if not category or not name or not inquiry:
            st.error("Please fill in Category, Your name, and the Inquiry field.")
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
        "Pulls the newest submission from your linked Google Sheet and "
        "emails the answer straight back to the email address given in "
        "that response — no manual entry needed."
    )
    if st.button("Process latest form response"):
        with st.spinner("Reading the latest form response and running the agents..."):
            try:
                resp = requests.post(f"{API_BASE}/process-latest-form-response", timeout=300)
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
                if data["emailed"]:
                    st.info("Emailed to the address from the form response.")
                else:
                    st.warning(
                        "Response generated, but the email send failed — "
                        "check your Gmail app password setup and the form's "
                        "email column."
                    )