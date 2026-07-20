import streamlit as st
import requests
import os 


API_BASE_URL = os.getenv("API_BASE_URL", "https://gen-ai-finops-dashboard.onrender.com")

a,b,c,d=st.columns(4)
with a:
    if st.button("Home",help="return to main dashboard",use_container_width=True):
        st.switch_page("Dashboard.py")
with b:
    if st.button("Key Insights",help="View important usage data",use_container_width=True):
        st.switch_page("pages/1 Key Insights.py")
with c:
    if st.button("Optimization",help='Optimize your genAI Usage',use_container_width=True):
        st.switch_page("pages/3 Optimization tips.py")
with d:
    if st.button("Forecast",help="predict future usage",use_container_width=True):
        st.switch_page("pages/4 Forecasts.py")
st.title("AI:blue[ Consultation]")


if "access_token" not in st.session_state or not st.session_state.access_token:
    st.info("No user logged in, Please login first.")
    st.divider()
    if st.button("Log in now",icon_position="right",use_container_width=True):
        st.switch_page("Dashboard.py")
    st.stop()


def get_auth_headers():
    return {
        "Authorization": f"Bearer {st.session_state.access_token}"
    }

st.session_state.session_chat=None

def fetch_my_invoices():
    response = requests.get(
        f"{API_BASE_URL}/invoices/my-invoices",
        headers=get_auth_headers(),
        timeout=30
    )

    if response.status_code == 200:
        return response.json()

    st.error(response.text)
    return []


def reindex_invoices():
    response = requests.post(
        f"{API_BASE_URL}/invoices/reindex",
        headers=get_auth_headers(),
        timeout=90
    )

    return response

def rewrite(question, invoice_id=None):
    response = requests.post(
        f"{API_BASE_URL}/ai/rewrite",
        headers=get_auth_headers(),
        json={
            "question":question,
            "invoice_id":invoice_id

        },
        timeout=99
    )
    return response

def ask_ai(question, invoice_id=None):
    response = requests.post(
        f"{API_BASE_URL}/ai/consult/groq",
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


with st.expander("AI Search Setup"):
    st.write("If this is your first time using AI consultation, index your invoices into the vector store.")
    if st.button("Reindex my invoice data for AI"):
        response = requests.post(
            f"{API_BASE_URL}/invoices/reindex",
            headers=get_auth_headers(),
            timeout=60
            )
        if response.status_code == 200:
            st.success("Reindex completed.")
        else:
            st.error(response.text)

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


question = st.chat_input("Ask about your invoice, cost drivers, token usage, models, providers, or optimization")

if question:
    with st.spinner("Analyzing invoice context..."):
        response1 = rewrite(
            question=question,
            invoice_id=invoice_id
        )
        if response1.status_code == 200:
            new_query=response1.json()
            r1=new_query.get("new_query")
    response=ask_ai(
        question=f"{question}and context help is {r1}",
        invoice_id=invoice_id
    )
        

    if response.status_code == 200:
        data = response.json()

        st.subheader(":blue[AI] Answer")
        st.write(data.get("answer",""))


    else:
        st.error(response.text)