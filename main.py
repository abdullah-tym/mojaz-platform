import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import base64 # Needed for PDF display
from streamlit_drawable_canvas import st_canvas # CORRECTED: Import st_canvas

# Import modular components
from config import DATA_FILE, AMIRI_FONT_NAME, AMIRI_FONT_PATH, CONTRACT_TYPE_OPTIONS
from data_persistence import load_data, save_data
from pdf_utils import generate_contract_pdf, reshape_arabic, get_font_path
from crm_modules import (
    render_client_management,
    render_case_management,
    render_reminder_management,
    render_invoice_management
)
from styles import custom_css # Import the CSS string

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Mojaz Platform - Legal & Contract Management",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://www.google.com/',
        'Report a bug': "https://www.google.com/",
        'About': "# Mojaz Platform. This is a legal and contract management app."
    }
)

# Apply custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# --- Initialize Session State and Load Data ---
# This function is defined in data_persistence.py and loads data into st.session_state
load_data()

# --- Helper for ID Generation (could be in utils.py if more general) ---
def next_id(df, col):
    """Generates the next sequential ID for a DataFrame."""
    if df.empty:
        return 1
    return df[col].max() + 1

# --- Main Application Layout ---
st.title("🧑‍⚖️ موجز - إدارة العقود والمحاماة")

# --- Dashboard KPIs ---
st.markdown("---")
st.header("📊 لوحة المعلومات")
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4) # Added one more column for KPI
with col_kpi1:
    st.markdown(f'<div class="kpi-box">إجمالي العملاء<br><strong>{len(st.session_state.clients)}</strong></div>', unsafe_allow_html=True)
with col_kpi2:
    st.markdown(f'<div class="kpi-box">إجمالي القضايا<br><strong>{len(st.session_state.cases)}</strong></div>', unsafe_allow_html=True)
with col_kpi3:
    total_invoiced = st.session_state.invoices["amount"].sum() if not st.session_state.invoices.empty else 0
    total_paid = st.session_state.invoices[st.session_state.invoices["paid"]]["amount"].sum() if not st.session_state.invoices.empty else 0
    st.markdown(f'<div class="kpi-box">المبالغ المحصلة<br><strong>{total_paid:,.2f} ر.س</strong></div>', unsafe_allow_html=True)
with col_kpi4:
    # Calculate upcoming reminders
    upcoming_reminders_count = st.session_state.reminders[
        (st.session_state.reminders['date'] >= datetime.today().date()) &
        (st.session_state.reminders['is_completed'] == False)
    ].shape[0]
    st.markdown(f'<div class="kpi-box">تذكيرات قادمة<br><strong>{upcoming_reminders_count}</strong></div>', unsafe_allow_html=True)
st.markdown("---")

# --- Main Tabs for Application Modules ---
tab1, tab2 = st.tabs(["📄 مولد العقود (MojazContracts)", "⚖️ نظام إدارة القضايا (MojazLegalCRM)"])

