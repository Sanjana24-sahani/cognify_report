import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date

# --- NEW CONNECTION LOGIC ---
def get_gsheet_client():
    # You will use the secrets to store your JSON credentials
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict)
    client = gspread.authorize(creds)
    return client

# --- REST OF YOUR FORM CODE ---
# When submitting:
# client = get_gsheet_client()
# sheet = client.open("Your_Sheet_Name").sheet1
# sheet.append_rows(new_report_df.values.tolist())

# Page config
st.set_page_config(page_title="Cognify Institute", layout="wide")

# Custom CSS to hide "Ctrl+Enter" and style the app
st.markdown("""
    <style>
    .stTextArea div[data-baseweb="base-input"] + div { display: none; }
    .main-title {text-align: center; color: #1E3A8A; margin-bottom: 0;}
    .section-header {background-color: #1E3A8A; color: white; padding: 10px; text-align: center; border-radius: 5px;}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>COGNIFY INSTITUTE</h1>", unsafe_allow_html=True)
st.markdown("<div class='section-header'>TEACHER DAILY CLASS REPORT</div><br>", unsafe_allow_html=True)

# Establishing Google Sheets Connection
# Note: You will need to set up your secrets/credentials in Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

with st.form("class_report_form"):
    col1, col2 = st.columns(2)
    with col1:
        report_date = st.date_input("Date", date.today())
        subject = st.text_input("Subject")
        teacher_name = st.text_input("Teacher Name")
    with col2:
        class_name = st.text_input("Class")
        topic_covered = st.text_area("Topic Covered")
    
    homework = st.text_input("Homework Given")
    remarks = st.text_area("General Remarks")

    st.markdown("### STUDENT ATTENDANCE")
    
    # Pre-define empty rows for the teacher
    input_data = pd.DataFrame(
        {"Student ID": ["" for _ in range(15)], 
         "Student Name": ["" for _ in range(15)], 
         "Status": [None for _ in range(15)], 
         "Late / Remarks": ["" for _ in range(15)]}
    )

    edited_df = st.data_editor(
        input_data, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status", options=["P", "A", "L", "O"], required=True
            )
        }
    )

    submit_button = st.form_submit_button("SUBMIT TO CLOUD")

if submit_button:
    if not teacher_name or not subject:
        st.error("Please enter Teacher Name and Subject.")
    else:
        # Filter valid rows
        valid_df = edited_df.dropna(subset=["Status"])
        valid_df = valid_df[valid_df["Student Name"].str.strip() != ""]

        if valid_df.empty:
            st.warning("No student attendance recorded.")
        else:
            # Prepare data for Google Sheets
            new_rows = []
            for _, row in valid_df.iterrows():
                new_rows.append({
                    "Date": str(report_date),
                    "Teacher": teacher_name,
                    "Class": class_name,
                    "Subject": subject,
                    "Topic": topic_covered,
                    "Homework": homework,
                    "Remarks": remarks,
                    "Student ID": row["Student ID"],
                    "Student Name": row["Student Name"],
                    "Status": row["Status"],
                    "Attendance Note": row["Late / Remarks"]
                })
            
            new_report_df = pd.DataFrame(new_rows)
            
            # Fetch existing data from Google Sheet
            existing_data = conn.read(worksheet="Sheet1")
            
            # Combine and Update
            updated_df = pd.concat([existing_data, new_report_df], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            
            st.success("✅ Data successfully synced with Google Sheets!")
            st.balloons()
