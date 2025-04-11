import streamlit as st
import pandas as pd
import datetime
import os
import re
import base64
import requests
from io import BytesIO

# ✅ SharePoint Direct Download Link
SHAREPOINT_FILE_URL = "https://airtcom-my.sharepoint.com/:x:/g/personal/bakula_randomtrees_com/ERxk3s9m-69Fk1oBzkkE84wBMUXUTJtbElVumYtitGxUEQ?download=1"

def load_data():
    try:
        response = requests.get(SHAREPOINT_FILE_URL)
        response.raise_for_status()
        df = pd.read_excel(BytesIO(response.content), engine="openpyxl", keep_default_na=False, na_values=[])
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
    return status_colors.get(status_text, "#B0BEC5")

def apply_sentiment_circle(sentiment):
    sentiment_colors = {
        "Green": "#4CAF50",
        "Amber": "#FFC107",
        "Red": "#FF0000"
    }
    return sentiment_colors.get(sentiment, "#B0BEC5")

def generate_styled_table_html(df):
    if df.empty:
        return "<p>No data available.</p>"

    columns = [col for col in df.columns if col != "Start Date"]

    wrap_left_align_cols = [
        "Key Progress (This Week)",
        "Upcoming Milestones",
        "Risks & Issues",
        "Customer Sentiment Remarks",
        "Value adds",
        "Leadership Support Needed",
        "Comments"
    ]

    col_width_map = {
        "Week": "140px",
        "Account Name": "100px",
        "Client Name": "100px",
        "Industry": "90px",
        "Project Name": "120px",
        "Project Status": "90px",
        "Customer Sentiment Rating": "160px",
        "Customer Sentiment Remarks": "160px"
    }

    wrap_col_width = "150px"

    table_html = """
    <div style='display: flex; width: 100%; justify-content: center;'>
        <table style='border-collapse: collapse; font-family: Arial, sans-serif; font-size: 10px; table-layout: auto; width: 100%; max-width: 100%; min-width: 1200px;'>
    """

    table_html += "<tr style='background-color: #f2f2f2; text-align: center; font-weight: bold;'>"
    for col in columns:
        width = col_width_map.get(col, wrap_col_width if col in wrap_left_align_cols else "80px")
        table_html += f"<th style='border: 1px solid #ddd; padding: 6px; width: {width};'>{col}</th>"
    table_html += "</tr>"

    for _, row in df.iterrows():
        table_html += "<tr style='background-color: #f9f9f9;'>"
        for col in columns:
            value = row[col]
            if value is None or str(value).strip() == "":
                cell_content = ""
            else:
                cell_content = str(value).strip()

            if col in ["Week", "Project Name", "Account Name", "Industry", "Client Name"]:
                table_html += f"<td style='border: 1px solid #ddd; padding: 6px; text-align: center; vertical-align: middle;'>{cell_content}</td>"
            elif col in wrap_left_align_cols:
                table_html += f"<td style='border: 1px solid #ddd; padding: 6px; white-space: pre-wrap; word-break: break-word; text-align: left; vertical-align: top;'>{cell_content}</td>"
            elif col == "Project Status":
                color = apply_status_circle(cell_content)
                circle_html = f"<div style='display: flex; justify-content: center;'><span style='display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: {color};'></span></div>"
                table_html += f"<td style='border: 1px solid #ddd; padding: 6px; text-align: center;'>{circle_html}</td>"
            elif col == "Customer Sentiment Rating":
                color = apply_sentiment_circle(cell_content)
                circle_html = f"<div style='display: flex; justify-content: center;'><span style='display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: {color};'></span></div>"
                table_html += f"<td style='border: 1px solid #ddd; padding: 6px; text-align: center;'>{circle_html}</td>"
            else:
                table_html += f"<td style='border: 1px solid #ddd; padding: 6px; text-align: left;'>{cell_content}</td>"
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

        earliest_date = df["Start Date"].min()

        st.markdown("<h3 style='text-align: center;'>Select Date Range</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input("Start Date", value=earliest_date, min_value=earliest_date)
        with col2:
            end_date = st.date_input("End Date", value=datetime.date.today())

        st.markdown("<h3 style='text-align: center;'>Select Options</h3>", unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            week_selected = st.selectbox("Week", sorted(df["Week"].unique()), index=None, placeholder="All Selections")

        filtered_df_for_dropdowns = df.copy()
        if week_selected:
            filtered_df_for_dropdowns = filtered_df_for_dropdowns[filtered_df_for_dropdowns["Week"] == week_selected]

        with col2:
            account_selected = st.selectbox("Account Name", sorted(filtered_df_for_dropdowns["Account Name"].unique()), index=None, placeholder="All Selections")

        if account_selected:
            filtered_df_for_dropdowns = filtered_df_for_dropdowns[filtered_df_for_dropdowns["Account Name"] == account_selected]

        with col3:
            client_selected = st.selectbox("Client Name", sorted(filtered_df_for_dropdowns["Client Name"].unique()), index=None, placeholder="All Selections")

        if client_selected:
            filtered_df_for_dropdowns = filtered_df_for_dropdowns[filtered_df_for_dropdowns["Client Name"] == client_selected]

        with col4:
            industry_selected = st.selectbox("Industry", sorted(filtered_df_for_dropdowns["Industry"].unique()), index=None, placeholder="All Selections")

        if industry_selected:
            filtered_df_for_dropdowns = filtered_df_for_dropdowns[filtered_df_for_dropdowns["Industry"] == industry_selected]

        with col5:
            project_selected = st.selectbox("Project Name", sorted(filtered_df_for_dropdowns["Project Name"].unique()), index=None, placeholder="All Selections")

        submit = st.button("SUBMIT")
        if submit:
            st.subheader("Project Details")
            filtered_df = df.copy()

            # ✅ Priority to week filter
            if week_selected:
                filtered_df = filtered_df[filtered_df["Week"] == week_selected]
            else:
                filtered_df = filtered_df[(filtered_df["Start Date"] >= start_date) & (filtered_df["Start Date"] <= end_date)]

            if account_selected:
                filtered_df = filtered_df[filtered_df["Account Name"] == account_selected]
            if client_selected:
                filtered_df = filtered_df[filtered_df["Client Name"] == client_selected]
            if industry_selected:
                filtered_df = filtered_df[filtered_df["Industry"] == industry_selected]
            if project_selected:
                filtered_df = filtered_df[filtered_df["Project Name"] == project_selected]

            if not filtered_df.empty:
                styled_table = generate_styled_table_html(filtered_df)
                st.markdown(styled_table, unsafe_allow_html=True)
            else:
                st.write("No data available.")

if __name__ == "__main__":
    main()