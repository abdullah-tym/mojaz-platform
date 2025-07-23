# data_persistence.py

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date, timedelta # Import timedelta

from config import DATA_FILE # Import DATA_FILE from config

def load_data():
    """
    Loads application data from a JSON file into st.session_state.
    Initializes empty DataFrames with correct columns if the file does not exist or is empty.
    Ensures all expected columns are present, adding them with defaults if missing.
    """
    # Always initialize empty DataFrames with their full column structure first
    _initialize_empty_data()

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load data into already structured DataFrames, if data exists in JSON
            # Then, ensure all expected columns are present in the loaded DataFrame
            # before type conversions.

            # Clients
            if data.get("clients"):
                loaded_clients_df = pd.DataFrame(data["clients"])
                for col in st.session_state.clients.columns: # Iterate over expected columns
                    if col not in loaded_clients_df.columns:
                        loaded_clients_df[col] = None # Add missing column with None
                st.session_state.clients = loaded_clients_df
            
            # Cases
            if data.get("cases"):
                loaded_cases_df = pd.DataFrame(data["cases"])
                for col in st.session_state.cases.columns:
                    if col not in loaded_cases_df.columns:
                        loaded_cases_df[col] = None
                st.session_state.cases = loaded_cases_df

            # Invoices
            if data.get("invoices"):
                loaded_invoices_df = pd.DataFrame(data["invoices"])
                for col in st.session_state.invoices.columns:
                    if col not in loaded_invoices_df.columns:
                        loaded_invoices_df[col] = None
                st.session_state.invoices = loaded_invoices_df

            # Reminders
            if data.get("reminders"):
                loaded_reminders_df = pd.DataFrame(data["reminders"])
                for col in st.session_state.reminders.columns:
                    if col not in loaded_reminders_df.columns:
                        loaded_reminders_df[col] = None
                st.session_state.reminders = loaded_reminders_df
            
            # Users
            if data.get("users"):
                loaded_users_df = pd.DataFrame(data["users"])
                for col in st.session_state.users.columns:
                    if col not in loaded_users_df.columns:
                        loaded_users_df[col] = None
                st.session_state.users = loaded_users_df

            # Time Entries (NEW)
            if data.get("time_entries"):
                loaded_time_entries_df = pd.DataFrame(data["time_entries"])
                for col in st.session_state.time_entries.columns:
                    if col not in loaded_time_entries_df.columns:
                        loaded_time_entries_df[col] = None
                st.session_state.time_entries = loaded_time_entries_df


            # Apply type conversions only if the DataFrames are not empty after loading
            # Clients
            if not st.session_state.clients.empty:
                st.session_state.clients['client_id'] = st.session_state.clients['client_id'].astype(int)
                st.session_state.clients['type'] = st.session_state.clients['type'].fillna('فرد')
                st.session_state.clients['address'] = st.session_state.clients['address'].fillna('')
                st.session_state.clients['company_name'] = st.session_state.clients['company_name'].fillna('')
                st.session_state.clients['secondary_contact'] = st.session_state.clients['secondary_contact'].fillna('')


            # Cases
            if not st.session_state.cases.empty:
                st.session_state.cases['case_id'] = st.session_state.cases['case_id'].astype(int)
                st.session_state.cases['client_id'] = st.session_state.cases['client_id'].astype(int)
                st.session_state.cases['court_date'] = pd.to_datetime(st.session_state.cases['court_date'], errors='coerce').dt.date
                st.session_state.cases['court_date'] = st.session_state.cases['court_date'].fillna(datetime.today().date())
                st.session_state.cases['priority'] = st.session_state.cases['priority'].fillna('متوسطة')
                # Deserialize activity log
                st.session_state.cases['activity_log'] = st.session_state.cases['activity_log'].apply(lambda x: json.loads(x) if isinstance(x, str) else [])


            # Invoices
            if not st.session_state.invoices.empty:
                st.session_state.invoices['invoice_id'] = st.session_state.invoices['invoice_id'].astype(int)
                st.session_state.invoices['client_id'] = st.session_state.invoices['client_id'].astype(int)
                if 'case_id' in st.session_state.invoices.columns:
                    st.session_state.invoices['case_id'] = st.session_state.invoices['case_id'].fillna(0).astype(int)
                st.session_state.invoices['amount'] = st.session_state.invoices['amount'].astype(float)
                st.session_state.invoices['paid'] = st.session_state.invoices['paid'].astype(bool)
                st.session_state.invoices['date'] = pd.to_datetime(st.session_state.invoices['date'], errors='coerce').dt.date
                st.session_state.invoices['date'] = st.session_state.invoices['date'].fillna(datetime.today().date())
                st.session_state.invoices['due_date'] = pd.to_datetime(st.session_state.invoices['due_date'], errors='coerce').dt.date
                st.session_state.invoices['due_date'] = st.session_state.invoices['due_date'].fillna(datetime.today().date() + timedelta(days=30))

            # Reminders
            if not st.session_state.reminders.empty:
                st.session_state.reminders['reminder_id'] = st.session_state.reminders['reminder_id'].astype(int)
                st.session_state.reminders['related_id'] = st.session_state.reminders['related_id'].astype(int)
                st.session_state.reminders['date'] = pd.to_datetime(st.session_state.reminders['date'], errors='coerce').dt.date
                st.session_state.reminders['date'] = st.session_state.reminders['date'].fillna(datetime.today().date())
                st.session_state.reminders['is_completed'] = st.session_state.reminders['is_completed'].astype(bool)
            
            # Time Entries (NEW)
            if not st.session_state.time_entries.empty:
                st.session_state.time_entries['entry_id'] = st.session_state.time_entries['entry_id'].astype(int)
                st.session_state.time_entries['client_id'] = st.session_state.time_entries['client_id'].astype(int)
                st.session_state.time_entries['case_id'] = st.session_state.time_entries['case_id'].fillna(0).astype(int)
                st.session_state.time_entries['hours'] = st.session_state.time_entries['hours'].astype(float)
                st.session_state.time_entries['date'] = pd.to_datetime(st.session_state.time_entries['date'], errors='coerce').dt.date
                st.session_state.time_entries['date'] = st.session_state.time_entries['date'].fillna(datetime.today().date())


        except json.JSONDecodeError:
            st.error("Error decoding data file. Starting with empty data.")
        except Exception as e:
            st.error(f"An unexpected error occurred while loading data: {e}. Starting with empty data.")
    # If DATA_FILE doesn't exist, _initialize_empty_data() already set the session state.

