# pdf_utils.py

from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image
from io import BytesIO
import tempfile
import os
from datetime import datetime, date # Import date for type checking

import streamlit as st # Used for st.error and st.stop in get_font_path

from config import AMIRI_FONT_NAME, AMIRI_FONT_PATH # Import font constants

def reshape_arabic(text):
    """Reshapes Arabic text for proper display in PDF and Streamlit."""
    if not isinstance(text, str):
        return text # Return as is if not a string (e.g., numbers, None)
    return get_display(arabic_reshaper.reshape(text))

def get_font_path(font_name=AMIRI_FONT_NAME):
    """Returns the path to the specified font, with error handling."""
    font_paths = {
        AMIRI_FONT_NAME: AMIRI_FONT_PATH
    }
    path = font_paths.get(font_name)
    if not path or not os.path.exists(path):
        st.error(f"Error: Required font '{font_name}' not found at {path}. "
                 "Please ensure 'Amiri-Regular.ttf' is in the same directory as main_app.py.")
        st.stop() # Stop execution if font is critical and missing
    return path

def generate_contract_pdf(contract_type, data, signature_img_data=None, stamp_file_data=None):
    """
    Generates a PDF contract based on type and data, with optional signature and stamp.
    """
    pdf = FPDF()
    pdf.add_page()

    amiri_font_path = get_font_path(AMIRI_FONT_NAME)
    pdf.add_font(AMIRI_FONT_NAME, "", amiri_font_path, uni=True)
    pdf.set_font(AMIRI_FONT_NAME, size=14)

    pdf.set_font(AMIRI_FONT_NAME, size=20)
    pdf.cell(0, 15, txt=reshape_arabic(f"{contract_type}"), ln=True, align="C")
    pdf.ln(10)

    pdf.set_font(AMIRI_FONT_NAME, size=12)

    # Convert date objects to string for PDF display
    formatted_date = data['date'].strftime("%Y-%m-%d") if isinstance(data['date'], (datetime, date)) else data['date']
    
    content_lines = []
    if contract_type == "عقد عمل":
        start_date_formatted = data['start_date'].strftime("%Y-%m-%d") if isinstance(data['start_date'], (datetime, date)) else data['start_date']
        content_lines = [
            f"بتاريخ {formatted_date}، تم الاتفاق بين:",
            f"الطرف الأول: {data['party1']}، سجل تجاري رقم: {data.get('cr_number', 'غير محدد')}، العنوان: {data.get('address', 'غير محدد')}.",
            f"الطرف الثاني: {data['party2']}، رقم الهوية/الإقامة: {data.get('id_number', 'غير محدد')}.",
            f"بموجب هذا العقد، يلتزم الطرف الثاني بالعمل لدى الطرف الأول بوظيفة: {data.get('job_title', 'غير محدد')}.",
            f"وذلك براتب شهري قدره: {data.get('salary', 0):.2f} ريال سعودي، لمدة: {data.get('duration', 0)} شهرًا، تبدأ في: {start_date_formatted}.",
        ]
        if data.get("housing_allowance") and data.get("housing_percentage"):
            content_lines.append(f"يشمل العقد بدل سكن بنسبة {data['housing_percentage']}% من الراتب الأساسي.")
        if data.get("non_compete"):
            content_lines.append(f"يتعهد الطرف الثاني بعدم المنافسة أو العمل لدى جهة أخرى مماثلة في مدينة {data.get('non_compete_city', 'غير محدد')} لمدة 6 أشهر بعد انتهاء العقد.")
        if data.get("penalty_clause") and data.get("penalty_amount"):
            content_lines.append(f"في حال الإخلال ببنود العقد، تفرض غرامة مالية قدرها {data.get('penalty_amount', 0):.2f} ريال سعودي على الطرف المخل.")
        if data.get("termination_clause"):
            content_lines.append("يمكن لأي من الطرفين فسخ العقد بإشعار كتابي مسبق مدته 30 يومًا.")
        content_lines.append("يخضع هذا العقد لأحكام نظام العمل السعودي ولوائحه التنفيذية.")

    elif contract_type == "عقد إيجار":
        content_lines = [
            f"بتاريخ {formatted_date}، بين المؤجر: {data['party1']} والمستأجر: {data['party2']}.",
            f"العقار المؤجر: {data.get('property_address', 'غير محدد')}.",
            f"مدة الإيجار: {data.get('duration', 0)} شهرًا، تبدأ من تاريخ توقيع العقد.",
            f"قيمة الإيجار الشهري: {data.get('rent', 0):.2f} ريال سعودي.",
            f"قيمة التأمين (إن وجد): {data.get('deposit', 0):.2f} ريال سعودي.",
            f"مسؤولية الصيانة: {'على المؤجر' if data.get('maintenance') else 'على المستأجر'}."
        ]
    elif contract_type == "عقد وكالة":
        content_lines = [
            f"بتاريخ {formatted_date}، أبرم هذا العقد بين الموكل: {data['party1']} والوكيل: {data['party2']}.",
            f"مدة الوكالة: {data.get('duration', 0)} شهرًا.",
            f"نطاق الوكالة: {data.get('agency_scope', 'غير محدد')}."
        ]
    elif contract_type == "عقد بيع":
        delivery_date_formatted = data['delivery_date'].strftime("%Y-%m-%d") if isinstance(data['delivery_date'], (datetime, date)) else data['delivery_date']
        content_lines = [
            f"بتاريخ {formatted_date}، تم إبرام عقد البيع هذا بين البائع: {data['party1']} والمشتري: {data['party2']}.",
            f"وصف الأصل المباع: {data.get('item_description', 'غير محدد')}.",
            f"قيمة البيع الإجمالية: {data.get('price', 0):.2f} ريال سعودي.",
            f"تاريخ التسليم المتوقع: {delivery_date_formatted}."
        ]
    elif contract_type == "عقد عدم إفشاء (NDA)":
        content_lines = [
            f"بتاريخ {formatted_date}، تم الاتفاق على السرية بين: {data['party1']} و {data['party2']}.",
            f"مدة الالتزام بالسرية: {data.get('duration', 0)} شهرًا.",
            f"طبيعة المعلومات المشمولة بالسرية: {data.get('scope', 'غير محدد')}."
        ]
    
    for line in content_lines:
        pdf.multi_cell(0, 10, txt=reshape_arabic(line), align="R")
    
    pdf.ln(20)

    # --- Signature Handling ---
    if signature_img_data is not None:
        tmp_sig_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_sig:
                tmp_sig_path = tmp_sig.name 

            sig_img = Image.fromarray(signature_img_data.astype('uint8')).convert("RGBA")
            max_w, max_h = 70, 50
            sig_w, sig_h = sig_img.size
            ratio = min(max_w / sig_w, max_h / sig_h)
            new_w = int(sig_w * ratio)
            new_h = int(sig_h * ratio)
            sig_img = sig_img.resize((new_w, new_h), Image.LANCZOS)
            
            bg = Image.new("RGBA", sig_img.size, (255, 255, 255, 255))
            bg.paste(sig_img, (0, 0), sig_img)
            final_sig_img = bg.convert("RGB")
            
            final_sig_img.save(tmp_sig_path, "PNG")

            pdf.image(tmp_sig_path, x=pdf.w - 80, y=pdf.h - 70, w=new_w, h=new_h)
        finally:
            if tmp_sig_path and os.path.exists(tmp_sig_path):
                os.unlink(tmp_sig_path)

    # --- Stamp Handling ---
    if stamp_file_data:
        tmp_stamp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_stamp:
                tmp_stamp_path = tmp_stamp.name 
                stamp_file_data.seek(0) # Ensure file pointer is at the beginning
                tmp_stamp.write(stamp_file_data.read())
            
            stamp_img = Image.open(tmp_stamp_path).convert("RGBA")
            max_w_stamp, max_h_stamp = 50, 50
            stamp_w, stamp_h = stamp_img.size
            ratio_stamp = min(max_w_stamp / stamp_w, max_h_stamp / stamp_h)
            new_w_stamp = int(stamp_w * ratio_stamp)
            new_h_stamp = int(stamp_h * ratio_stamp)
            stamp_img = stamp_img.resize((new_w_stamp, new_h_stamp), Image.LANCZOS)
            
            bg_stamp = Image.new("RGBA", stamp_img.size, (255, 255, 255, 255))
            bg_stamp.paste(stamp_img, (0, 0), stamp_img)
            final_stamp_img = bg_stamp.convert("RGB")
            
            final_stamp_img.save(tmp_stamp_path, "PNG")

            pdf.image(tmp_stamp_path, x=20, y=pdf.h - 70, w=new_w_stamp, h=new_h_stamp)
        finally:
            if tmp_stamp_path and os.path.exists(tmp_stamp_path):
                os.unlink(tmp_stamp_path)

    return pdf.output(dest="S").encode("latin-1")
