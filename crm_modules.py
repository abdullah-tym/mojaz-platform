# crm_modules.py

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Import necessary functions/constants from other modules
from config import (
    CASE_TYPE_OPTIONS, CASE_STATUS_OPTIONS,
    REMINDER_RELATED_TYPES, PAYMENT_STATUS_OPTIONS
)
from pdf_utils import reshape_arabic # Assuming reshape_arabic is needed here too

# --- Helper for ID Generation (re-defined here for modularity, or import from utils if created) ---
def next_id_local(df, col):
    """Generates the next sequential ID for a DataFrame."""
    if df.empty:
        return 1
    return df[col].max() + 1

# --- Client Management Functions and UI ---
def render_client_management(next_id_func, save_data_func, reshape_arabic_func):
    """Renders the UI for client management."""
    st.header("👥 إدارة العملاء")
    st.markdown("أضف، عدّل، أو احذف بيانات العملاء.")

    with st.expander("➕ إضافة عميل جديد", expanded=False):
        with st.form("add_client_form", clear_on_submit=True):
            col_c_add1, col_c_add2 = st.columns(2)
            with col_c_add1:
                new_client_name = st.text_input("اسم العميل", key="crm_new_client_name_input")
                new_client_phone = st.text_input("رقم الهاتف", key="crm_new_client_phone_input")
            with col_c_add2:
                new_client_email = st.text_input("البريد الإلكتروني", key="crm_new_client_email_input")
                new_client_notes = st.text_area("ملاحظات إضافية", key="crm_new_client_notes_input")
            
            submitted_client = st.form_submit_button("➕ حفظ العميل")
            if submitted_client:
                if new_client_name and new_client_phone:
                    cid = next_id_func(st.session_state.clients, "client_id")
                    st.session_state.clients.loc[len(st.session_state.clients)] = [cid, new_client_name, new_client_phone, new_client_email, new_client_notes]
                    save_data_func()
                    st.success(f"✅ تم إضافة العميل: {reshape_arabic_func(new_client_name)} بنجاح!")
                    st.rerun()
                else:
                    st.warning("الرجاء إدخال اسم العميل ورقم الهاتف على الأقل.")
    
    st.markdown("---")
    st.markdown("### 📋 قائمة العملاء")
    if not st.session_state.clients.empty:
        df_clients_display = st.session_state.clients.copy()
        df_clients_display = df_clients_display.rename(columns={
            "name": "الاسم", "phone": "الهاتف", "email": "البريد الإلكتروني", "notes": "ملاحظات"
        })
        
        search_client = st.text_input("ابحث عن عميل (بالاسم أو الهاتف أو البريد الإلكتروني)", "", key="crm_search_client_input")
        filtered_clients = df_clients_display[
            df_clients_display["الاسم"].astype(str).str.contains(search_client, case=False, na=False) |
            df_clients_display["الهاتف"].astype(str).str.contains(search_client, case=False, na=False) |
            df_clients_display["البريد الإلكتروني"].astype(str).str.contains(search_client, case=False, na=False)
        ]
        
        st.dataframe(filtered_clients.set_index("client_id"))

        st.markdown("### ✏️ تعديل / حذف عميل")
        if not filtered_clients.empty:
            client_to_edit_id = st.selectbox(
                "اختر العميل للتعديل أو الحذف", 
                filtered_clients["client_id"].tolist(), 
                format_func=lambda x: f"{x} - {st.session_state.clients[st.session_state.clients['client_id'] == x]['name'].iloc[0]}",
                key="crm_select_client_to_edit"
            )
            
            current_client_data = st.session_state.clients[st.session_state.clients["client_id"] == client_to_edit_id].iloc[0]

            with st.form("edit_client_form"):
                col_c_edit1, col_c_edit2 = st.columns(2)
                with col_c_edit1:
                    edited_client_name = st.text_input("اسم العميل", value=current_client_data["name"], key="crm_edited_client_name_input")
                    edited_client_phone = st.text_input("رقم الهاتف", value=current_client_data["phone"], key="crm_edited_client_phone_input")
                with col_c_edit2:
                    edited_client_email = st.text_input("البريد الإلكتروني", value=current_client_data["email"], key="crm_edited_client_email_input")
                    edited_client_notes = st.text_area("ملاحظات", value=current_client_data["notes"], key="crm_edited_client_notes_input")
                
                col_buttons = st.columns(2)
                with col_buttons[0]:
                    update_client_button = st.form_submit_button("💾 تحديث بيانات العميل")
                with col_buttons[1]:
                    delete_client_button = st.form_submit_button("🗑️ حذف العميل")

                if update_client_button:
                    st.session_state.clients.loc[st.session_state.clients["client_id"] == client_to_edit_id, ["name", "phone", "email", "notes"]] = \
                        [edited_client_name, edited_client_phone, edited_client_email, edited_client_notes]
                    save_data_func()
                    st.success(f"✅ تم تحديث بيانات العميل: {reshape_arabic_func(edited_client_name)}.")
                    st.rerun()

                if delete_client_button:
                    if any(st.session_state.cases["client_id"] == client_to_edit_id) or \
                       any(st.session_state.invoices["client_id"] == client_to_edit_id) or \
                       any((st.session_state.reminders["related_type"] == "عميل") & (st.session_state.reminders["related_id"] == client_to_edit_id)):
                        st.warning("⚠️ لا يمكن حذف هذا العميل لوجود قضايا، فواتير أو تذكيرات مرتبطة به. يرجى حذفها أولاً.")
                    else:
                        st.session_state.clients = st.session_state.clients[st.session_state.clients["client_id"] != client_to_edit_id]
                        save_data_func()
                        st.success(f"🗑️ تم حذف العميل: {reshape_arabic_func(current_client_data['name'])}.")
                        st.rerun()
        else:
            st.info("لا توجد عملاء لعرضهم. يرجى إضافة عميل أولاً.")

