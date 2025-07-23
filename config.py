# config.py

import os

# --- Data Persistence ---
DATA_FILE = "mojaz_data.json" # File to store application data

# --- Font Configuration for PDF Generation ---
AMIRI_FONT_NAME = "Amiri"
# Assumes Amiri-Regular.ttf is in the same directory as main_app.py or the project root
AMIRI_FONT_PATH = os.path.join(os.path.dirname(__file__), "Amiri-Regular.ttf")

# --- Contract Type Options (for consistency) ---
CONTRACT_TYPE_OPTIONS = {
    "عقد عمل": "employment_contract",
    "عقد إيجار": "lease_agreement",
    "عقد وكالة": "agency_contract",
    "عقد بيع": "sales_contract",
    "عقد عدم إفشاء (NDA)": "nda_contract"
}

# --- Case Type Options ---
CASE_TYPE_OPTIONS = ["مدني", "جنائي", "تجاري", "إداري", "أحوال شخصية", "عقاري", "عمالي", "أخرى"]

# --- Case Status Options ---
CASE_STATUS_OPTIONS = ["نشطة", "مغلقة", "معلقة", "مؤجلة", "في الاستئناف", "انتظار الحكم"]

# --- Reminder Related Types ---
REMINDER_RELATED_TYPES = ["عميل", "قضية", "عام"]

# --- Payment Status Options ---
PAYMENT_STATUS_OPTIONS = ["الكل", "مدفوعة", "غير مدفوعة"]
