# auth.py

import streamlit as st
import pandas as pd # Import pandas for DataFrame operations
from config import USERS # Import initial user credentials from config

def authenticate_user(save_data_func):
    """
    Handles user login and signup on the main page.
    Manages session persistence using st.query_params.
    Returns True if authenticated, False otherwise.
    """
    # Initialize session state variables if they don't exist
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None

    # Check for authentication token in query parameters on initial load
    if not st.session_state.authenticated and "auth_token" in st.query_params:
        token_username = st.query_params["auth_token"][0]
        # Verify token against stored users (simple check, could be more robust)
        if not st.session_state.users.empty and token_username in st.session_state.users['username'].values:
            st.session_state.authenticated = True
            st.session_state.username = token_username
            st.success(f"مرحباً بك مجدداً، {token_username}!")
            # Clean up query param for cleaner URL
            del st.query_params["auth_token"] # This might trigger a rerun, but it's cleaner

    if st.session_state.authenticated:
        # User is authenticated, return True to show main app
        return True
    else:
        # User is not authenticated, show login/signup form
        st.title("👋 مرحباً بك في موجز!")
        st.markdown("يرجى تسجيل الدخول أو إنشاء حساب جديد للمتابعة.")

        login_tab, signup_tab = st.tabs(["تسجيل الدخول", "إنشاء حساب جديد"])

        with login_tab:
            st.subheader("تسجيل الدخول")
            with st.form("login_form_main", clear_on_submit=False):
                username = st.text_input("اسم المستخدم", key="login_username_main")
                password = st.text_input("كلمة المرور", type="password", key="login_password_main")
                login_button = st.form_submit_button("دخول")

                if login_button:
                    # Check against loaded users data first
                    if not st.session_state.users.empty and \
                       username in st.session_state.users['username'].values and \
                       st.session_state.users[st.session_state.users['username'] == username]['password'].iloc[0] == password:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        # Set query parameter for persistence
                        st.experimental_set_query_params(auth_token=username)
                        st.success(f"تم تسجيل الدخول بنجاح! مرحباً، {username}!")
                        st.rerun()
                    # Fallback to initial config users if not found in loaded data (first run)
                    elif username in USERS and USERS[username] == password:
                        # If authenticated via config, add to session_state.users for persistence
                        if not st.session_state.users.empty and username not in st.session_state.users['username'].values:
                            new_user_df = pd.DataFrame([{"username": username, "password": password}])
                            st.session_state.users = pd.concat([st.session_state.users, new_user_df], ignore_index=True)
                            save_data_func() # Save the new user
                        elif st.session_state.users.empty: # If users DataFrame was empty
                            st.session_state.users = pd.DataFrame([{"username": username, "password": password}])
                            save_data_func()
                        
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        # Set query parameter for persistence
                        st.experimental_set_query_params(auth_token=username)
                        st.success(f"تم تسجيل الدخول بنجاح! مرحباً، {username}!")
                        st.rerun()
                    else:
                        st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")

        with signup_tab:
            st.subheader("إنشاء حساب جديد")
            with st.form("signup_form_main", clear_on_submit=True):
                new_username = st.text_input("اسم المستخدم الجديد", key="signup_username_main")
                new_password = st.text_input("كلمة المرور الجديدة", type="password", key="signup_password_main")
                confirm_password = st.text_input("تأكيد كلمة المرور", type="password", key="signup_confirm_password_main")
                signup_button = st.form_submit_button("إنشاء حساب")

                if signup_button:
                    if not new_username or not new_password or not confirm_password:
                        st.warning("الرجاء ملء جميع الحقول.")
                    elif new_password != confirm_password:
                        st.error("كلمة المرور وتأكيد كلمة المرور غير متطابقين.")
                    elif not st.session_state.users.empty and new_username in st.session_state.users['username'].values:
                        st.error("اسم المستخدم هذا موجود بالفعل. يرجى اختيار اسم مستخدم آخر.")
                    else:
                        # Add new user to session state and save
                        new_user_df = pd.DataFrame([{"username": new_username, "password": new_password}])
                        st.session_state.users = pd.concat([st.session_state.users, new_user_df], ignore_index=True)
                        save_data_func()
                        st.success(f"✅ تم إنشاء الحساب بنجاح لـ {new_username}! يمكنك الآن تسجيل الدخول.")
                        # Optionally, log them in directly after signup
                        # st.session_state.authenticated = True
                        # st.session_state.username = new_username
                        # st.experimental_set_query_params(auth_token=new_username)
                        # st.rerun()
        return False