with tab1:
    st.subheader("📄 مولد العقود القانونية")
    st.markdown("استخدم هذه الأداة لإنشاء عقود قانونية مخصصة بسرعة وسهولة.")

    selected_contract_type_ar = st.selectbox("اختر نوع العقد", list(CONTRACT_TYPE_OPTIONS.keys()), key="main_contract_type_select")
    
    with st.form("contract_generation_form", clear_on_submit=False):
        st.markdown("### 📌 بيانات الأطراف")
        col1, col2 = st.columns(2)
        with col1:
            party1_name = st.text_input("اسم الطرف الأول", help="الجهة الأولى في العقد (مثلاً: الشركة المؤجرة، صاحب العمل).", key="main_party1_name_contract")
            party2_name = st.text_input("اسم الطرف الثاني", help="الجهة الثانية في العقد (مثلاً: المستأجر، الموظف).", key="main_party2_name_contract")
        with col2:
            contract_date = st.date_input("تاريخ العقد", datetime.today(), key="main_contract_date_input")

        contract_details = {}
        if selected_contract_type_ar == "عقد عمل":
            st.markdown("### 📝 تفاصيل عقد العمل")
            col_emp1, col_emp2 = st.columns(2)
            with col_emp1:
                contract_details["cr_number"] = st.text_input("السجل التجاري للطرف الأول", key="main_emp_cr_number")
                contract_details["id_number"] = st.text_input("رقم هوية الطرف الثاني / الإقامة", key="main_emp_id_number")
                contract_details["salary"] = st.number_input("الراتب الشهري (بالريال السعودي)", min_value=0.0, step=100.0, format="%.2f", key="main_emp_salary")
                contract_details["job_title"] = st.text_input("المسمى الوظيفي", key="main_emp_job_title")
                contract_details["start_date"] = st.date_input("تاريخ بدء العمل", datetime.today(), key="main_emp_start_date")
            with col_emp2:
                contract_details["address"] = st.text_input("عنوان الطرف الأول", key="main_emp_address")
                contract_details["duration"] = st.number_input("مدة العقد (بالأشهر)", min_value=1, step=1, key="main_emp_duration")
                contract_details["housing_allowance"] = st.checkbox("يشمل بدل سكن؟", key="main_emp_housing_allowance_check")
                if contract_details["housing_allowance"]:
                    contract_details["housing_percentage"] = st.slider("نسبة بدل السكن (%)", 0, 50, 25, key="main_emp_housing_percentage")
                contract_details["non_compete"] = st.checkbox("إضافة شرط عدم المنافسة؟", key="main_emp_non_compete_check")
                if contract_details["non_compete"]:
                    contract_details["non_compete_city"] = st.text_input("المدينة المشمولة بالشرط", key="main_emp_non_compete_city")
                contract_details["penalty_clause"] = st.checkbox("إضافة شرط جزائي؟", key="main_emp_penalty_clause_check")
                if contract_details["penalty_clause"]:
                    contract_details["penalty_amount"] = st.number_input("قيمة الشرط الجزائي (ريال)", min_value=0.0, step=100.0, format="%.2f", key="main_emp_penalty_amount")
                contract_details["termination_clause"] = st.checkbox("إمكانية فسخ العقد بإشعار مسبق؟", key="main_emp_termination_clause_check")

        elif selected_contract_type_ar == "عقد إيجار":
            st.markdown("### 📝 تفاصيل عقد الإيجار")
            contract_details["property_address"] = st.text_area("عنوان العقار المؤجر بالتفصيل", key="main_lease_property_address")
            col_lease1, col_lease2 = st.columns(2)
            with col_lease1:
                contract_details["duration"] = st.number_input("مدة الإيجار (بالأشهر)", min_value=1, step=1, key="main_lease_duration")
                contract_details["rent"] = st.number_input("قيمة الإيجار الشهري (ريال)", min_value=0.0, step=100.0, format="%.2f", key="main_lease_rent")
            with col_lease2:
                contract_details["deposit"] = st.number_input("قيمة التأمين (إن وجد) (ريال)", min_value=0.0, step=50.0, format="%.2f", key="main_lease_deposit")
                contract_details["maintenance"] = st.checkbox("هل المؤجر مسؤول عن الصيانة الرئيسية؟", key="main_lease_maintenance_check")

        elif selected_contract_type_ar == "عقد وكالة":
            st.markdown("### 📝 تفاصيل عقد الوكالة")
            contract_details["agency_scope"] = st.text_area("نطاق ومسؤوليات الوكالة بالتفصيل", key="main_agency_scope")
            contract_details["duration"] = st.number_input("مدة الوكالة (بالأشهر)", min_value=1, step=1, key="main_agency_duration")

        elif selected_contract_type_ar == "عقد بيع":
            st.markdown("### 📝 تفاصيل عقد البيع")
            contract_details["item_description"] = st.text_area("وصف الأصل أو الممتلكات المباعة بالتفصيل", key="main_sales_item_description")
            col_sales1, col_sales2 = st.columns(2)
            with col_sales1:
                contract_details["price"] = st.number_input("قيمة البيع الإجمالية (ريال)", min_value=0.0, step=100.0, format="%.2f", key="main_sales_price")
            with col_sales2:
                contract_details["delivery_date"] = st.date_input("تاريخ التسليم المتوقع", datetime.today(), key="main_sales_delivery_date")

        elif selected_contract_type_ar == "عقد عدم إفشاء (NDA)":
            st.markdown("### 📝 تفاصيل عقد عدم الإفشاء (NDA)")
            contract_details["scope"] = st.text_area("طبيعة ونطاق المعلومات السرية المشمولة بالعقد", key="main_nda_scope")
            contract_details["duration"] = st.number_input("مدة الالتزام بالسرية (بالأشهر)", min_value=1, step=1, key="main_nda_duration")

        st.markdown("---")
        st.markdown("### ✍️ التوقيع والختم")
        col_sig, col_stamp = st.columns(2)
        with col_sig:
            st.markdown('<div class="signature-container">', unsafe_allow_html=True)
            st.markdown('<p class="label-bold">ارسم توقيعك هنا:</p>', unsafe_allow_html=True)
            signature_data = st_canvas( # CORRECTED: Changed from st.canvas to st_canvas
                fill_color="rgba(255, 165, 0, 0.3)",
                stroke_width=2,
                stroke_color="#000000",
                background_color="#ffffff",
                height=150,
                # width=300, # Removed width as requested
                drawing_mode="freedraw",
                key=f"canvas_signature_main_contract_{selected_contract_type_ar}", # Unique key for this tab
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_stamp:
            st.markdown('<div class="stamp-container">', unsafe_allow_html=True)
            st.markdown('<p class="label-bold">رفع صورة ختم الشركة (PNG):</p>', unsafe_allow_html=True)
            company_stamp_file = st.file_uploader("🖼️ رفع ختم", type=["png"], key=f"uploader_stamp_main_contract_{selected_contract_type_ar}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📤 خيارات الإرسال والمشاركة")
        col_share1, col_share2 = st.columns(2)
        with col_share1:
            send_whatsapp_check = st.checkbox("إرسال عبر واتساب", key="main_whatsapp_check")
            whatsapp_num = st.text_input("رقم الجوال (مثال: 9665xxxxxxxx)", max_chars=12, help="يرجى إدخال الرقم بدون رمز الدولة المسبوق بـ '+'", key="main_whatsapp_input") if send_whatsapp_check else ""
        with col_share2:
            send_email_check = st.checkbox("إرسال عبر البريد الإلكتروني", key="main_email_check")
            email_addr = st.text_input("البريد الإلكتروني", help="أدخل البريد الإلكتروني للمستلم", key="main_email_input") if send_email_check else ""

        generate_button = st.form_submit_button("✨ توليد العقد والتحميل")

    if generate_button:
        if not party1_name or not party2_name:
            st.warning("الرجاء إدخال اسمي الطرف الأول والثاني للمتابعة.")
        else:
            contract_data_for_pdf = {
                "party1": party1_name,
                "party2": party2_name,
                "date": contract_date, # Pass as date object to PDF function
                **contract_details
            }
            
            signature_image_array = None
            if signature_data and signature_data.image_data is not None:
                # Check if the drawn canvas is mostly white (empty)
                if signature_data.image_data.sum() < (signature_data.image_data.size * 255 * 3) * 0.98:
                    signature_image_array = signature_data.image_data
                else:
                    st.info("لم يتم اكتشاف توقيع واضح. سيتم إنشاء العقد بدون توقيع.")


            stamp_image_bytes = None
            if company_stamp_file:
                stamp_image_bytes = company_stamp_file # Pass the file object directly

            try:
                pdf_bytes_output = generate_contract_pdf(
                    selected_contract_type_ar,
                    contract_data_for_pdf,
                    signature_img_data=signature_image_array,
                    stamp_file_data=stamp_image_bytes
                )
                
                st.success("✅ تم إنشاء العقد بنجاح! يمكنك معاينته أو تحميله أدناه.")
                
                st.markdown("### 📄 معاينة العقد")
                base64_pdf = base64.b64encode(pdf_bytes_output).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                
                st.download_button(
                    label="📥 تحميل العقد كملف PDF",
                    data=pdf_bytes_output,
                    file_name=f"{selected_contract_type_ar}_{party1_name}_vs_{party2_name}.pdf",
                    mime="application/pdf"
                )

                if send_whatsapp_check and whatsapp_num:
                    full_whatsapp_num = whatsapp_num if whatsapp_num.startswith("966") else "966" + whatsapp_num
                    wa_message = reshape_arabic(f"تم إنشاء عقد {selected_contract_type_ar} بين {party1_name} و {party2_name} بتاريخ {contract_date.strftime('%Y-%m-%d')}. تجده مرفقاً.")
                    wa_url = f"https://wa.me/{full_whatsapp_num}?text={wa_message}"
                    st.markdown(f"[📲 إرسال إشعار عبر واتساب]({wa_url})", unsafe_allow_html=True)
                    st.info("⚠️ ملاحظة: يتطلب الإرسال عبر واتساب أن يكون المستلم قد حفظ رقمك أو الموافقة على فتح الدردشة.")

                if send_email_check and email_addr:
                    st.info(f"📧 تم تجهيز العقد للإرسال إلى: {email_addr}. (ميزة الإرسال المباشر عبر البريد الإلكتروني تتطلب تكاملاً خارجياً)")

            except Exception as e:
                st.error(f"حدث خطأ أثناء توليد العقد: {e}")
                st.exception(e) # Display full traceback for debugging (can be commented out in production)


# --- CRM Tab (Delegated to crm_modules.py) ---
with tab2:
    st.subheader("⚖️ نظام إدارة القضايا والعملاء (CRM)")
    st.markdown("نظام متكامل لإدارة بيانات العملاء، القضايا، التذكيرات، والفواتير المرتبطة.")

    # Render CRM modules using functions from crm_modules.py
    clients_tab, cases_tab, reminders_tab, invoices_tab = st.tabs(["👥 العملاء", "⚖️ القضايا", "⏰ التذكيرات", "💰 الفواتير"])

    with clients_tab:
        render_client_management(next_id, save_data, reshape_arabic)
    
    with cases_tab:
        render_case_management(next_id, save_data, reshape_arabic)

    with reminders_tab:
        render_reminder_management(next_id, save_data, reshape_arabic)

    with invoices_tab:
        render_invoice_management(next_id, save_data, reshape_arabic)

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import base64 # Needed for PDF display
from streamlit_drawable_canvas import st_canvas # CORRECTED: Import st_canvas

# Import modular components
from config import DATA_FILE, AMIRI_FONT_NAME, AMIRI_FONT_PATH, CONTRACT_TYPE_OPTIONS
from data_persistence import load_data, save_data
from pdf_utils import generate_contract_pdf, reshape_arabic, get_font_path
from crm_modules import (
    render_client_management,
    render_case_management,
    render_reminder_management,
    render_invoice_management
)
from styles import custom_css # Import the CSS string

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Mojaz Platform - Legal & Contract Management",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://www.google.com/',
        'Report a bug': "https://www.google.com/",
        'About': "# Mojaz Platform. This is a legal and contract management app."
    }
)

