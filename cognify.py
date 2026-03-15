import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
import json

st.set_page_config(page_title="Cognify Institute", layout="wide")

# --- CONNECTION FUNCTION ---
def connect_to_sheets():
    # Load credentials from Streamlit Secrets
    creds_dict = json.loads(st.secrets["gcp_service_account"])
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

# --- UI ---
st.title("COGNIFY INSTITUTE")
with st.form("class_report"):
    col1, col2 = st.columns(2)
    with col1:
        date_input = st.date_input("Date", date.today())
        teacher = st.text_input("Teacher Name")
    with col2:
        subject = st.text_input("Subject")
        class_name = st.text_input("Class")
    
    topic = st.text_area("Topic Covered")
    homework = st.text_input("Homework")
    
    # Simple attendance input
    student_name = st.text_input("Student Name")
    status = st.selectbox("Status", ["P", "A", "L", "O"])
    
    submit = st.form_submit_button("Submit")

if submit:
    try:
        client = connect_to_sheets()
        # Ensure your sheet is named 'AttendanceData'
        sheet = client.open("Cognify_Master").sheet1 
        sheet.append_row([str(date_input), teacher, class_name, subject, topic, homework, student_name, status])
        st.success("Data sent to Google Sheets!")
    except Exception as e:
        st.error(f"Error: {e}")
