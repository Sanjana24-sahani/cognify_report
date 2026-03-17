import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
import json

# Page Config
st.set_page_config(page_title="Cognify Institute Report", layout="wide")

# CSS to make the form look professional
st.markdown("""
    <style>
    .header {text-align: center; color: #1E3A8A; font-weight: bold;}
    .sub-header {text-align: center; font-style: italic; margin-bottom: 20px;}
    .title-box {background-color: #1E3A8A; color: white; padding: 10px; text-align: center; border-radius: 5px; margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='header'>COGNIFY INSTITUTE</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Excellence in Academic Learning</p>", unsafe_allow_html=True)
st.markdown("<div class='title-box'>TEACHER DAILY CLASS REPORT</div>", unsafe_allow_html=True)

# Connection Function
def get_gsheet():
    # Use the dictionary constructor to avoid the AttrDict error
    creds_dict = dict(st.secrets["gcp_service_account"])
    
    # These two scopes are REQUIRED for full access
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file"
    ]
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("Cognify_Master").Attendance

# Form Layout

with st.form("teacher_report"):
    c1, c2 = st.columns(2)
    with c1:
        date_input = st.date_input("Date")
        subject = st.text_input("Subject")
        teacher = st.text_input("Teacher Name")
    with c2:
        class_name = st.text_input("Class")
        topic = st.text_area("Topic Covered", height=100)
    
    homework = st.text_input("Homework Given")
    remarks = st.text_area("Remarks")
    
    st.markdown("### STUDENT ATTENDANCE")
    
    # 20 initial rows, dynamic for adding more
    data = {
        "Student ID": ["" for _ in range(10)],
        "Student Name": ["" for _ in range(10)],
        "Status": [None for _ in range(10)],
        "Late / Remarks": ["" for _ in range(10)]
    }
    df = pd.DataFrame(data)
    
    edited_df = st.data_editor(
        df, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status (P/A/L/O)",
                options=["P", "A", "L", "O"],
                required=False,
            )
        }
    )
    
    submitted = st.form_submit_button("SUBMIT REPORT")

if submitted:
    try:
        sheet = get_gsheet()
        
        rows_to_add = []
        for index, row in edited_df.iterrows():
            if row["Student ID"] != "":
                rows_to_add.append([
                    str(date_input), teacher, class_name, subject, 
                    row["Student ID"], row["Student Name"], 
                    row["Status"], row["Late / Remarks"], 
                    topic, homework, remarks
                ])
        
        if rows_to_add:
            # sheet.append_rows returns a dict on success
            result = sheet.append_rows(rows_to_add)
            
            # If we reach here without an exception, it's a success!
            st.success("✅ Attendance submitted successfully!")
        else:
            st.warning("⚠️ No data to submit. Please fill in the Student ID.")
            
    except Exception as e:
        # Check if 'e' is actually just a successful response string
        if "200" in str(e):
            st.success("✅ Attendance submitted successfully!")
        else:
            st.error(f"Actual Submission Error: {e}")