# Apply custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# --- Initialize Session State and Load Data ---
# This function is defined in data_persistence.py and loads data into st.session_state
load_data()

# --- Helper for ID Generation (could be in utils.py if more general) ---
def next_id(df, col):
    """Generates the next sequential ID for a DataFrame."""
    if df.empty:
        return 1
    return df[col].max() + 1

# --- Main Application Layout ---
st.title("🧑‍⚖️ موجز - إدارة العقود والمحاماة")

# --- Dashboard KPIs ---
st.markdown("---")
st.header("📊 لوحة المعلومات")
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4) # Added one more column for KPI
with col_kpi1:
    st.markdown(f'<div class="kpi-box">إجمالي العملاء<br><strong>{len(st.session_state.clients)}</strong></div>', unsafe_allow_html=True)
with col_kpi2:
    st.markdown(f'<div class="kpi-box">إجمالي القضايا<br><strong>{len(st.session_state.cases)}</strong></div>', unsafe_allow_html=True)
with col_kpi3:
    total_invoiced = st.session_state.invoices["amount"].sum() if not st.session_state.invoices.empty else 0
    total_paid = st.session_state.invoices[st.session_state.invoices["paid"]]["amount"].sum() if not st.session_state.invoices.empty else 0
    st.markdown(f'<div class="kpi-box">المبالغ المحصلة<br><strong>{total_paid:,.2f} ر.س</strong></div>', unsafe_allow_html=True)
