import streamlit as st
import requests
import pandas as pd
import os 

API_BASE_URL = os.getenv("API_BASE_URL", "https://gen-ai-finops-dashboard.onrender.com")

a,b,c,d=st.columns(4)
with a:
    if st.button("Home",help="return to main dashboard",use_container_width=True):
        st.switch_page("Dashboard.py")
with b:
    if st.button("Key Insights",help="view important usage data",use_container_width=True):
        st.switch_page("pages/1 Key Insights.py")
with c:
    if st.button("AI consulting",help='redirect to ask AI',use_container_width=True):
        st.switch_page("pages/2 AI consultation.py")
with d:
    if st.button("Forecast",help="predict future usage",use_container_width=True):
        st.switch_page("pages/4 Forecasts.py")
st.title(":blue[Optimization] Tips")



if "access_token" not in st.session_state or not st.session_state.access_token:
    st.info("No user logged in, Please login first.")
    st.divider()
    if st.button("Log in now",icon_position="right",use_container_width=True):
        st.switch_page("Dashboard.py") and go_to_login()
    st.stop()


def get_auth_headers():
    return {
        "Authorization": f"Bearer {st.session_state.access_token}"
    }


def fetch_my_invoices():
    response = requests.get(
        f"{API_BASE_URL}/invoices/my-invoices",
        headers=get_auth_headers(),
        timeout=20
    )

    if response.status_code == 200:
        return response.json()

    st.error(response.text)
    return []


def reindex_invoices():
    response = requests.post(
        f"{API_BASE_URL}/invoices/reindex",
        headers=get_auth_headers(),
        timeout=60
    )

    return response


def ask_ai(question, invoice_id=None):
    response = requests.post(
        f"{API_BASE_URL}/ai/optimize",
        headers=get_auth_headers(),
        json={
            "question": question,
            "invoice_id": invoice_id
        },
        timeout=90
    )

    return response


invoices = fetch_my_invoices()

if not invoices:
    st.info("No invoices found. Please upload invoice data first.")
    st.stop()



invoice_options = {
    f"Invoice {item['id']} - {item['file_name']}": item["id"]
    for item in invoices
}

selected_invoice = st.selectbox(
    "Choose invoice context",
    options=["All invoices"] + list(invoice_options.keys())
)

invoice_id = None

if selected_invoice != "All invoices":
    invoice_id = invoice_options[selected_invoice]


question = f"{invoice_id} provide top 3 optimization points for this certain invoice, make them quick and short but explain briefly do not give too elaborate answers"

if st.button("Optimize Usage",use_container_width=True):
    with st.spinner("Analyzing invoice context..."):
        response = ask_ai(
            question=question,
            invoice_id=invoice_id
        )

    if response.status_code == 200:
        data = response.json()

        st.subheader(":blue[Optimization] Answer")
        st.write(data.get("answer", ""))


    else:
        st.error(response.text)