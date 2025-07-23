import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import base64
from streamlit_drawable_canvas import st_canvas
import plotly.express as px # For charts

# Import modular components
from config import DATA_FILE, AMIRI_FONT_NAME, AMIRI_FONT_PATH, CONTRACT_TYPE_OPTIONS, CASE_STATUS_OPTIONS
from data_persistence import load_data, save_data
from pdf_utils import generate_contract_pdf, reshape_arabic, get_font_path
from crm_modules import (
    render_client_management,
    render_case_management,
    render_reminder_management,
    render_invoice_management
)
from styles import custom_css
from auth import authenticate_user # Import authentication function

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
load_data()

# --- Helper for ID Generation ---
def next_id(df, col):
    """Generates the next sequential ID for a DataFrame."""
    if df.empty:
        return 1
    return df[col].max() + 1

# --- Authentication Check ---
if not authenticate_user():
    st.stop() # Stop execution if user is not authenticated

# --- Main Application Layout (visible only after authentication) ---
st.title("🧑‍⚖️ موجز - إدارة العقود والمحاماة")

# --- Dashboard KPIs & Charts ---
st.markdown("---")
st.header("📊 لوحة المعلومات")

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
with col_kpi1:
    st.markdown(f'<div class="kpi-box">إجمالي العملاء<br><strong>{len(st.session_state.clients)}</strong></div>', unsafe_allow_html=True)
with col_kpi2:
    st.markdown(f'<div class="kpi-box">إجمالي القضايا<br><strong>{len(st.session_state.cases)}</strong></div>', unsafe_allow_html=True)
with col_kpi3:
    total_invoiced = st.session_state.invoices["amount"].sum() if not st.session_state.invoices.empty else 0
    total_paid = st.session_state.invoices[st.session_state.invoices["paid"]]["amount"].sum() if not st.session_state.invoices.empty else 0
    st.markdown(f'<div class="kpi-box">المبالغ المحصلة<br><strong>{total_paid:,.2f} ر.س</strong></div>', unsafe_allow_html=True)
with col_kpi4:
    upcoming_reminders_count = st.session_state.reminders[
        (st.session_state.reminders['date'] >= datetime.today().date()) &
        (st.session_state.reminders['is_completed'] == False)
    ].shape[0]
    st.markdown(f'<div class="kpi-box">تذكيرات قادمة<br><strong>{upcoming_reminders_count}</strong></div>', unsafe_allow_html=True)
st.markdown("---")

# --- Dashboard Charts ---
st.subheader("📈 نظرة عامة بيانية")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("#### توزيع القضايا حسب الحالة")
    if not st.session_state.cases.empty:
        case_status_counts = st.session_state.cases['status'].value_counts().reset_index()
        case_status_counts.columns = ['الحالة', 'العدد']
        fig_cases_status = px.pie(case_status_counts, values='العدد', names='الحالة', title='توزيع القضايا',
                                  color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_cases_status.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_cases_status, use_container_width=True)
    else:
        st.info("لا توجد قضايا لعرض الرسوم البيانية.")

with chart_col2:
    st.markdown("#### حالة الفواتير")
    if not st.session_state.invoices.empty:
        invoice_status_counts = st.session_state.invoices['paid'].value_counts().reset_index()
        invoice_status_counts.columns = ['Paid', 'Count']
        invoice_status_counts['Paid'] = invoice_status_counts['Paid'].map({True: 'مدفوعة', False: 'غير مدفوعة'})
        fig_invoices_status = px.bar(invoice_status_counts, x='Paid', y='Count', title='حالة الفواتير',
                                     color='Paid', color_discrete_map={'مدفوعة': '#28a745', 'غير مدفوعة': '#dc3545'})
        st.plotly_chart(fig_invoices_status, use_container_width=True)
    else:
        st.info("لا توجد فواتير لعرض الرسوم البيانية.")

st.markdown("---")

# --- Main Tabs for Application Modules ---
tab1, tab2, tab3 = st.tabs(["📄 مولد العقود (MojazContracts)", "⚖️ نظام إدارة القضايا (MojazLegalCRM)", "🧠 الذكاء الاصطناعي (AI Insights)"])

