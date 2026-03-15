import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date
import json
import pandas as pd

st.set_page_config(page_title="Cognify Institute", layout="wide")

# CONNECT TO GOOGLE SHEETS
def connect_to_sheets():
    creds_dict = json.loads(st.secrets["gcp_service_account"])

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    return client


# LOAD STUDENTS FROM STUDENT LIST SHEET
def load_students(class_name):
    client = connect_to_sheets()
    sheet = client.open("Cognify_Master").worksheet("Student_List")

    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    students = df[df["Class"] == class_name]["Student Name"].tolist()
    return students


st.title("COGNIFY INSTITUTE - CLASS REPORT")

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

    students = []

    if class_name:
        try:
            students = load_students(class_name)
        except:
            st.warning("Student list not found yet")

    attendance_data = []

    if students:
        st.subheader("Mark Attendance")

        for student in students:
            status = st.selectbox(
                student,
                ["Present", "Absent"],
                key=student
            )

            attendance_data.append((student, status))

    submit = st.form_submit_button("Submit")

if submit:
    try:
        client = connect_to_sheets()
        sheet = client.open("Cognify_Master").worksheet("Attendance")

        for student, status in attendance_data:
            sheet.append_row([
                str(date_input),
                teacher,
                class_name,
                subject,
                student,
                status,
                topic,
                homework
            ])

        st.success("Attendance submitted successfully!")

    except Exception as e:
        st.error(e)