def _initialize_empty_data():
    """Initializes empty DataFrames in session state with predefined columns."""
    st.session_state.clients = pd.DataFrame(columns=["client_id", "name", "phone", "email", "notes", "type", "address", "company_name", "secondary_contact"])
    st.session_state.cases = pd.DataFrame(columns=["case_id", "client_id", "case_name", "case_type", "status", "court_date", "opposing_party", "case_description", "responsible_lawyer", "notes", "priority", "activity_log"])
    st.session_state.invoices = pd.DataFrame(columns=["invoice_id", "client_id", "case_id", "amount", "paid", "date", "due_date"])
    st.session_state.reminders = pd.DataFrame(columns=["reminder_id", "related_type", "related_id", "description", "date", "is_completed"])
    st.session_state.users = pd.DataFrame(columns=["username", "password"])
    st.session_state.time_entries = pd.DataFrame(columns=["entry_id", "client_id", "case_id", "date", "hours", "category", "description"]) # NEW


def save_data():
    """
    Saves current application data from st.session_state to a JSON file.
    Converts date objects to strings for JSON serialization.
    Serializes complex objects like activity_log.
    """
    # Convert date objects in DataFrames to string format for JSON serialization
    clients_data = st.session_state.clients.to_dict(orient="records")
    
    cases_data = st.session_state.cases.copy()
    if not cases_data.empty:
        cases_data['court_date'] = cases_data['court_date'].apply(lambda x: x.isoformat() if isinstance(x, date) else x)
        # Serialize activity log to JSON string
        cases_data['activity_log'] = cases_data['activity_log'].apply(lambda x: json.dumps(x) if isinstance(x, list) else '[]')
    cases_data = cases_data.to_dict(orient="records")

    invoices_data = st.session_state.invoices.copy()
    if not invoices_data.empty:
        invoices_data['date'] = invoices_data['date'].apply(lambda x: x.isoformat() if isinstance(x, date) else x)
        invoices_data['due_date'] = invoices_data['due_date'].apply(lambda x: x.isoformat() if isinstance(x, date) else x)
    invoices_data = invoices_data.to_dict(orient="records")

    reminders_data = st.session_state.reminders.copy()
    if not reminders_data.empty:
        reminders_data['date'] = reminders_data['date'].apply(lambda x: x.isoformat() if isinstance(x, date) else x)
    reminders_data = reminders_data.to_dict(orient="records")

    users_data = st.session_state.users.to_dict(orient="records")

    time_entries_data = st.session_state.time_entries.copy() # NEW
    if not time_entries_data.empty:
        time_entries_data['date'] = time_entries_data['date'].apply(lambda x: x.isoformat() if isinstance(x, date) else x)
    time_entries_data = time_entries_data.to_dict(orient="records")


    data = {
        "clients": clients_data,
        "cases": cases_data,
        "invoices": invoices_data,
        "reminders": reminders_data,
        "users": users_data,
        "time_entries": time_entries_data # NEW
    }
    
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Error saving data: {e}")
