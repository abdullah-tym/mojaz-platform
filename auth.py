# auth.py

import streamlit as st
from config import USERS # Import user credentials from config

def authenticate_user():
    """
    Handles user login and logout.
    Sets st.session_state.authenticated and st.session_state.username.
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None

    if st.session_state.authenticated:
        # Display logout button if authenticated
        st.sidebar.success(f"مرحباً، {st.session_state.username}!")
        if st.sidebar.button("تسجيل الخروج", key="logout_button"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun() # Rerun to show login form
        return True
    else:
        # Display login form
        st.sidebar.subheader("تسجيل الدخول")
        with st.sidebar.form("login_form"):
            username = st.text_input("اسم المستخدم", key="login_username")
            password = st.text_input("كلمة المرور", type="password", key="login_password")
            login_button = st.form_submit_button("دخول")

            if login_button:
                if username in USERS and USERS[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.sidebar.success(f"تم تسجيل الدخول بنجاح! مرحباً، {username}!")
                    st.rerun() # Rerun to hide login form and show app content
                else:
                    st.sidebar.error("اسم المستخدم أو كلمة المرور غير صحيحة.")
        return False