with col_kpi4:
    # Calculate upcoming reminders
    upcoming_reminders_count = st.session_state.reminders[
        (st.session_state.reminders['date'] >= datetime.today().date()) &
        (st.session_state.reminders['is_completed'] == False)
    ].shape[0]
    st.markdown(f'<div class="kpi-box">تذكيرات قادمة<br><strong>{upcoming_reminders_count}</strong></div>', unsafe_allow_html=True)
st.markdown("---")

# --- Main Tabs for Application Modules ---
tab1, tab2 = st.tabs(["📄 مولد العقود (MojazContracts)", "⚖️ نظام إدارة القضايا (MojazLegalCRM)"])

with tab1:
    st.subheader("📄 مولد العقود القانونية")
    st.markdown("استخدم هذه الأداة لإنشاء عقود قانونية مخصصة بسرعة وسهولة.")

    selected_contract_type_ar = st.selectbox("اختر نوع العقد", list(CONTRACT_TYPE_OPTIONS.keys()), key="main_contract_type_select")
    
    with st.form("contract_generation_form", clear_on_submit=False):
        st.markdown("### 📌 بيانات الأطراف")
        col1, col2 = st.columns(2)
        with col1:
            party1_name = st.text_input("اسم الطرف الأول", help="الجهة الأولى في العقد (مثلاً: الشركة المؤجرة، صاحب العمل).", key="main_party1_name_contract")
            party2_name = st.text_input("اسم الطرف الثاني", help="الجهة الثانية في العقد (مثلاً: المستأجر، الموظف).", key="main_party2_name_contract")
        with col2:
            contract_date = st.date_input("تاريخ العقد", datetime.today(), key="main_contract_date_input")

        contract_details = {}
        if selected_contract_type_ar == "عقد عمل":
            st.markdown("### 📝 تفاصيل عقد العمل")
            col_emp1, col_emp2 = st.columns(2)
            with col_emp1:
                contract_details["cr_number"] = st.text_input("السجل التجاري للطرف الأول", key="main_emp_cr_number")
                contract_details["id_number"] = st.text_input("رقم هوية الطرف الثاني / الإقامة", key="main_emp_id_number")
                contract_details["salary"] = st.number_input("الراتب الشهري (بالريال السعودي)", min_value=0.0, step=100.0, format="%.2f", key="main_emp_salary")
                contract_details["job_title"] = st.text_input("المسمى الوظيفي", key="main_emp_job_title")
                contract_details["start_date"] = st.date_input("تاريخ بدء العمل", datetime.today(), key="main_emp_start_date")
            with col_emp2:
                contract_details["address"] = st.text_input("عنوان الطرف الأول", key="main_emp_address")
                contract_details["duration"] = st.number_input("مدة العقد (بالأشهر)", min_value=1, step=1, key="main_emp_duration")
                contract_details["housing_allowance"] = st.checkbox("يشمل بدل سكن؟", key="main_emp_housing_allowance_check")
                if contract_details["housing_allowance"]:
                    contract_details["housing_percentage"] = st.slider("نسبة بدل السكن (%)", 0, 50, 25, key="main_emp_housing_percentage")
                contract_details["non_compete"] = st.checkbox("إضافة شرط عدم المنافسة؟", key="main_emp_non_compete_check")
                if contract_details["non_compete"]:
                    contract_details["non_compete_city"] = st.text_input("المدينة المشمولة بالشرط", key="main_emp_non_compete_city")
                contract_details["penalty_clause"] = st.checkbox("إضافة شرط جزائي؟", key="main_emp_penalty_clause_check")
                if contract_details["penalty_clause"]:
                    contract_details["penalty_amount"] = st.number_input("قيمة الشرط الجزائي (ريال)", min_value=0.0, step=100.0, format="%.2f", key="main_emp_penalty_amount")
                contract_details["termination_clause"] = st.checkbox("إمكانية فسخ العقد بإشعار مسبق؟", key="main_emp_termination_clause_check")

        elif selected_contract_type_ar == "عقد إيجار":
            st.markdown("### 📝 تفاصيل عقد الإيجار")
            contract_details["property_address"] = st.text_area("عنوان العقار المؤجر بالتفصيل", key="main_lease_property_address")
            col_lease1, col_lease2 = st.columns(2)
            with col_lease1:
                contract_details["duration"] = st.number_input("مدة الإيجار (بالأشهر)", min_value=1, step=1, key="main_lease_duration")
                contract_details["rent"] = st.number_input("قيمة الإيجار الشهري (ريال)", min_value=0.0, step=100.0, format="%.2f", key="main_lease_rent")
            with col_lease2:
                contract_details["deposit"] = st.number_input("قيمة التأمين (إن وجد) (ريال)", min_value=0.0, step=50.0, format="%.2f", key="main_lease_deposit")
                contract_details["maintenance"] = st.checkbox("هل المؤجر مسؤول عن الصيانة الرئيسية؟", key="main_lease_maintenance_check")

        elif selected_contract_type_ar == "عقد وكالة":
            st.markdown("### 📝 تفاصيل عقد الوكالة")
            contract_details["agency_scope"] = st.text_area("نطاق ومسؤوليات الوكالة بالتفصيل", key="main_agency_scope")
            contract_details["duration"] = st.number_input("مدة الوكالة (بالأشهر)", min_value=1, step=1, key="main_agency_duration")

        elif selected_contract_type_ar == "عقد بيع":
            st.markdown("### 📝 تفاصيل عقد البيع")
            contract_details["item_description"] = st.text_area("وصف الأصل أو الممتلكات المباعة بالتفصيل", key="main_sales_item_description")
            col_sales1, col_sales2 = st.columns(2)
            with col_sales1:
                contract_details["price"] = st.number_input("قيمة البيع الإجمالية (ريال)", min_value=0.0, step=100.0, format="%.2f", key="main_sales_price")
            with col_sales2:
                contract_details["delivery_date"] = st.date_input("تاريخ التسليم المتوقع", datetime.today(), key="main_sales_delivery_date")

        elif selected_contract_type_ar == "عقد عدم إفشاء (NDA)":
            st.markdown("### 📝 تفاصيل عقد عدم الإفشاء (NDA)")
            contract_details["scope"] = st.text_area("طبيعة ونطاق المعلومات السرية المشمولة بالعقد", key="main_nda_scope")
            contract_details["duration"] = st.number_input("مدة الالتزام بالسرية (بالأشهر)", min_value=1, step=1, key="main_nda_duration")

        st.markdown("---")
        st.markdown("### ✍️ التوقيع والختم")
        col_sig, col_stamp = st.columns(2)
        with col_sig:
            st.markdown('<div class="signature-container">', unsafe_allow_html=True)
            st.markdown('<p class="label-bold">ارسم توقيعك هنا:</p>', unsafe_allow_html=True)
            signature_data = st_canvas( # CORRECTED: Changed from st.canvas to st_canvas
                fill_color="rgba(255, 165, 0, 0.3)",
                stroke_width=2,
                stroke_color="#000000",
                background_color="#ffffff",
                height=150,
                # width=300, # Removed width as requested
                drawing_mode="freedraw",
                key=f"canvas_signature_main_contract_{selected_contract_type_ar}", # Unique key for this tab
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_stamp:
            st.markdown('<div class="stamp-container">', unsafe_allow_html=True)
            st.markdown('<p class="label-bold">رفع صورة ختم الشركة (PNG):</p>', unsafe_allow_html=True)
            company_stamp_file = st.file_uploader("🖼️ رفع ختم", type=["png"], key=f"uploader_stamp_main_contract_{selected_contract_type_ar}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📤 خيارات الإرسال والمشاركة")
        col_share1, col_share2 = st.columns(2)
        with col_share1:
            send_whatsapp_check = st.checkbox("إرسال عبر واتساب", key="main_whatsapp_check")
            whatsapp_num = st.text_input("رقم الجوال (مثال: 9665xxxxxxxx)", max_chars=12, help="يرجى إدخال الرقم بدون رمز الدولة المسبوق بـ '+'", key="main_whatsapp_input") if send_whatsapp_check else ""
        with col_share2:
            send_email_check = st.checkbox("إرسال عبر البريد الإلكتروني", key="main_email_check")
            email_addr = st.text_input("البريد الإلكتروني", help="أدخل البريد الإلكتروني للمستلم", key="main_email_input") if send_email_check else ""

        generate_button = st.form_submit_button("✨ توليد العقد والتحميل")

    if generate_button:
        if not party1_name or not party2_name:
            st.warning("الرجاء إدخال اسمي الطرف الأول والثاني للمتابعة.")
        else:
            contract_data_for_pdf = {
                "party1": party1_name,
                "party2": party2_name,
                "date": contract_date, # Pass as date object to PDF function
                **contract_details
            }
            
            signature_image_array = None
            if signature_data and signature_data.image_data is not None:
                # Check if the drawn canvas is mostly white (empty)
                if signature_data.image_data.sum() < (signature_data.image_data.size * 255 * 3) * 0.98:
                    signature_image_array = signature_data.image_data
                else:
                    st.info("لم يتم اكتشاف توقيع واضح. سيتم إنشاء العقد بدون توقيع.")


            stamp_image_bytes = None
            if company_stamp_file:
                stamp_image_bytes = company_stamp_file # Pass the file object directly

            try:
                pdf_bytes_output = generate_contract_pdf(
                    selected_contract_type_ar,
                    contract_data_for_pdf,
                    signature_img_data=signature_image_array,
                    stamp_file_data=stamp_image_bytes
                )
                
                st.success("✅ تم إنشاء العقد بنجاح! يمكنك معاينته أو تحميله أدناه.")
                
                st.markdown("### 📄 معاينة العقد")
                base64_pdf = base64.b64encode(pdf_bytes_output).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                
                st.download_button(
                    label="📥 تحميل العقد كملف PDF",
                    data=pdf_bytes_output,
                    file_name=f"{selected_contract_type_ar}_{party1_name}_vs_{party2_name}.pdf",
                    mime="application/pdf"
                )

                if send_whatsapp_check and whatsapp_num:
                    full_whatsapp_num = whatsapp_num if whatsapp_num.startswith("966") else "966" + whatsapp_num
                    wa_message = reshape_arabic(f"تم إنشاء عقد {selected_contract_type_ar} بين {party1_name} و {party2_name} بتاريخ {contract_date.strftime('%Y-%m-%d')}. تجده مرفقاً.")
                    wa_url = f"https://wa.me/{full_whatsapp_num}?text={wa_message}"
                    st.markdown(f"[📲 إرسال إشعار عبر واتساب]({wa_url})", unsafe_allow_html=True)
                    st.info("⚠️ ملاحظة: يتطلب الإرسال عبر واتساب أن يكون المستلم قد حفظ رقمك أو الموافقة على فتح الدردشة.")

                if send_email_check and email_addr:
                    st.info(f"📧 تم تجهيز العقد للإرسال إلى: {email_addr}. (ميزة الإرسال المباشر عبر البريد الإلكتروني تتطلب تكاملاً خارجياً)")

            except Exception as e:
                st.error(f"حدث خطأ أثناء توليد العقد: {e}")
                st.exception(e) # Display full traceback for debugging (can be commented out in production)


# --- CRM Tab (Delegated to crm_modules.py) ---
with tab2:
    st.subheader("⚖️ نظام إدارة القضايا والعملاء (CRM)")
    st.markdown("نظام متكامل لإدارة بيانات العملاء، القضايا، التذكيرات، والفواتير المرتبطة.")

    # Render CRM modules using functions from crm_modules.py
    clients_tab, cases_tab, reminders_tab, invoices_tab = st.tabs(["👥 العملاء", "⚖️ القضايا", "⏰ التذكيرات", "💰 الفواتير"])

    with clients_tab:
        render_client_management(next_id, save_data, reshape_arabic)
    
    with cases_tab:
        render_case_management(next_id, save_data, reshape_arabic)

    with reminders_tab:
        render_reminder_management(next_id, save_data, reshape_arabic)

    with invoices_tab:
        render_invoice_management(next_id, save_data, reshape_arabic)