with tab1:
    st.subheader("📄 مولد العقود القانونية")
    st.markdown("استخدم هذه الأداة لإنشاء عقود قانونية مخصصة بسرعة وسهولة.")

    selected_contract_type_ar = st.selectbox("اختر نوع العقد", list(CONTRACT_TYPE_OPTIONS.keys()), key="tab1_contract_type_select")
    
    with st.form("contract_generation_form", clear_on_submit=False):
        st.markdown("### 📌 بيانات الأطراف")
        col1, col2 = st.columns(2)
        with col1:
            party1_name = st.text_input("اسم الطرف الأول", help="الجهة الأولى في العقد (مثلاً: الشركة المؤجرة، صاحب العمل).", key="tab1_party1_name_contract")
            party2_name = st.text_input("اسم الطرف الثاني", help="الجهة الثانية في العقد (مثلاً: المستأجر، الموظف).", key="tab1_party2_name_contract")
        with col2:
            contract_date = st.date_input("تاريخ العقد", datetime.today(), key="tab1_contract_date_input")

        contract_details = {}
        if selected_contract_type_ar == "عقد عمل":
            st.markdown("### 📝 تفاصيل عقد العمل")
            col_emp1, col_emp2 = st.columns(2)
            with col_emp1:
                contract_details["cr_number"] = st.text_input("السجل التجاري للطرف الأول", key="tab1_emp_cr_number")
                contract_details["id_number"] = st.text_input("رقم هوية الطرف الثاني / الإقامة", key="tab1_emp_id_number")
                contract_details["salary"] = st.number_input("الراتب الشهري (بالريال السعودي)", min_value=0.0, step=100.0, format="%.2f", key="tab1_emp_salary")
                contract_details["job_title"] = st.text_input("المسمى الوظيفي", key="tab1_emp_job_title")
                contract_details["start_date"] = st.date_input("تاريخ بدء العمل", datetime.today(), key="tab1_emp_start_date")
            with col_emp2:
                contract_details["address"] = st.text_input("عنوان الطرف الأول", key="tab1_emp_address")
                contract_details["duration"] = st.number_input("مدة العقد (بالأشهر)", min_value=1, step=1, key="tab1_emp_duration")
                contract_details["housing_allowance"] = st.checkbox("يشمل بدل سكن؟", key="tab1_emp_housing_allowance_check")
                if contract_details["housing_allowance"]:
                    contract_details["housing_percentage"] = st.slider("نسبة بدل السكن (%)", 0, 50, 25, key="tab1_emp_housing_percentage")
                contract_details["non_compete"] = st.checkbox("إضافة شرط عدم المنافسة؟", key="tab1_emp_non_compete_check")
                if contract_details["non_compete"]:
                    contract_details["non_compete_city"] = st.text_input("المدينة المشمولة بالشرط", key="tab1_emp_non_compete_city")
                contract_details["penalty_clause"] = st.checkbox("إضافة شرط جزائي؟", key="tab1_emp_penalty_clause_check")
                if contract_details["penalty_clause"]:
                    contract_details["penalty_amount"] = st.number_input("قيمة الشرط الجزائي (ريال)", min_value=0.0, step=100.0, format="%.2f", key="tab1_emp_penalty_amount")
                contract_details["termination_clause"] = st.checkbox("إمكانية فسخ العقد بإشعار مسبق؟", key="tab1_emp_termination_clause_check")

        elif selected_contract_type_ar == "عقد إيجار":
            st.markdown("### 📝 تفاصيل عقد الإيجار")
            contract_details["property_address"] = st.text_area("عنوان العقار المؤجر بالتفصيل", key="tab1_lease_property_address")
            col_lease1, col_lease2 = st.columns(2)
            with col_lease1:
                contract_details["duration"] = st.number_input("مدة الإيجار (بالأشهر)", min_value=1, step=1, key="tab1_lease_duration")
                contract_details["rent"] = st.number_input("قيمة الإيجار الشهري (ريال)", min_value=0.0, step=100.0, format="%.2f", key="tab1_lease_rent")
            with col_lease2:
                contract_details["deposit"] = st.number_input("قيمة التأمين (إن وجد) (ريال)", min_value=0.0, step=50.0, format="%.2f", key="tab1_lease_deposit")
                contract_details["maintenance"] = st.checkbox("هل المؤجر مسؤول عن الصيانة الرئيسية؟", key="tab1_lease_maintenance_check")

        elif selected_contract_type_ar == "عقد وكالة":
            st.markdown("### 📝 تفاصيل عقد الوكالة")
            contract_details["agency_scope"] = st.text_area("نطاق ومسؤوليات الوكالة بالتفصيل", key="tab1_agency_scope")
            contract_details["duration"] = st.number_input("مدة الوكالة (بالأشهر)", min_value=1, step=1, key="tab1_agency_duration")

        elif selected_contract_type_ar == "عقد بيع":
            st.markdown("### 📝 تفاصيل عقد البيع")
            contract_details["item_description"] = st.text_area("وصف الأصل أو الممتلكات المباعة بالتفصيل", key="tab1_sales_item_description")
            col_sales1, col_sales2 = st.columns(2)
            with col_sales1:
                contract_details["price"] = st.number_input("قيمة البيع الإجمالية (ريال)", min_value=0.0, step=100.0, format="%.2f", key="tab1_sales_price")
            with col_sales2:
                contract_details["delivery_date"] = st.date_input("تاريخ التسليم المتوقع", datetime.today(), key="tab1_sales_delivery_date")

        elif selected_contract_type_ar == "عقد عدم إفشاء (NDA)":
            st.markdown("### 📝 تفاصيل عقد عدم الإفشاء (NDA)")
            contract_details["scope"] = st.text_area("طبيعة ونطاق المعلومات السرية المشمولة بالعقد", key="tab1_nda_scope")
            contract_details["duration"] = st.number_input("مدة الالتزام بالسرية (بالأشهر)", min_value=1, step=1, key="tab1_nda_duration")

        st.markdown("---")
        st.markdown("### ✍️ التوقيع والختم")
        col_sig, col_stamp = st.columns(2)
        with col_sig:
            st.markdown('<div class="signature-container">', unsafe_allow_html=True)
            st.markdown('<p class="label-bold">ارسم توقيعك هنا:</p>', unsafe_allow_html=True)
            signature_data = st_canvas(
                fill_color="rgba(255, 165, 0, 0.3)",
                stroke_width=2,
                stroke_color="#000000",
                background_color="#ffffff",
                height=150,
                drawing_mode="freedraw",
                key=f"tab1_canvas_signature_main_contract_{selected_contract_type_ar}",
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_stamp:
            st.markdown('<div class="stamp-container">', unsafe_allow_html=True)
            st.markdown('<p class="label-bold">رفع صورة ختم الشركة (PNG):</p>', unsafe_allow_html=True)
            company_stamp_file = st.file_uploader("🖼️ رفع ختم", type=["png"], key=f"tab1_uploader_stamp_main_contract_{selected_contract_type_ar}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📤 خيارات الإرسال والمشاركة")
        col_share1, col_share2 = st.columns(2)
        with col_share1:
            send_whatsapp_check = st.checkbox("إرسال عبر واتساب", key="tab1_whatsapp_check")
            whatsapp_num = st.text_input("رقم الجوال (مثال: 9665xxxxxxxx)", max_chars=12, help="يرجى إدخال الرقم بدون رمز الدولة المسبوق بـ '+'", key="tab1_whatsapp_input") if send_whatsapp_check else ""
        with col_share2:
            send_email_check = st.checkbox("إرسال عبر البريد الإلكتروني", key="tab1_email_check")
            email_addr = st.text_input("البريد الإلكتروني", help="أدخل البريد الإلكتروني للمستلم", key="tab1_email_input") if send_email_check else ""

        generate_button = st.form_submit_button("✨ توليد العقد والتحميل")

    if generate_button:
        if not party1_name or not party2_name:
            st.warning("الرجاء إدخال اسمي الطرف الأول والثاني للمتابعة.")
        else:
            contract_data_for_pdf = {
                "party1": party1_name,
                "party2": party2_name,
                "date": contract_date,
                **contract_details
            }
            
            signature_image_array = None
            if signature_data and signature_data.image_data is not None:
                if signature_data.image_data.sum() < (signature_data.image_data.size * 255 * 3) * 0.98:
                    signature_image_array = signature_data.image_data
                else:
                    st.info("لم يتم اكتشاف توقيع واضح. سيتم إنشاء العقد بدون توقيع.")

            stamp_image_bytes = None
            if company_stamp_file:
                stamp_image_bytes = company_stamp_file

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
                st.exception(e)


# --- CRM Tab (Delegated to crm_modules.py) ---
with tab2:
    st.subheader("⚖️ نظام إدارة القضايا والعملاء (CRM)")
    st.markdown("نظام متكامل لإدارة بيانات العملاء، القضايا، التذكيرات، والفواتير المرتبطة.")

    clients_tab, cases_tab, reminders_tab, invoices_tab = st.tabs(["👥 العملاء", "⚖️ القضايا", "⏰ التذكيرات", "💰 الفواتير"])

    with clients_tab:
        render_client_management(next_id, save_data, reshape_arabic)
    
    with cases_tab:
        render_case_management(next_id, save_data, reshape_arabic)

    with reminders_tab:
        render_reminder_management(next_id, save_data, reshape_arabic)

    with invoices_tab:
        render_invoice_management(next_id, save_data, reshape_arabic)

# --- AI Insights Tab (NEW) ---
with tab3:
    st.subheader("🧠 الذكاء الاصطناعي (AI Insights)")
    st.markdown("استكشف كيف يمكن للذكاء الاصطناعي تعزيز إدارة العقود والقضايا لديك.")

    st.info("هذا القسم يوضح إمكانيات التكامل المستقبلي للذكاء الاصطناعي. الميزات أدناه هي مفاهيمية ولا تتطلب اتصالات API حقيقية في هذا الإصدار التجريبي.")

    ai_feature = st.selectbox(
        "اختر ميزة الذكاء الاصطناعي لاستكشافها:",
        ["تحليل العقود الذكي", "ملخصات القضايا التلقائية", "التنبؤ بنتائج القضايا", "مساعد البحث القانوني"],
        key="ai_feature_select"
    )

    if ai_feature == "تحليل العقود الذكي":
        st.markdown("#### 📄 تحليل العقود الذكي")
        st.write("يمكن للذكاء الاصطناعي مراجعة العقود لتحديد البنود الرئيسية، المخاطر المحتملة، والتناقضات، مما يوفر الوقت ويقلل الأخطاء.")
        st.file_uploader("قم بتحميل ملف عقد (PDF/DOCX) للتحليل (ميزة مفاهيمية)", type=["pdf", "docx"], key="ai_contract_uploader")
        st.button("بدء التحليل (ميزة مفاهيمية)", key="ai_analyze_button")
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 8px; margin-top: 20px;">
            <strong>نتائج التحليل المقترحة:</strong>
            <ul>
                <li>تحديد الأطراف والتواريخ الرئيسية.</li>
                <li>استخراج الالتزامات والحقوق لكل طرف.</li>
                <li>تحديد البنود الغامضة أو التي قد تتطلب مراجعة.</li>
                <li>اقتراح بنود قياسية مفقودة.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    elif ai_feature == "ملخصات القضايا التلقائية":
        st.markdown("#### 📝 ملخصات القضايا التلقائية")
        st.write("يقوم الذكاء الاصطناعي بتلخيص الوثائق القانونية الطويلة أو سجلات القضايا، مما يساعد المحامين على فهم النقاط الأساسية بسرعة.")
        
        if not st.session_state.cases.empty:
            case_names_for_ai = st.session_state.cases['case_name'].tolist()
            selected_case_for_summary = st.selectbox("اختر قضية لتلخيصها (ميزة مفاهيمية)", case_names_for_ai, key="ai_case_summary_select")
            st.button(f"توليد ملخص للقضية: {selected_case_for_summary} (ميزة مفاهيمية)", key="ai_summarize_button")
            st.markdown("""
            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <strong>ملخص مقترح:</strong>
                <p>هذا ملخص تلقائي للقضية المختارة، يبرز الوقائع الأساسية، الأطراف المعنية، والوضع القانوني الحالي، بالإضافة إلى أي تطورات حديثة.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("أضف قضايا في قسم 'إدارة القضايا' لتجربة هذه الميزة المفاهيمية.")

    elif ai_feature == "التنبؤ بنتائج القضايا":
        st.markdown("#### 🔮 التنبؤ بنتائج القضايا")
        st.write("باستخدام بيانات القضايا التاريخية، يمكن للذكاء الاصطناعي تقديم تقديرات لاحتمالية نجاح أو فشل قضية معينة، بناءً على عوامل متعددة.")
        st.warning("⚠️ هذه الميزة تتطلب كميات كبيرة من البيانات التاريخية الدقيقة وتستخدم لأغراض استشارية فقط.")
        st.button("الحصول على تنبؤ (ميزة مفاهيمية)", key="ai_predict_button")
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 8px; margin-top: 20px;">
            <strong>تنبؤ مقترح:</strong>
            <ul>
                <li>احتمالية النجاح: 75%</li>
                <li>المخاطر الرئيسية: عدم كفاية الأدلة في النقطة X.</li>
                <li>العوامل الإيجابية: سابقة قضائية قوية في قضية مشابهة.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    elif ai_feature == "مساعد البحث القانوني":
        st.markdown("#### 📚 مساعد البحث القانوني")
        st.write("يمكن للذكاء الاصطناعي المساعدة في البحث عن السوابق القضائية، المواد القانونية، والآراء الفقهية ذات الصلة بقضية معينة، مما يسرع عملية البحث القانوني.")
        st.text_area("أدخل استفسارك القانوني (ميزة مفاهيمية)", height=100, key="ai_legal_query")
        st.button("بحث (ميزة مفاهيمية)", key="ai_search_button")
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 8px; margin-top: 20px;">
            <strong>نتائج البحث المقترحة:</strong>
            <ul>
                <li>مرجع قانوني: المادة X من نظام Y.</li>
                <li>سابقة قضائية: الحكم رقم Z في القضية A.</li>
                <li>رأي فقهي: رأي الدكتور B حول المسألة C.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
