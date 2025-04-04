import streamlit as st
import pandas as pd
import datetime
import os
import re
import base64
import requests
from io import BytesIO

# ✅ SharePoint Direct Download Link
SHAREPOINT_FILE_URL = "https://airtcom-my.sharepoint.com/:f:/g/personal/bakula_randomtrees_com/ERxk3s9m-69Fk1oBzkkE84wBMUXUTJtbElVumYtitGxUEQ?download=1"

def load_data():
    try:
        # ✅ Download file from SharePoint
        response = requests.get(SHAREPOINT_FILE_URL)
        response.raise_for_status()  # Raise error if download fails
        
        # ✅ Read Excel file from response
        df = pd.read_excel(BytesIO(response.content), engine="openpyxl")
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def parse_week_to_dates(week_str):
    try:
        match = re.search(r'(\d{1,2})\s*([A-Za-z]+)', week_str)
        if match:
            day, month = match.groups()
            current_year = datetime.datetime.today().year
            return datetime.datetime.strptime(f"{day} {month} {current_year}", "%d %b %Y").date()
    except:
        return None

def apply_status_circle(status_text):
    status_colors = {
        "Green": "#4CAF50",
        "Amber Green": "linear-gradient(to left, #4CAF50 50%, #FFC107 50%)",
        "Amber": "#FFC107",
        "Red Amber": "linear-gradient(to left, #FFC107 50%, #FF0000 50%)",
        "Red": "#FF0000"
    }
    return status_colors.get(status_text, "#B0BEC5")  # Default to gray

def apply_sentiment_circle(sentiment):
    sentiment_colors = {
        "Positive": "#4CAF50",
        "Neutral": "#FFC107",
        "Negative": "#F44336"
    }
    return sentiment_colors.get(sentiment, "#B0BEC5")

def generate_styled_table_html(df):
    if df.empty:
        return "<p>No data available.</p>"
    
    columns = [col for col in df.columns if col != "Start Date"]  # Remove Start Date column
    table_html = """
    <div style='display: flex; justify-content: center; width: 100%;'>
        <table style='border-collapse: collapse; font-family: Arial, sans-serif; font-size: 9px; width: 100%;'>
    """
    
    table_html += "<tr style='background-color: #f2f2f2; text-align: center; font-weight: bold;'>"
    for col in columns:
        table_html += f"<th style='border: 1px solid #ddd; padding: 8px; white-space: nowrap;'>{col}</th>"
    table_html += "</tr>"
    
    for _, row in df.iterrows():
        table_html += "<tr style='background-color: #f9f9f9; text-align: center;'>"
        for col in columns:
            cell_content = row[col] if pd.notna(row[col]) else ""
            
            # **Ensure "Week" and "Project Name" stay on one line**
            if col in ["Week", "Project Name"]:
                table_html += f"<td style='border: 1px solid #ddd; padding: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{cell_content}</td>"
            
            # **Ensure "Key Progress" wraps text properly**
            elif col == "Key Progress":
                table_html += f"<td style='border: 1px solid #ddd; padding: 8px; white-space: normal; word-break: break-word; min-width: 200px; max-width: 400px; text-align: left;'>{cell_content}</td>"
            
            # **Status and Sentiment indicators**
            elif col == "Project Status":
                color = apply_status_circle(cell_content)
                circle_html = f"<div style='display: flex; justify-content: center;'><span style='display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: {color};'></span></div>"
                table_html += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{circle_html}</td>"
            
            elif col == "Customer Sentiment Rating":
                color = apply_sentiment_circle(cell_content)
                circle_html = f"<div style='display: flex; justify-content: center;'><span style='display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: {color};'></span></div>"
                table_html += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: center;'>{circle_html}</td>"
            
            else:
                table_html += f"<td style='border: 1px solid #ddd; padding: 8px; text-align: left;'>{cell_content}</td>"

        table_html += "</tr>"
    
    table_html += "</table></div>"
    return table_html

def load_image_as_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def main():

    st.markdown(
        """
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <img src='data:image/png;base64,{}' alt='RandomTrees Logo' style='width: 200px;'/>
            <div style='width: 150px; height: 75px; background-color: #ccc; text-align: center; line-height: 75px; font-weight: bold;'>PDE Logo</div>
        </div>
        """.format(load_image_as_base64(r"randomtrees.png")),
        unsafe_allow_html=True
    )

    st.title("Project Monitoring Dashboard")
    
    df = load_data()
    
    if df is not None:
        df["Start Date"] = df["Week"].apply(parse_week_to_dates)
        df = df.dropna(subset=["Start Date"])
        
        st.markdown("<h3 style='text-align: center;'>Select Date Range</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Start Date", value=datetime.date.today() - datetime.timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", value=datetime.date.today())
        
        df = df[(df["Start Date"] >= start_date) & (df["Start Date"] <= end_date)]
        
        st.markdown("<h3 style='text-align: center;'>Select Options</h3>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            week_selected = st.selectbox("Week", df["Week"].unique(), index=None, placeholder="All Selections")
        with col2:
            account_selected = st.selectbox("Account Name", df["Account Name"].unique(), index=None, placeholder="All Selections")
        with col3:
            client_selected = st.selectbox("Client Name", df["Client Name"].unique(), index=None, placeholder="All Selections")
        with col4:
            project_selected = st.selectbox("Project Name", df["Project Name"].unique(), index=None, placeholder="All Selections")
        
        submit = st.button("SUBMIT")
        if submit:
            st.subheader("Project Details")
            if not df.empty:
                styled_table = generate_styled_table_html(df)
                st.markdown(styled_table, unsafe_allow_html=True)
            else:
                st.write("No data available.")

if __name__ == "__main__":
    main()