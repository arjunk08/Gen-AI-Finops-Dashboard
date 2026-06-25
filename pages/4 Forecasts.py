import streamlit as st 
import pandas as pd 
import requests
import numpy as np

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config("Forecast")

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
    if st.button("Optimize Usage",help="Redirect to Optimization tips",use_container_width=True):
        st.switch_page("pages/3 Optimization tips.py")

st.title(":blue[Future] Cost and Token Usage Forecast")

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "user" not in st.session_state:
    st.session_state.user = None

def go_to_login():
    st.session_state.page = "login"
    st.rerun()

def get_auth_headers():
    token = st.session_state.access_token

    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}"
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


def api_extract_from_database(invoice_number):
    response=requests.get(
        f"{API_BASE_URL}/invoices/{invoice_number}",
        headers=get_auth_headers(), 
        timeout=40
        )
    return response
    


    

if st.session_state.user==None and st.session_state.access_token==None:
    st.divider()
    st.info("No User logged in,Please log in first")
    st.divider()
    if st.button("Log in now",icon_position="right"):
        st.switch_page("Dashboard.py") and go_to_login()
else:

    invoices=fetch_my_invoices()
    invoice_options = {
    f"Invoice {item['id']} - {item['file_name']}": item["id"]
    for item in invoices
    }
    selected_invoice = st.selectbox(
    "Select Invoice",
    options=list(invoice_options.keys())
    )
    invoice_id = invoice_options[selected_invoice]
    df=api_extract_from_database(invoice_id).json()
    invoice_data=df["rows"]
    df1=pd.DataFrame(invoice_data)
    col1,col2=st.columns(2)
    with col1:
        if st.button("Forecast Costs",use_container_width=True):
            avg=sum(df1["amount_usd"])/len(df1["amount_usd"])
            st.info("TO BE ADDED IN FUTURE UPDATES")
    with col2:
        if st.button("Forecast Token Usage",use_container_width=True):
            st.info("TO BE ADDED IN FUTURE UPDATES")

    

