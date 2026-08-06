import os

import pandas as pd
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "https://gen-ai-finops-dashboard.onrender.com")
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

def predict_future_costs(df1):
    df1['billing_date'] = pd.to_datetime(df1['billing_date'])
    min_date = df1['billing_date'].min()
    max_date = df1['billing_date'].max()
    days_spanned = (max_date - min_date).days
    if days_spanned < 1:
        days_spanned = 1
    total_cost = df1['amount_usd'].sum()
    daily_burn_rate = total_cost / days_spanned
    return daily_burn_rate * 30

def predict_future_tokens(df1):
    df1['billing_date'] = pd.to_datetime(df1['billing_date'])
    min_date = df1['billing_date'].min()
    max_date = df1['billing_date'].max()
    days_spanned = (max_date - min_date).days
    if days_spanned < 1:
        days_spanned = 1
    total_tokens = df1['total_tokens'].sum()
    daily_burn_rate = total_tokens / days_spanned
    return daily_burn_rate * 30


    
    
if st.session_state.user is None and st.session_state.access_token is None:
    st.info("No User logged in,Please log in first")
    st.divider()
    if st.button("Log in now",icon_position="right",use_container_width=True):
        st.switch_page("Dashboard.py")
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
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Forecast Costs", use_container_width=True):
            proj_30 = predict_future_costs(df1)
            st.metric("Estimated 30-Day Cost", f"${proj_30:,.2f}")
            df1['billing_date'] = pd.to_datetime(df1['billing_date'])
            cost_trend = df1.groupby('billing_date')['amount_usd'].sum()
            st.line_chart(cost_trend)
           
    with col2:
        if st.button("Forecast Token Usage", use_container_width=True):
            proj_30_tokens = predict_future_tokens(df1)
            st.metric("Estimated 30-Day Tokens", f"{proj_30_tokens:,.0f}")
            df1['billing_date'] = pd.to_datetime(df1['billing_date'])
            token_trend = df1.groupby('billing_date')['total_tokens'].sum()
            st.line_chart(token_trend)

    

