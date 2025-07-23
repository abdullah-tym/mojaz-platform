# styles.py

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

html, body, [class*="st-emotion"] {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl;
    text-align: right;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] div[role="listbox"],
div[data-testid="stDateInput"] input,
div[data-testid="stNumberInput"] input {
    text-align: right;
    direction: rtl;
}
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stDateInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stCheckbox"] label,
div[data-testid="stRadio"] label {
    width: 100%;
    text-align: right;
}

h1, h2, h3, h4, h5, h6 {
    color: #0d3b66;
    font-weight: 700;
    margin-bottom: 0.5em;
    text-align: right;
}

.stButton > button {
    background-color: #f4d35e;
    color: #0d3b66;
    font-weight: 700;
    border-radius: 8px;
    padding: 10px 25px;
    margin-top: 15px;
    border: none;
    transition: background-color 0.3s ease, color 0.3s ease;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
}
.stButton > button:hover {
    background-color: #ee964b;
    color: white;
    cursor: pointer;
}

section[data-testid="stForm"] {
    background-color: #f9f9f9;
    padding: 20px 30px;
    border-radius: 15px;
    margin-bottom: 30px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

div[data-testid="stMarkdownContainer"] p {
    margin-bottom: 0.8em;
    line-height: 1.7;
    text-align: right;
}

.signature-container, .stamp-container {
    background-color: #e1e7f0;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 25px;
    border: 1px dashed #0d3b66;
}

.label-bold {
    font-weight: 700;
    margin-bottom: 8px;
    display: block;
    color: #0d3b66;
}

/* Updated KPI box styling */
.kpi-box {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 12px;
    color: #0d3b66;
    font-weight: 700;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    border: 1px solid #e0e0e0;
    font-size: 1.2em;
}
.kpi-box strong {
    font-size: 1.8em;
    display: block;
    margin-top: 5px;
}

.stRadio > label, .stCheckbox > label {
    flex-direction: row-reverse;
    justify-content: flex-end;
}
.stRadio div[role="radiogroup"], .stCheckbox div {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}
.stRadio div label span, .stCheckbox div label span {
    margin-right: 0.5em;
}

.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
</style>
"""
