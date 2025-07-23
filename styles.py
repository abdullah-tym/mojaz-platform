# styles.py

custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons'); /* For Streamlit's internal icons */
/* Font Awesome for custom icons */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css');

:root {
    --primary-blue: #007bff; /* PracticePanther's primary blue */
    --dark-blue: #0056b3;
    --light-grey-bg: #f8f9fa; /* Very light grey background */
    --medium-grey: #e9ecef; /* Slightly darker grey for borders/dividers */
    --dark-text: #343a40;
    --light-text: #6c757d;
    --card-bg: #ffffff;
    --border-radius: 8px;
    --box-shadow-light: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    --box-shadow-medium: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

html, body, [class*="st-emotion"] {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl;
    text-align: right;
    background-color: var(--light-grey-bg);
    color: var(--dark-text);
}

/* --- General Layout & Headers --- */
h1, h2, h3, h4, h5, h6 {
    color: var(--dark-blue);
    font-weight: 700;
    margin-bottom: 0.8em;
    text-align: right;
    padding-bottom: 5px;
    border-bottom: 1px solid var(--medium-grey);
}

/* Main Streamlit container padding */
.st-emotion-cache-z5fcl4 { /* Main content area */
    padding-top: 2rem;
    padding-right: 2rem;
    padding-left: 2rem;
    padding-bottom: 2rem;
}

/* --- Top Navigation Bar (Custom) --- */
.top-nav-container {
    background-color: var(--card-bg);
    padding: 10px 20px;
    border-bottom: 1px solid var(--medium-grey);
    box-shadow: var(--box-shadow-light);
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 1000;
    margin: -2rem -2rem 2rem -2rem; /* Pull to edges of main content area */
    width: calc(100% + 4rem); /* Adjust width to cover full page width */
    border-radius: 0; /* No border radius for top bar */
}

.top-nav-left, .top-nav-right, .top-nav-center {
    display: flex;
    align-items: center;
    gap: 15px;
}

.top-nav-logo {
    font-size: 1.8em;
    font-weight: 700;
    color: var(--primary-blue);
    display: flex;
    align-items: center;
    gap: 5px;
}

.top-nav-search input {
    border-radius: 20px !important;
    padding: 8px 15px !important;
    border: 1px solid var(--medium-grey) !important;
    background-color: var(--light-grey-bg) !important;
    width: 250px; /* Fixed width for search */
}

.top-nav-link {
    font-weight: 600;
    color: var(--dark-text);
    text-decoration: none;
    padding: 8px 12px;
    border-radius: var(--border-radius);
    transition: background-color 0.2s ease;
}
.top-nav-link:hover {
    background-color: var(--medium-grey);
}

.top-nav-icon-button {
    background-color: transparent;
    border: none;
    color: var(--dark-text);
    font-size: 1.2em;
    cursor: pointer;
    padding: 5px;
    border-radius: 50%;
    transition: background-color 0.2s ease;
}
.top-nav-icon-button:hover {
    background-color: var(--medium-grey);
}

.user-profile {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    color: var(--dark-text);
}
.user-avatar {
    width: 35px;
    height: 35px;
    border-radius: 50%;
    background-color: var(--primary-blue);
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 0.9em;
}

/* --- KPI Box Styling (PracticePanther style) --- */
.kpi-box {
    background-color: var(--card-bg);
    padding: 20px;
    border-radius: var(--border-radius);
    color: var(--dark-text);
    font-weight: 600;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: var(--box-shadow-light);
    border: 1px solid var(--medium-grey);
    font-size: 1.1em;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 120px; /* Ensure consistent height */
}
.kpi-box:hover {
    transform: translateY(-3px);
    box-shadow: var(--box-shadow-medium);
}
.kpi-box strong {
    font-size: 2em;
    display: block;
    margin-top: 5px;
    color: var(--primary-blue); /* Default KPI number color */
}

/* Specific KPI colors */
.kpi-trust { background-color: #e6f7ff; border-left: 5px solid #007bff; } /* Light blue */
.kpi-trust strong { color: #007bff; }
.kpi-paid { background-color: #e6ffe6; border-left: 5px solid #28a745; } /* Light green */
.kpi-paid strong { color: #28a745; }
.kpi-total-due { background-color: #fff3e0; border-left: 5px solid #ffc107; } /* Light yellow/orange */
.kpi-total-due strong { color: #ffc107; }
.kpi-billable { background-color: #ffe6f7; border-left: 5px solid #6f42c1; } /* Light purple */
.kpi-billable strong { color: #6f42c1; }


/* --- Quick Action Buttons Grid --- */
.quick-actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); /* Responsive grid */
    gap: 15px;
    margin-top: 20px;
    margin-bottom: 30px;
}
.quick-action-card {
    background-color: var(--card-bg);
    padding: 15px;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow-light);
    border: 1px solid var(--medium-grey);
    text-align: center;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100px;
}
.quick-action-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--box-shadow-medium);
}
.quick-action-card i { /* Font Awesome icons */
    font-size: 2.2em;
    color: var(--primary-blue);
    margin-bottom: 10px;
}
.quick-action-card span {
    font-size: 0.9em;
    font-weight: 600;
    color: var(--dark-text);
}

/* --- Calendar & Timer Section --- */
.sidebar-right {
    background-color: var(--card-bg);
    padding: 20px;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow-light);
    border: 1px solid var(--medium-grey);
    margin-bottom: 20px;
}
.sidebar-right h4 {
    border-bottom: 1px solid var(--medium-grey);
    padding-bottom: 10px;
    margin-top: 0;
}

.mobile-apps-buttons {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}
.mobile-app-button {
    background-color: var(--primary-blue);
    color: white;
    padding: 8px 15px;
    border-radius: 20px;
    font-size: 0.9em;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s ease;
}
.mobile-app-button:hover {
    background-color: var(--dark-blue);
}
.mobile-app-button.active {
    background-color: var(--dark-blue); /* Active state */
}

.timer-display {
    background-color: var(--light-grey-bg);
    border: 1px solid var(--medium-grey);
    padding: 15px;
    border-radius: var(--border-radius);
    text-align: center;
    font-size: 2em;
    font-weight: 700;
    color: var(--dark-blue);
    margin-top: 15px;
}

/* Calendar (Conceptual) */
.calendar-conceptual {
    background-color: var(--light-grey-bg);
    border: 1px solid var(--medium-grey);
    padding: 15px;
    border-radius: var(--border-radius);
    margin-top: 20px;
    text-align: center;
    color: var(--dark-text);
}
.calendar-conceptual .header {
    font-weight: 700;
    font-size: 1.1em;
    margin-bottom: 10px;
}
.calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 5px;
    font-size: 0.9em;
}
.calendar-day {
    padding: 8px 5px;
    border-radius: 5px;
    background-color: var(--card-bg);
    border: 1px solid var(--medium-grey);
    color: var(--dark-text);
}
.calendar-day.today {
    background-color: var(--primary-blue);
    color: white;
    font-weight: 700;
}
.calendar-day.weekend {
    color: #dc3545; /* Red for weekends */
}


/* --- Recent Activity Section --- */
.recent-activity-container {
    background-color: var(--card-bg);
    padding: 20px;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow-light);
    border: 1px solid var(--medium-grey);
    margin-top: 30px;
}
.recent-activity-container h4 {
    margin-top: 0;
    border-bottom: 1px solid var(--medium-grey);
    padding-bottom: 10px;
}
.recent-activity-search input {
    border-radius: 20px !important;
    padding: 8px 15px !important;
    border: 1px solid var(--medium-grey) !important;
    background-color: var(--light-grey-bg) !important;
    width: 100%;
}
.activity-item {
    padding: 10px 0;
    border-bottom: 1px dashed var(--medium-grey);
    color: var(--light-text);
}
.activity-item:last-child {
    border-bottom: none;
}


/* --- General Streamlit Widget Overrides --- */
/* Primary Button Styling */
.stButton > button {
    background-color: var(--primary-blue);
    color: white;
    font-weight: 600;
    border-radius: var(--border-radius);
    padding: 10px 20px;
    border: none;
    transition: background-color 0.2s ease, transform 0.2s ease;
    box-shadow: var(--box-shadow-light);
}
.stButton > button:hover {
    background-color: var(--dark-blue);
    transform: translateY(-2px);
    box-shadow: var(--box-shadow-medium);
}

/* Secondary Buttons (e.g., Delete) */
.stButton > button[kind="secondary"] {
    background-color: #dc3545; /* Red for delete */
    color: white;
}
.stButton > button[kind="secondary"]:hover {
    background-color: #c82333;
}

/* Form Container Styling */
section[data-testid="stForm"] {
    background-color: var(--card-bg);
    padding: 25px 35px;
    border-radius: 15px;
    margin-bottom: 30px;
    box-shadow: var(--box-shadow-medium);
    border: 1px solid var(--medium-grey);
}

/* Info, Warning, Success, Error Boxes */
div[data-testid="stAlert"] {
    border-radius: var(--border-radius);
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: var(--box-shadow-light);
}
div[data-testid="stAlert"].st-emotion-cache-1f19u73 { /* Info */
    background-color: #e0f7fa; border-left: 5px solid #00bcd4; color: #006064;
}
div[data-testid="stAlert"].st-emotion-cache-1f19u73.warning { /* Warning */
    background-color: #fff3e0; border-left: 5px solid #ff9800; color: #e65100;
}
div[data-testid="stAlert"].st-emotion-cache-1f19u73.success { /* Success */
    background-color: #e8f5e9; border-left: 5px solid #4caf50; color: #2e7d32;
}
div[data-testid="stAlert"].st-emotion-cache-1f19u73.error { /* Error */
    background-color: #ffebee; border-left: 5px solid #f44336; color: #c62828;
}

/* Plotly Chart Container */
.stPlotlyChart {
    border-radius: var(--border-radius);
    overflow: hidden;
    box-shadow: var(--box-shadow-light);
    border: 1px solid var(--medium-grey);
    padding: 10px;
    background-color: var(--card-bg);
}

/* Tabs Styling */
div[data-testid="stTabs"] button {
    font-weight: 600;
    color: var(--light-text);
    background-color: var(--light-grey-bg);
    border-radius: var(--border-radius) var(--border-radius) 0 0;
    padding: 10px 20px;
    margin-right: 5px;
    border: 1px solid var(--medium-grey);
    border-bottom: none;
    transition: all 0.2s ease;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--dark-blue);
    background-color: var(--card-bg);
    border-top: 2px solid var(--primary-blue); /* Primary blue underline for active tab */
    border-left: 1px solid var(--medium-grey);
    border-right: 1px solid var(--medium-grey);
    border-bottom: none;
    box-shadow: var(--box-shadow-light);
}

