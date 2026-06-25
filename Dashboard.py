import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt 
import seaborn as sns
import re

API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="GenAI Invoice Dashboard",
    layout="wide"
)


if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "landing"


def get_auth_headers():
    token = st.session_state.access_token

    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}"
    }


def logout():
    st.session_state.access_token = None
    st.session_state.user = None
    st.session_state.page = "landing"
    st.rerun()


def go_to_login():
    st.session_state.page = "login"
    st.rerun()


def go_to_register():
    st.session_state.page = "register"
    st.rerun()


def go_to_landing():
    st.session_state.page = "landing"
    st.rerun()


def api_register(email, username, password):
    response = requests.post(
        f"{API_BASE_URL}/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password
        },
        timeout=20
    )

    return response


def api_login(email, password):
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={
            "email": email,
            "password": password
        },
        timeout=20
    )

    return response

def del_my_invoice(Invoice_id):
    response=requests.delete(
        f"{API_BASE_URL}/invoices/del/{Invoice_id}",
        headers=get_auth_headers(),
        timeout=20
    )
    return response


def api_get_my_invoices():
    response = requests.get(
        f"{API_BASE_URL}/invoices/my-invoices",
        headers=get_auth_headers(),
        timeout=20
    )

    return response


def api_get_dashboard_summary():
    response = requests.get(
        f"{API_BASE_URL}/invoices/dashboard-summary",
        headers=get_auth_headers(),
        timeout=20
    )

    return response

def api_get_model_summary():
    response=requests.get(
        f"{API_BASE_URL}/invoices/models-summary",
        headers=get_auth_headers()
    )
    return response

def api_upload_invoice(uploaded_file):
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type
        )
    }

    response = requests.post(
        f"{API_BASE_URL}/invoices/upload-invoice",
        headers=get_auth_headers(),
        files=files,
        timeout=60
    )

    return response

def clean_label(value):
    if isinstance(value, tuple):
        return str(value[0])

    value = str(value)

    return (
        value
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
        .replace("'", "")
        .replace('"', "")
        .strip()
    )
def landing_page():
    st.title(":blue[Invoice] Dashboard for GenAI Usage")

    st.write(
        """
        Upload your GenAI invoice, track cost, monitor token consumption,
        and view analytics for your own account.
        """
    )

    st.divider()

    col1, col2, col3 = st.columns([1, 1, 1],border=True)

    with col1:
        st.header(":blue[Get your AI] Usage summary")

    with col2:
        if st.button("Log in", use_container_width=True):
            go_to_login()

        if st.button("Register", use_container_width=True):
            go_to_register()

    with col3:
        st.header(":blue[Register] to Get access to KPIs and AI Optimization")


def register_page():
    st.title(":blue[Create Account]")

    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Create Account", use_container_width=True):
            if not email or not password:
                st.warning("Email and password are required.")
                return

            try:
                response = api_register(email, username, password)

                if response.status_code == 200:
                    st.success("Account created successfully. Please login.")
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    try:
                        st.error(response.json().get("detail", "Registration failed."))
                    except Exception:
                        st.error(response.text)

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI backend. Make sure FastAPI is running.")

    with col2:
        if st.button("Back", use_container_width=True):
            go_to_landing()


def login_page():
    st.title(":blue[Log in]")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Log in", use_container_width=True):
            if not email or not password:
                st.warning("Email and password are required.")
                return

            try:
                response = api_login(email, password)

                if response.status_code == 200:
                    data = response.json()

                    st.session_state.access_token = data["access_token"]
                    st.session_state.user = data["user"]
                    st.session_state.page = "dashboard"

                    st.success("Login successful.")
                    st.rerun()

                else:
                    try:
                        st.error(response.json().get("detail", "Login failed."))
                    except Exception:
                        st.error(response.text)

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI backend. Make sure FastAPI is running.")

    with col2:
        if st.button("Back", use_container_width=True):
            go_to_landing()


def upload_invoice_widget():
    st.subheader("Upload Invoice")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel invoice",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        if st.button("Upload Invoice", use_container_width=True):
            try:
                response = api_upload_invoice(uploaded_file)

                if response.status_code == 200:
                    result = response.json()
                    st.success(result.get("message", "Invoice uploaded successfully."))
                    st.rerun()
                else:
                    try:
                        st.error(response.json().get("detail", "Upload failed."))
                    except Exception:
                        st.error(response.text)

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI backend.")