# --- Case Management Functions and UI ---
def render_case_management(next_id_func, save_data_func, reshape_arabic_func):
    """Renders the UI for case management."""
    st.header("⚖️ إدارة القضايا")
    st.markdown("سجل، تتبع، وعدّل تفاصيل القضايا القانونية.")

    if st.session_state.clients.empty:
        st.warning("⚠️ لا يمكن إضافة قضايا. يرجى إضافة عميل واحد على الأقل في صفحة 'العملاء' أولاً.")
    else:
        with st.expander("➕ إضافة قضية جديدة", expanded=False):
            with st.form("add_case_form", clear_on_submit=True):
                client_names = st.session_state.clients["name"].tolist()
                selected_client_name = st.selectbox("اختر العميل المرتبط بالقضية", client_names, key="crm_case_client_select")
                client_id_for_case = st.session_state.clients[st.session_state.clients["name"] == selected_client_name]["client_id"].iloc[0]

                col_case_add1, col_case_add2 = st.columns(2)
                with col_case_add1:
                    new_case_name = st.text_input("اسم القضية / موضوعها", key="crm_new_case_name_input")
                    new_case_type = st.selectbox("نوع القضية", CASE_TYPE_OPTIONS, key="crm_new_case_type_select")
                    new_opposing_party = st.text_input("الطرف الخصم", key="crm_new_opposing_party_input")
                with col_case_add2:
                    new_case_status = st.selectbox("الحالة", CASE_STATUS_OPTIONS, key="crm_new_case_status_select")
                    new_court_date = st.date_input("تاريخ الجلسة القادمة", datetime.today() + timedelta(days=7), key="crm_new_court_date_input")
                    new_responsible_lawyer = st.text_input("المحامي المسؤول", key="crm_new_responsible_lawyer_input")

                new_case_description = st.text_area("وصف القضية", key="crm_new_case_description_input")
                new_case_notes = st.text_area("ملاحظات إضافية على القضية", key="crm_new_case_notes_input")

                submitted_case = st.form_submit_button("➕ حفظ القضية")
                if submitted_case:
                    if new_case_name:
                        cid = next_id_func(st.session_state.cases, "case_id")
                        st.session_state.cases.loc[len(st.session_state.cases)] = [cid, client_id_for_case, new_case_name, new_case_type, new_case_status, new_court_date, new_opposing_party, new_case_description, new_responsible_lawyer, new_case_notes]
                        save_data_func()
                        st.success(f"✅ تم إضافة القضية: {reshape_arabic_func(new_case_name)} بنجاح!")
                        st.rerun()
                    else:
                        st.warning("الرجاء إدخال اسم القضية.")
        
        st.markdown("---")
        st.markdown("### 📋 قائمة القضايا")
        if not st.session_state.cases.empty:
            df_cases_display = st.session_state.cases.copy()
            df_cases_display = df_cases_display.merge(st.session_state.clients[["client_id", "name"]], on="client_id", how="left", suffixes=('_case', '_client'))
            df_cases_display = df_cases_display.rename(columns={
                "name": "العميل", "case_name": "اسم القضية", "case_type": "نوع القضية", 
                "status": "الحالة", "court_date": "تاريخ الجلسة", "opposing_party": "الطرف الخصم",
                "case_description": "وصف القضية", "responsible_lawyer": "المحامي المسؤول", "notes": "ملاحظات"
            })
            
            search_case = st.text_input("ابحث عن قضية (بالاسم أو العميل أو الحالة أو الطرف الخصم)", "", key="crm_search_case_input")
            filtered_cases = df_cases_display[
                df_cases_display["اسم القضية"].astype(str).str.contains(search_case, case=False, na=False) |
                df_cases_display["العميل"].astype(str).str.contains(search_case, case=False, na=False) |
                df_cases_display["الحالة"].astype(str).str.contains(search_case, case=False, na=False) |
                df_cases_display["الطرف الخصم"].astype(str).str.contains(search_case, case=False, na=False)
            ]
            
            st.dataframe(filtered_cases[["case_id", "اسم القضية", "العميل", "نوع القضية", "الحالة", "تاريخ الجلسة", "الطرف الخصم", "المحامي المسؤول"]].set_index("case_id"))

            st.markdown("### ✏️ تعديل / حذف قضية")
            if not filtered_cases.empty:
                case_to_edit_id = st.selectbox(
                    "اختر القضية للتعديل أو الحذف", 
                    filtered_cases["case_id"].tolist(), 
                    format_func=lambda x: f"{x} - {st.session_state.cases[st.session_state.cases['case_id'] == x]['case_name'].iloc[0]}",
                    key="crm_select_case_to_edit"
                )
                current_case_data = st.session_state.cases[st.session_state.cases["case_id"] == case_to_edit_id].iloc[0]
                
                current_court_date = pd.to_datetime(current_case_data["court_date"]).date() if pd.notnull(current_case_data["court_date"]) else datetime.today().date()

                with st.form("edit_case_form"):
                    client_options = st.session_state.clients["name"].tolist()
                    current_client_name = st.session_state.clients[st.session_state.clients["client_id"] == current_case_data["client_id"]]["name"].iloc[0]
                    edited_client_name = st.selectbox("العميل المرتبط بالقضية", client_options, index=client_options.index(current_client_name), key="crm_edited_case_client_select")
                    edited_client_id_for_case = st.session_state.clients[st.session_state.clients["name"] == edited_client_name]["client_id"].iloc[0]

                    col_case_edit1, col_case_edit2 = st.columns(2)
                    with col_case_edit1:
                        edited_case_name = st.text_input("اسم القضية / موضوعها", value=current_case_data["case_name"], key="crm_edited_case_name_input")
                        edited_case_type = st.selectbox("نوع القضية", CASE_TYPE_OPTIONS, index=CASE_TYPE_OPTIONS.index(current_case_data["case_type"]), key="crm_edited_case_type_select")
                        edited_opposing_party = st.text_input("الطرف الخصم", value=current_case_data["opposing_party"], key="crm_edited_opposing_party_input")
                    with col_case_edit2:
                        edited_case_status = st.selectbox("الحالة", CASE_STATUS_OPTIONS, index=CASE_STATUS_OPTIONS.index(current_case_data["status"]), key="crm_edited_case_status_select")
                        edited_court_date = st.date_input("تاريخ الجلسة القادمة", value=current_court_date, key="crm_edited_court_date_input")
                        edited_responsible_lawyer = st.text_input("المحامي المسؤول", value=current_case_data["responsible_lawyer"], key="crm_edited_responsible_lawyer_input")

                    edited_case_description = st.text_area("وصف القضية", value=current_case_data["case_description"], key="crm_edited_case_description_input")
                    edited_case_notes = st.text_area("ملاحظات إضافية على القضية", value=current_case_data["notes"], key="crm_edited_case_notes_input")

                    col_buttons_case = st.columns(2)
                    with col_buttons_case[0]:
                        update_case_button = st.form_submit_button("💾 تحديث بيانات القضية")
                    with col_buttons_case[1]:
                        delete_case_button = st.form_submit_button("🗑️ حذف القضية")

                    if update_case_button:
                        st.session_state.cases.loc[st.session_state.cases["case_id"] == case_to_edit_id, 
                            ["client_id", "case_name", "case_type", "status", "court_date", "opposing_party", "case_description", "responsible_lawyer", "notes"]] = \
                            [edited_client_id_for_case, edited_case_name, edited_case_type, edited_case_status, edited_court_date, edited_opposing_party, edited_case_description, edited_responsible_lawyer, edited_case_notes]
                        save_data_func()
                        st.success(f"✅ تم تحديث بيانات القضية: {reshape_arabic_func(edited_case_name)}.")
                        st.rerun()

                    if delete_case_button:
                        if any(st.session_state.invoices["case_id"] == case_to_edit_id) or \
                           any((st.session_state.reminders["related_type"] == "قضية") & (st.session_state.reminders["related_id"] == case_to_edit_id)):
                            st.warning("⚠️ لا يمكن حذف هذه القضية لوجود فواتير أو تذكيرات مرتبطة بها. يرجى حذفها أولاً.")
                        else:
                            st.session_state.cases = st.session_state.cases[st.session_state.cases["case_id"] != case_to_edit_id]
                            save_data_func()
                            st.success(f"🗑️ تم حذف القضية: {reshape_arabic_func(current_case_data['case_name'])}.")
                            st.rerun()
            else:
                st.info("لا توجد قضايا لعرضها. يرجى إضافة قضية أولاً.")

