import streamlit as st
st.set_page_config(layout="wide", page_title="My App", initial_sidebar_state="auto")

# Now safe to run other Streamlit commands
hide_ui = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_ui, unsafe_allow_html=True)
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.exceptions import LoginError
import extra_streamlit_components as stx
import datetime
import traceback
import re

from admin_utils import load_users, add_user, delete_user, update_password, list_users, update_role, reset_password
from utils import load_data, parse_week_to_dates, generate_styled_table_html

def main():
    try:
        # st.set_page_config(layout="wide")

        # Load user credentials
        user_data = load_users()
        authenticator = stauth.Authenticate(
            credentials=user_data['credentials'],
            cookie_name="sreamelite_cookie",
            key="abcdef",  # can be any string
            cookie_expiry_days=1
        )
        auth_status = None
        _ = authenticator.login("main")
        print(_, flush = True)
        auth_status = st.session_state["authentication_status"]
        name = st.session_state["name"]
        username = st.session_state["username"]

        if auth_status is False:
            st.error("Incorrect username or password")
            for key in list(st.session_state.keys()):
                st.session_state.pop(key, None)


        elif auth_status is None:
            st.warning("Please enter your username and password")
            for key in list(st.session_state.keys()):
                st.session_state.pop(key, None)

        elif auth_status:
            # st.sidebar.title(f"Welcome, {name}")
            role = user_data['credentials']['usernames'][username]["role"]

            if "page" not in st.session_state:
                st.session_state.pop('page', "Dashboard")
                st.session_state.page = "Dashboard"
                st.rerun()

            # col1, col2, col3 = st.columns([1, 9, 1])
            # with col3:
            #     if st.button("Settings", use_container_width=True):
            #         st.session_state.page = "Settings"
            # # Logout button
            # with col1:
            #     authenticator.logout("Logout", "main")

            if st.session_state.page == "Dashboard":
                col1, col2, col3 = st.columns([1, 9, 1])
                with col3:
                    if st.button("Settings", use_container_width=True):
                        st.session_state.page = "Settings"
                        st.rerun()
                # Logout button
                with col1:
                    authenticator.logout("Logout", "main")
                st.title("📊 Dashboard")
                # st.write("This is the main dashboard.")
                df = load_data()

                if df is not None:
                    print(df.head(), flush =True)
                    df["Start Date"] = df["Week"].apply(parse_week_to_dates)
                    df = df.dropna(subset=["Start Date"])

                    earliest_date = df["Start Date"].min()
                    print(earliest_date, flush =True)
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
                            print(filtered_df.head(), flush = True)
                            styled_table = generate_styled_table_html(filtered_df)
                            st.markdown(styled_table, unsafe_allow_html=True)
                        else:
                            st.write("No data available.")

            elif st.session_state.page == "Settings" and role == "admin":
                col1, col2, col3 = st.columns([1, 9, 1])
                with col3:
                    if st.button("Dashboard", use_container_width=True):
                        st.session_state.page = "Dashboard"
                        st.rerun()
                # Logout button
                with col1:
                    authenticator.logout("Logout", "main")
                st.title("⚙️ Admin Settings")

                tab1, tab2, tab3, tab4, tab5 = st.tabs(["Add User", "Delete User", "Change Password", "Change Role", "User List"])

                with tab1:
                    st.subheader("Add New User")
                    new_user = st.text_input("Username", key="add_user")
                    new_pass = st.text_input("Password", key="add_pass")
                    new_role = st.selectbox("Role", ["user", "admin"], key="add_role")
                    if st.button("Create User", key="add_btn"):
                        # new_user = new_user+'@randomtrees.com'
                        if new_user and not bool(re.match("^[A-Za-z0-9]+$", new_user)):
                            st.error("Username must contain only letters and numbers (no spaces or special characters).")
                        elif len(new_pass)<8:
                            st.error("Password must be at least 8 characters long.")
                        elif add_user(new_user, new_pass, new_role):
                            st.success("User added successfully.")
                        else:
                            st.error("User already exists.")

                with tab2:
                    st.subheader("Delete User")
                    del_user = st.text_input("Username to Delete", key="del_user")
                    if st.button("Delete", key="del_btn"):
                        if delete_user(del_user):
                            st.success("User deleted.")
                        else:
                            st.error("User not found.")

                with tab3:
                    st.subheader("Change User Password")
                    user_to_update = st.text_input("Username", key="update_user")
                    new_password = st.text_input("New Password", key="update_pass")
                    if st.button("Change Password", key="update_btn"):
                        if len(new_password)<8:
                            st.error("Password must be at least 8 characters long.")
                        elif update_password(user_to_update, new_password):
                            st.success("Password updated.")
                        else:
                            st.error("User not found.")

                with tab4:
                    st.subheader("Change User Role")
                    user_to_update_role = st.text_input("Username", key="update_user_role")
                    new_role = st.selectbox("Role", ["user", "admin"], key="new_role", placeholder=None)
                    if st.button("Change Role", key="update_role_btn"):
                        if update_role(user_to_update_role, new_role):
                            st.success("User Role updated.")
                        else:
                            st.error("User not found.")

                with tab5:
                    st.subheader("List of Users and Roles")
                    users = list_users()
                    for uname, uinfo in users.items():
                        if uname=='zekinv':
                            continue
                        st.write(f"**{uname}** — *{uinfo['role']}*")

            elif st.session_state.page == "Settings" and role == "user":
                col1, col2, col3 = st.columns([1, 9, 1])
                with col3:
                    if st.button("Dashboard", use_container_width=True):
                        st.session_state.page = "Dashboard"
                        st.rerun()
                # Logout button
                with col1:
                    authenticator.logout("Logout", "main")
                st.title("⚙️ User Settings")

                st.subheader("Change Password")
                user_to_update_pass = st.session_state["username"]
                old_password = st.text_input("Old Password", key="old_pass")
                new_password = st.text_input("New Password", key="new_pass")
                confirm_password = st.text_input("Confirm Password", key="confirm_pass")
                if new_password==confirm_password:
                    if st.button("Change Password", key="update_btn"):
                        if len(new_password)<8:
                            st.error("Password must be at least 8 characters long.")
                        elif reset_password(user_to_update_pass, new_password, old_password):
                            st.success("Password updated.")
                        else:
                            st.error("In-Valid Password")
                else:
                    st.error("Confirm Password Not Matching")
    except LoginError:
        if auth_status:
            authenticator.logout("Logout", "main")
        for key in ['name', 'username', 'authentication_status']:
            if key in st.session_state:
                del st.session_state[key]
        cookie_manager = stx.CookieManager(key="abcdef")
        # st.write("Cookies available:", cookie_manager.cookies)
        cookie_manager.delete('sreamelite_cookie')
        print(traceback.format_exc(), flush =True)
        st.rerun()
    
if __name__=='__main__':
    try:
        main()
    except Exception as e:
        for key in list(st.session_state.keys()):
            st.session_state.pop(key, None)
        print(traceback.format_exc(), flush =True)