def dashboard_page():
    user_data = st.session_state.user

    col1, col2 = st.columns([4, 1])

    with col1:
        st.title(":blue[GenAI] Invoice Dashboard")
        st.caption(f"Logged in as {user_data['email']}")

    with col2:
        if st.button("Logout", use_container_width=True):
            logout()

    st.divider()

    invoices_response = api_get_my_invoices()

    if invoices_response.status_code == 401:
        st.error("Session expired or unauthorized. Please login again.")
        logout()
        return

    if invoices_response.status_code != 200:
        st.error(invoices_response.text)
        return

    invoices = invoices_response.json()

    # If no invoices exist for this user, prompt upload
    if not invoices:
        st.info("No invoice data found for this account. Upload your first invoice to continue.")
        upload_invoice_widget()
        return

    # If invoices exist, show upload option plus dashboard
    upload_invoice_widget()

    st.divider()

    summary_response = api_get_dashboard_summary()

    model_summary= api_get_model_summary()

    if summary_response.status_code == 401:
        st.error("Session expired or unauthorized. Please login again.")
        logout()
        return

    if summary_response.status_code != 200:
        st.error(summary_response.text)
        return

    summary = summary_response.json()
    summary_model= model_summary.json()

    st.subheader("Invoice Pay Cycle Summary")

    paycycle_start = summary.get("paycycle_start")
    paycycle_end = summary.get("paycycle_end")

    if paycycle_start and paycycle_end:
        paycycle = f"{paycycle_start} to \n {paycycle_end}"
    else:
        paycycle = "No date data"

    c1, c2, c3, c4 = st.tabs(["Invoice id","Pay cycle","Total cost","Total tokens"])

    with c1:
        t2,t3,t4=st.columns(3)
        with t2:
            st.metric("Cost for this invoice",f"${summary.get('total_cost_perinvoice',0):,.2f}")
        with t3:
            st.metric("Tokens used in this invoice",summary.get("total_tokens_perinvoice"))
        with t4:
            st.metric("Start date",summary.get("paycycle_start"))

        

    with c2:
        st.metric("Invoice Pay Cycle", paycycle)

    with c3:
        col1,col2=st.columns(2)
        with col1:
            st.metric("Invoice Count",summary.get("invoice_count"))
        with col2:
            st.metric("Total Cost for all invoices", f"${summary.get('total_cost', 0):,.2f}")

    with c4:
        cola,colb=st.columns(2)
        with cola:
            st.metric("Invoice Count",summary.get("invoice_count"))
        with colb:
            st.metric("Total Tokens for all invoices", f"{summary.get('total_tokens', 0):,}")

    st.divider()
    st.header("View Graphical Metrics")
    colab,colbc=st.columns(2)
    with colab:
        M1=pd.DataFrame(summary_model.get("models"))
        colrs=sns.color_palette("pastel")
        st.subheader("Model:blue[ Usage] Distribution" \
        "  :blue[Accross all Invoices]")
        fig2, donut=plt.subplots()
        freq1=M1.value_counts()
        donut.pie(freq1.values,labels=freq1.index,colors=colrs,autopct="%1.1f%%",wedgeprops={'width':0.7,'edgecolor':'w'})
        st.pyplot(fig2)
    with colbc:
        st.subheader(":blue[Other] Options")
        st.write("---")
        if st.button("View More Charts and Distributions for Specific invoices"):
            st.switch_page("pages/1 Key Insights.py")
        if st.button("Get AI consultation"):
            st.switch_page("pages/2 AI consultation.py")
        if st.button("Look at Quick saving tips"):
            st.switch_page("pages/3 Optimization tips.py")
        if st.button("Future forecasts"):
            st.switch_page("pages/4 Forecasts.py")
        st.write("---")
    
    st.write("delete invoices")
    invoices = api_get_my_invoices().json()
    invoice_options = {
        f"Invoice {item['file_name']}": item["id"]
        for item in invoices
        }
    selected_invoice = st.selectbox(
        "Choose invoice to delete",
        options= list(invoice_options.keys())
    )
    if selected_invoice != "All invoices":
        invoice_id1 = invoice_options[selected_invoice]
    if st.button("Delete Invoice Permanently"):
        del_my_invoice(invoice_id1)
        st.rerun()

    

    st.subheader("Past Invoices")


    invoice_df = pd.DataFrame(invoices)
    st.dataframe(invoice_df, column_config={"id":None,"file_hashid":None},use_container_width=True,hide_index=True)


if st.session_state.access_token:
    dashboard_page()

elif st.session_state.page == "login":
    login_page()

elif st.session_state.page == "register":
    register_page()


else:
    landing_page()