# --- Reminder Management Functions and UI ---
def render_reminder_management(next_id_func, save_data_func, reshape_arabic_func):
    """Renders the UI for reminder management."""
    st.header("⏰ إدارة التذكيرات والمهام")
    st.markdown("تتبع المواعيد الهامة والتذكيرات المرتبطة بالعملاء والقضايا.")

    with st.expander("➕ إضافة تذكير جديد", expanded=False):
        with st.form("add_reminder_form", clear_on_submit=True):
            reminder_type = st.radio("الربط بـ:", REMINDER_RELATED_TYPES, key="crm_reminder_related_type_radio")
            
            related_entity_id = None
            if reminder_type == "عميل":
                if not st.session_state.clients.empty:
                    client_names = st.session_state.clients['name'].tolist()
                    selected_client_for_reminder = st.selectbox("اختر العميل", client_names, key="crm_reminder_client_select")
                    related_entity_id = st.session_state.clients[st.session_state.clients["name"] == selected_client_for_reminder]["client_id"].iloc[0]
                else:
                    st.warning("لا يوجد عملاء لربط التذكير بهم. يرجى إضافة عميل أولاً أو اختر 'قضية' أو 'عام'.")
                    related_entity_id = 0 # Indicate no valid entity selected
            elif reminder_type == "قضية":
                if not st.session_state.cases.empty:
                    case_names = st.session_state.cases['case_name'].tolist()
                    selected_case_for_reminder = st.selectbox("اختر القضية", case_names, key="crm_reminder_case_select")
                    related_entity_id = st.session_state.cases[st.session_state.cases["case_name"] == selected_case_for_reminder]["case_id"].iloc[0]
                else:
                    st.warning("لا توجد قضايا لربط التذكير بها. يرجى إضافة قضية أولاً أو اختر 'عميل' أو 'عام'.")
                    related_entity_id = 0 # Indicate no valid entity selected
            elif reminder_type == "عام":
                related_entity_id = 0 # No specific relation for general reminders

            new_reminder_description = st.text_area("وصف التذكير / المهمة", key="crm_new_reminder_description_input")
            new_reminder_date = st.date_input("تاريخ التذكير", datetime.today() + timedelta(days=1), key="crm_new_reminder_date_input")
            
            submitted_reminder = st.form_submit_button("➕ حفظ التذكير")

            if submitted_reminder:
                if new_reminder_description and (reminder_type == "عام" or related_entity_id is not None):
                    rid = next_id_func(st.session_state.reminders, "reminder_id")
                    st.session_state.reminders.loc[len(st.session_state.reminders)] = [rid, reminder_type, related_entity_id, new_reminder_description, new_reminder_date, False]
                    save_data_func()
                    st.success(f"✅ تم إضافة التذكير: {reshape_arabic_func(new_reminder_description)} بنجاح!")
                    st.rerun()
                else:
                    st.warning("الرجاء إدخال وصف التذكير واختيار الربط المناسب.")
    
    st.markdown("---")
    st.markdown("### 📋 قائمة التذكيرات")
    if not st.session_state.reminders.empty:
        df_reminders_display = st.session_state.reminders.copy()
        
        # Add related client/case name for display
        df_reminders_display['الكيان المرتبط'] = ''
        for idx, row in df_reminders_display.iterrows():
            if row['related_type'] == 'عميل' and row['related_id'] in st.session_state.clients['client_id'].values:
                df_reminders_display.loc[idx, 'الكيان المرتبط'] = st.session_state.clients[st.session_state.clients['client_id'] == row['related_id']]['name'].iloc[0]
            elif row['related_type'] == 'قضية' and row['related_id'] in st.session_state.cases['case_id'].values:
                df_reminders_display.loc[idx, 'الكيان المرتبط'] = st.session_state.cases[st.session_state.cases['case_id'] == row['related_id']]['case_name'].iloc[0]
            else:
                df_reminders_display.loc[idx, 'الكيان المرتبط'] = 'لا يوجد' # For 'عام' or if entity was deleted

        # Add 'Status' for reminders (Upcoming, Overdue, Completed)
        df_reminders_display['الحالة'] = 'مكتملة'
        df_reminders_display.loc[(df_reminders_display['is_completed'] == False) & (df_reminders_display['date'] >= datetime.today().date()), 'الحالة'] = 'قادمة'
        df_reminders_display.loc[(df_reminders_display['is_completed'] == False) & (df_reminders_display['date'] < datetime.today().date()), 'الحالة'] = 'متأخرة'

        df_reminders_display = df_reminders_display.rename(columns={
            "description": "الوصف", "date": "التاريخ", "related_type": "نوع الربط", "is_completed": "اكتمل؟"
        })
        
        st.dataframe(df_reminders_display[["reminder_id", "الوصف", "التاريخ", "الحالة", "نوع الربط", "الكيان المرتبط"]].set_index("reminder_id"))

        st.markdown("### ✏️ تعديل / حذف / إكمال تذكير")
        if not df_reminders_display.empty:
            reminder_to_edit_id = st.selectbox(
                "اختر التذكير للتعديل أو الإكمال أو الحذف", 
                df_reminders_display["reminder_id"].tolist(), 
                format_func=lambda x: f"{x} - {st.session_state.reminders[st.session_state.reminders['reminder_id'] == x]['description'].iloc[0]}",
                key="crm_select_reminder_to_edit"
            )
            current_reminder_data = st.session_state.reminders[st.session_state.reminders["reminder_id"] == reminder_to_edit_id].iloc[0]
            
            with st.form("edit_reminder_form"):
                edited_reminder_description = st.text_area("وصف التذكير / المهمة", value=current_reminder_data["description"], key="crm_edited_reminder_description_input")
                edited_reminder_date = st.date_input("تاريخ التذكير", value=current_reminder_data["date"], key="crm_edited_reminder_date_input")
                edited_is_completed = st.checkbox("تم الإكمال؟", value=current_reminder_data["is_completed"], key="crm_edited_is_completed_check")
                
                col_rem_buttons = st.columns(3)
                with col_rem_buttons[0]:
                    update_reminder_button = st.form_submit_button("💾 تحديث التذكير")
                with col_rem_buttons[1]:
                    complete_reminder_button = st.form_submit_button("✅ وضع علامة 'مكتمل'")
                with col_rem_buttons[2]:
                    delete_reminder_button = st.form_submit_button("🗑️ حذف التذكير")

                if update_reminder_button:
                    st.session_state.reminders.loc[st.session_state.reminders["reminder_id"] == reminder_to_edit_id, ["description", "date", "is_completed"]] = \
                        [edited_reminder_description, edited_reminder_date, edited_is_completed]
                    save_data_func()
                    st.success(f"✅ تم تحديث التذكير: {reshape_arabic_func(edited_reminder_description)}.")
                    st.rerun()
                
                if complete_reminder_button:
                    st.session_state.reminders.loc[st.session_state.reminders["reminder_id"] == reminder_to_edit_id, "is_completed"] = True
                    save_data_func()
                    st.success(f"✅ تم وضع علامة 'مكتمل' للتذكير: {reshape_arabic_func(current_reminder_data['description'])}.")
                    st.rerun()

                if delete_reminder_button:
                    st.session_state.reminders = st.session_state.reminders[st.session_state.reminders["reminder_id"] != reminder_to_edit_id]
                    save_data_func()
                    st.success(f"🗑️ تم حذف التذكير: {reshape_arabic_func(current_reminder_data['description'])}.")
                    st.rerun()
        else:
            st.info("لا توجد تذكيرات لعرضها. يرجى إضافة تذكير أولاً.")
    else:
        st.info("لا توجد تذكيرات لعرضها.")

