import pandas as pd 
import streamlit as st 
from fastapi import FastAPI
import requests
import matplotlib.pyplot as plt 
import seaborn as sns

API_BASE_URL = "http://127.0.0.1:8000"

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

if st.session_state.user==None and st.session_state.access_token==None:
    a,b,c,d=st.columns(4)
    with a:
        if st.button("Home",help="return to main dashboard",use_container_width=True):
            st.switch_page("Dashboard.py")
    with b:
        if st.button("AI consulting",help="redirect to ask AI",use_container_width=True):
            st.switch_page("pages/2 AI consultation.py")
    with c:
        if st.button("Optimization",help='Optimize your genAI Usage',use_container_width=True):
            st.switch_page("pages/3 Optimization tips.py")
    with d:
        if st.button("Forecast",help="predict future usage",use_container_width=True):
            st.switch_page("pages/4 Forecasts.py")
    
    st.title(":blue[Key] Performance Indicators")
    st.info("No user logged in")
    st.divider()
    if st.button("Log in now",icon_position="right",use_container_width=True):
        st.switch_page("Dashboard.py") and go_to_login()

else:
    def api_extract_from_database(invoice_number):
        response=requests.get(
            f"{API_BASE_URL}/invoices/{invoice_number}",
            headers=get_auth_headers(), 
            timeout=40
            )
        return response
    
    
    def api_get_dashboard_summary():
        response = requests.get(
            f"{API_BASE_URL}/invoices/dashboard-summary",
            headers=get_auth_headers(),
            timeout=20
            )
        return response
    
    
    def fetch_my_invoices():
        response = requests.get(
            f"{API_BASE_URL}/invoices/my-invoices",
            headers=get_auth_headers(),
            timeout=20
            )
        return response
    
    
    invoice_response = fetch_my_invoices()

    if invoice_response.status_code != 200:
        st.error(invoice_response.text)
        st.stop()

    invoices = invoice_response.json()
    invoice_options = {
        f"Invoice {item['id']} - {item['file_name']}": item["id"]
        for item in invoices
        }


    a,b,c,d=st.columns(4)
    with a:
        if st.button("Home",help="return to main dashboard",use_container_width=True):
            st.switch_page("Dashboard.py")
    with b:
        if st.button("AI consulting",help="redirect to ask AI",use_container_width=True):
            st.switch_page("pages/2 AI consultation.py")
    with c:
        if st.button("Optimization",help='Optimize your genAI Usage',use_container_width=True):
            st.switch_page("pages/3 Optimization tips.py")
    with d:
        if st.button("Forecast",help="predict future usage",use_container_width=True):
            st.switch_page("pages/4 Forecasts.py")
         
    st.title("Select :blue[Invoice to View] Key Performance Indicators")
    summary=api_get_dashboard_summary().json()
    ab,bb=st.columns([1,2],border=True)
    with ab:
        id=st.selectbox("",invoice_options.keys(),placeholder="select invoice number")
        st.write("---")
        selected_invoice_id = invoice_options[id]
        KPI=st.button("Get KPIs",use_container_width=True,key="KPI")
    datadf=api_extract_from_database(selected_invoice_id).json()
    with bb:
        if datadf is not None:
            if KPI:
                try:
                    invoice_rows1=datadf["rows"]
                    df1=pd.DataFrame(invoice_rows1)
                    c1, c2, c3, = st.tabs(["Cost","Tokens","Department"])
                    if "Model" in df1.columns and "amount_usd" in df1.columns:
                        model_cost_df = (
                            df1.groupby("Model", dropna=False)["amount_usd"]
                            .sum()
                            .reset_index()
                            .sort_values("amount_usd", ascending=False)
                            )
                        weekly_cost_df=(df1.groupby("billing_date")["amount_usd"].sum().reset_index())
                    
                        with c1:
                            st.subheader("Cost per Model")
                            st.bar_chart(model_cost_df, x="Model", y="amount_usd",y_label="Amount per Model")
                            st.write("---")
                            st.subheader("Cost on billing days")
                            st.bar_chart(weekly_cost_df,x="billing_date",y="amount_usd")
                            st.dataframe(df1)
                    token_model_df=(df1.groupby("Model",dropna=False)["total_tokens"].sum().reset_index())
        
                    with c2:
                        st.subheader("Tokens used per model")
                        st.bar_chart(token_model_df,x="Model",y="total_tokens",y_label="Tokens Per Model")
                    with c3:
                        st.subheader("Department Cost")
                        if "business_unit" or "team" or "application" is not None:
                            appdf=(df1.groupby("business_unit" or "team" or "application")["amount_usd"].sum().reset_index())
                            st.bar_chart(appdf)                
                
                except Exception as e:
                    st.info(f"Select Invoice ID Using the Dropdown menu,{e}")
    
        