/* Sidebar Styling (for logout button) */
.st-emotion-cache-10y5gq { /* Target sidebar container */
    padding-top: 20px;
    padding-bottom: 20px;
    background-color: var(--card-bg);
    box-shadow: 2px 0 10px rgba(0,0,0,0.05);
}
.st-emotion-cache-10y5gq .stButton > button {
    background-color: #dc3545; /* Red for logout */
    color: white;
    box-shadow: none;
}
.st-emotion-cache-10y5gq .stButton > button:hover {
    background-color: #c82333;
    transform: none;
}

/* Fix for Streamlit's internal icons (e.g., sidebar collapse/expand) */
.st-emotion-cache-1c7y2vl button,
.st-emotion-cache-1c7y2vl button .material-icons {
    font-family: 'Material Icons' !important;
    font-size: 24px !important;
    color: var(--dark-blue) !important;
}
.st-emotion-cache-1c7y2vl button:hover {
    background-color: rgba(0, 123, 255, 0.1) !important;
}

/* Dataframe styling */
div[data-testid="stDataFrame"] {
    border-radius: var(--border-radius);
    border: 1px solid var(--medium-grey);
    box-shadow: var(--box-shadow-light);
    overflow: hidden; /* Ensures rounded corners are visible */
}
/* Header of the dataframe */
div[data-testid="stDataFrame"] .header {
    background-color: var(--light-grey-bg);
    color: var(--dark-text);
    font-weight: 600;
}
/* Rows of the dataframe */
div[data-testid="stDataFrame"] .row {
    background-color: var(--card-bg);
    border-bottom: 1px solid var(--medium-grey);
}
div[data-testid="stDataFrame"] .row:nth-child(even) {
    background-color: #fcfdff; /* Slightly different shade for even rows */
}


</style>
"""
