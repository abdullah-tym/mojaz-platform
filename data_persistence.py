# data_persistence.py

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date # Import date for type checking

from config import DATA_FILE # Import DATA_FILE from config

def load_data():
    """
    Loads application data from a JSON file into st.session_state.
    Initializes empty DataFrames with correct columns if the file does not exist or is empty.
    """
    # Always initialize empty DataFrames with their full column structure first
    _initialize_empty_data()

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load data into already structured DataFrames, if data exists in JSON
            if data.get("clients"):
                st.session_state.clients = pd.DataFrame(data["clients"])
            if data.get("cases"):
                st.session_state.cases = pd.DataFrame(data["cases"])
            if data.get("invoices"):
                st.session_state.invoices = pd.DataFrame(data["invoices"])
            if data.get("reminders"):
                st.session_state.reminders = pd.DataFrame(data["reminders"])

            # Apply type conversions only if the DataFrames are not empty after loading
            # Clients
            if not st.session_state.clients.empty:
                st.session_state.clients['client_id'] = st.session_state.clients['client_id'].astype(int)

            # Cases
            if not st.session_state.cases.empty:
                st.session_state.cases['case_id'] = st.session_state.cases['case_id'].astype(int)
                st.session_state.cases['client_id'] = st.session_state.cases['client_id'].astype(int)
                st.session_state.cases['court_date'] = pd.to_datetime(st.session_state.cases['court_date']).dt.date

            # Invoices
            if not st.session_state.invoices.empty:
                st.session_state.invoices['invoice_id'] = st.session_state.invoices['invoice_id'].astype(int)
                st.session_state.invoices['client_id'] = st.session_state.invoices['client_id'].astype(int)
                if 'case_id' in st.session_state.invoices.columns:
                    st.session_state.invoices['case_id'] = st.session_state.invoices['case_id'].fillna(0).astype(int)
                st.session_state.invoices['amount'] = st.session_state.invoices['amount'].astype(float)
                st.session_state.invoices['paid'] = st.session_state.invoices['paid'].astype(bool)
                st.session_state.invoices['date'] = pd.to_datetime(st.session_state.invoices['date']).dt.date

            # Reminders
            if not st.session_state.reminders.empty:
                st.session_state.reminders['reminder_id'] = st.session_state.reminders['reminder_id'].astype(int)
                st.session_state.reminders['related_id'] = st.session_state.reminders['related_id'].astype(int)
                st.session_state.reminders['date'] = pd.to_datetime(st.session_state.reminders['date']).dt.date
                st.session_state.reminders['is_completed'] = st.session_state.reminders['is_completed'].astype(bool)

        except json.JSONDecodeError:
            st.error("Error decoding data file. Starting with empty data.")
            # _initialize_empty_data() already called
        except Exception as e:
            st.error(f"An unexpected error occurred while loading data: {e}. Starting with empty data.")
            # _initialize_empty_data() already called

def _initialize_empty_data():
    """Initializes empty DataFrames in session state with predefined columns."""
    st.session_state.clients = pd.DataFrame(columns=["client_id", "name", "phone", "email", "notes"])
    st.session_state.cases = pd.DataFrame(columns=["case_id", "client_id", "case_name", "case_type", "status", "court_date", "opposing_party", "case_description", "responsible_lawyer", "notes"])
    st.session_state.invoices = pd.DataFrame(columns=["invoice_id", "client_id", "case_id", "amount", "paid", "date"])
    st.session_state.reminders = pd.DataFrame(columns=["reminder_id", "related_type", "related_id", "description", "date", "is_completed"])


def save_data():
    """
    Saves current application data from st.session_state to a JSON file.
    Converts date objects to strings for JSON serialization.
    """
    # Convert date objects in DataFrames to string format for JSON serialization
    clients_data = st.session_state.clients.to_dict(orient="records")
    
    cases_data = st.session_state.cases.copy()
    if not cases_data.empty:
        cases_data['court_date'] = cases_data['court_date'].apply(lambda x: x.isoformat() if isinstance(x, date) else x)
    cases_data = cases_data.to_dict(orient="records")

    invoices_data = st.session_state.invoices.copy()
    if not invoices_data.empty:
        invoices_data['date'] = invoices_data['date'].apply(lambda x: x.isoformat() if isinstance(x, date) else x)
    invoices_data = invoices_data.to_dict(orient="records")

    reminders_data = st.session_state.reminders.copy()
    if not reminders_data.empty:
        reminders_data['date'] = reminders_data['date'].apply(lambda x: x.isoformat() if isinstance(x, date) else x)
    reminders_data = reminders_data.to_dict(orient="records")

    data = {
        "clients": clients_data,
        "cases": cases_data,
        "invoices": invoices_data,
        "reminders": reminders_data
    }
    
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Error saving data: {e}")