# --- Invoice Management Functions and UI ---
def render_invoice_management(next_id_func, save_data_func, reshape_arabic_func):
    """Renders the UI for invoice management."""
    st.header("💰 إدارة الفواتير")
    st.markdown("سجل، تتبع، وعدّل حالة الفواتير.")

    if st.session_state.clients.empty:
        st.warning("⚠️ لا يمكن إضافة فواتير. يرجى إضافة عميل واحد على الأقل في صفحة 'العملاء' أولاً.")
    else:
        with st.expander("➕ إضافة فاتورة جديدة", expanded=False):
            with st.form("add_invoice_form", clear_on_submit=True):
                client_names_inv = st.session_state.clients["name"].tolist()
                selected_client_name_inv = st.selectbox("اختر العميل", client_names_inv, key="crm_inv_client_select")
                client_id_for_inv = st.session_state.clients[st.session_state.clients["name"] == selected_client_name_inv]["client_id"].iloc[0]

                # Option to link invoice to a case
                cases_for_client = st.session_state.cases[st.session_state.cases["client_id"] == client_id_for_inv]
                case_options = [""] + cases_for_client["case_name"].tolist() if not cases_for_client.empty else [""]
                selected_case_name_inv = st.selectbox("الربط بقضية (اختياري)", case_options, key="crm_inv_case_select")
                case_id_for_inv = None
                if selected_case_name_inv and not cases_for_client.empty:
                    case_id_for_inv = cases_for_client[cases_for_client["case_name"] == selected_case_name_inv]["case_id"].iloc[0]

                col_inv1, col_inv2 = st.columns(2)
                with col_inv1:
                    new_invoice_amount = st.number_input("المبلغ (ريال سعودي)", min_value=0.0, step=50.0, format="%.2f", key="crm_new_invoice_amount_input")
                    new_invoice_date = st.date_input("تاريخ الفاتورة", datetime.today(), key="crm_new_invoice_date_input")
                with col_inv2:
                    new_invoice_paid = st.checkbox("تم الدفع؟", key="crm_new_invoice_paid_check")
                
                submitted_invoice = st.form_submit_button("➕ حفظ الفاتورة")
                if submitted_invoice:
                    if new_invoice_amount > 0:
                        iid = next_id_func(st.session_state.invoices, "invoice_id")
                        st.session_state.invoices.loc[len(st.session_state.invoices)] = [iid, client_id_for_inv, case_id_for_inv, new_invoice_amount, new_invoice_paid, new_invoice_date]
                        save_data_func()
                        st.success(f"✅ تم إضافة فاتورة بمبلغ: {new_invoice_amount:,.2f} ر.س بنجاح!")
                        st.rerun()
                    else:
                        st.warning("الرجاء إدخال مبلغ صحيح للفاتورة.")
        
        st.markdown("---")
        st.markdown("### 📋 قائمة الفواتير")
        if not st.session_state.invoices.empty:
            df_invoices_display = st.session_state.invoices.copy()
            df_invoices_display = df_invoices_display.merge(st.session_state.clients[["client_id", "name"]], on="client_id", how="left", suffixes=('_inv', '_client'))
            
            # Add case name if linked
            if 'case_id' in df_invoices_display.columns and not st.session_state.cases.empty:
                df_invoices_display = df_invoices_display.merge(st.session_state.cases[["case_id", "case_name"]], on="case_id", how="left", suffixes=('_inv', '_case'))
            else:
                 df_invoices_display['case_name'] = None # Ensure column exists even if no cases

            df_invoices_display['الحالة'] = df_invoices_display['paid'].apply(lambda x: "مدفوعة" if x else "غير مدفوعة")
            df_invoices_display = df_invoices_display.rename(columns={
                "name": "العميل", "case_name": "القضية المرتبطة", "amount": "المبلغ", "date": "التاريخ"
            })

            # Filter by payment status
            payment_filter = st.selectbox("تصفية حسب حالة الدفع", PAYMENT_STATUS_OPTIONS, key="crm_invoice_payment_filter")
            if payment_filter == "مدفوعة":
                filtered_invoices = df_invoices_display[df_invoices_display['الحالة'] == "مدفوعة"]
            elif payment_filter == "غير مدفوعة":
                filtered_invoices = df_invoices_display[df_invoices_display['الحالة'] == "غير مدفوعة"]
            else:
                filtered_invoices = df_invoices_display
            
            st.dataframe(filtered_invoices[["invoice_id", "العميل", "القضية المرتبطة", "المبلغ", "التاريخ", "الحالة"]].set_index("invoice_id"))

            st.markdown("### ✏️ تعديل / حذف فاتورة")
            if not filtered_invoices.empty:
                invoice_to_edit_id = st.selectbox(
                    "اختر الفاتورة للتعديل أو الحذف", 
                    filtered_invoices["invoice_id"].tolist(), 
                    format_func=lambda x: f"{x} - {st.session_state.invoices[st.session_state.invoices['invoice_id'] == x]['amount'].iloc[0]} ر.س",
                    key="crm_select_invoice_to_edit"
                )
                current_invoice_data = st.session_state.invoices[st.session_state.invoices["invoice_id"] == invoice_to_edit_id].iloc[0]

                with st.form("edit_invoice_form"):
                    edited_invoice_amount = st.number_input("المبلغ (ريال سعودي)", value=float(current_invoice_data["amount"]), min_value=0.0, step=50.0, format="%.2f", key="crm_edited_invoice_amount_input")
                    edited_invoice_date = st.date_input("تاريخ الفاتورة", value=current_invoice_data["date"], key="crm_edited_invoice_date_input")
                    edited_invoice_paid = st.checkbox("تم الدفع؟", value=current_invoice_data["paid"], key="crm_edited_invoice_paid_check")

                    col_inv_buttons = st.columns(2)
                    with col_inv_buttons[0]:
                        update_invoice_button = st.form_submit_button("💾 تحديث الفاتورة")
                    with col_inv_buttons[1]:
                        delete_invoice_button = st.form_submit_button("🗑️ حذف الفاتورة")

                    if update_invoice_button:
                        st.session_state.invoices.loc[st.session_state.invoices["invoice_id"] == invoice_to_edit_id, ["amount", "paid", "date"]] = \
                            [edited_invoice_amount, edited_invoice_paid, edited_invoice_date]
                        save_data_func()
                        st.success(f"✅ تم تحديث الفاتورة رقم {invoice_to_edit_id}.")
                        st.rerun()

                    if delete_invoice_button:
                        st.session_state.invoices = st.session_state.invoices[st.session_state.invoices["invoice_id"] != invoice_to_edit_id]
                        save_data_func()
                        st.success(f"🗑️ تم حذف الفاتورة رقم {invoice_to_edit_id}.")
                        st.rerun()
            else:
                st.info("لا توجد فواتير لعرضها. يرجى إضافة فاتورة أولاً.")
        else:
            st.info("لا توجد فواتير لعرضها.")
