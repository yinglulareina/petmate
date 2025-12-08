"""
PetMate - AI Pet Health Assistant (Streamlit UI)

This module provides the web-based user interface for PetMate using Streamlit.
Includes symptom analysis, veterinary hospital locator, and interactive UI
with responsive design and user-friendly features.

Author: PetMate Team
Date: November 2025
"""

# ==================== Imports ====================
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from src.ai_symptom_analyzer import AISymptomAnalyzer
from src.vet_locator import VetLocator

# ==================== Page Config ====================
st.set_page_config(page_title="PetMate", page_icon="🐾", layout="centered")

# ==================== Global CSS ====================
st.markdown("""
<style>

/* ----------------------------------------------------------------------------------
   THEME STYLES
   ---------------------------------------------------------------------------------- */

/* Tab specific - dark text on light background */
.stTabs [data-baseweb="tab"],
.stTabs [data-baseweb="tab"] *,
.stTabs button[role="tab"],
.stTabs button[role="tab"] * {
    color: #0066cc !important;
}

/* Tab hover - dark text on light background */
.stTabs [data-baseweb="tab"]:hover,
.stTabs [data-baseweb="tab"]:hover *,
.stTabs button[role="tab"]:hover,
.stTabs button[role="tab"]:hover * {
    color: #03386e !important;
}

/* Selected tab - white text */
.stTabs [aria-selected="true"],
.stTabs [aria-selected="true"] *,
.stTabs button[aria-selected="true"],
.stTabs button[aria-selected="true"] * {
    color: white !important;
}

/* Primary button text force white */
.stButton > button[kind="primary"],
.stButton > button[kind="primary"] *,
.stButton > div > button[kind="primary"],
.stButton > div > button[kind="primary"] * {
    color: white !important;
}

/* Secondary buttons text force white */
.stButton > button[kind="secondary"],
.stButton > button[kind="secondary"] *,
.stButton > div > button[kind="secondary"],
.stButton > div > button[kind="secondary"] * {
    background: #0066cc !important;
    color: white !important;
}


/* ----------------------------------------------------------------------------------
   BASE STYLES
   ---------------------------------------------------------------------------------- */

/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

/* Global app styling */
.stApp { 
    font-family: 'Inter', sans-serif; 
    background: #f0f7ff; 
}

/* Hide Streamlit branding elements */
#MainMenu, footer, header { 
    visibility: hidden; 
}


/* ----------------------------------------------------------------------------------
   HEADER SECTION
   ---------------------------------------------------------------------------------- */

.header { 
    text-align: center; 
    padding: 1.5rem 0; 
}

.header h1 { 
    font-size: 2.2rem; 
    color: #0066cc; 
    margin: 0; 
}

.header p { 
    color: #5a8fc7; 
    margin: 0.5rem 0 0; 
}


/* ----------------------------------------------------------------------------------
   NAVIGATION TABS
   ---------------------------------------------------------------------------------- */

/* Tabs container - centered layout */
.stTabs {
    max-width: 800px;
    margin: 0 auto !important;
}

/* Tab list wrapper - transparent background, centered */
.stTabs [data-baseweb="tab-list"] { 
    gap: 16px;
    background: transparent !important;
    padding: 0 !important;
    border-radius: 0 !important;
    margin-bottom: 1.5rem;
    box-shadow: none !important;
    display: flex !important;
    justify-content: center !important;
}

/* Individual tab button - equal width, centered text */
.stTabs [data-baseweb="tab"] { 
    background: #e6f2ff !important;
    border-radius: 10px !important; 
    color: #0066cc !important; 
    padding: 0.75rem 0 !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    border: 2px solid #b3d9ff !important;
    transition: background-color 0.3s ease, border-color 0.3s ease !important;
    width: 200px !important;
    text-align: center !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Tab hover state - color change only, no movement */
.stTabs [data-baseweb="tab"]:hover {
    background: #cce5ff !important;
    border-color: #0066cc !important;
}

/* Active/selected tab */
.stTabs [aria-selected="true"] { 
    background: linear-gradient(135deg, #0066cc, #004999) !important; 
    color: white !important;
    border-color: #0066cc !important;
}


/* ----------------------------------------------------------------------------------
   BUTTONS
   ---------------------------------------------------------------------------------- */

/* Primary buttons (e.g., Analyze Symptoms, Search) */
.stButton > button[kind="primary"] { 
    background: linear-gradient(135deg, #0066cc, #004999) !important;
    border: none !important; 
    border-radius: 10px !important; 
}

/* Secondary buttons (e.g., New Analysis) */
.stButton > button[kind="secondary"] { 
    border: 2px solid #0066cc !important; 
    color: #0066cc !important; 
}


/* ----------------------------------------------------------------------------------
   INPUT FIELDS
   ---------------------------------------------------------------------------------- */

/* Text area and text input - base styling */
.stTextArea textarea, 
.stTextInput input {
    background-color: #f8fafc !important;
    border-radius: 10px !important; 
    border: 2px solid #d1e3f8 !important;
    font-size: 1rem !important;
    color: #1e293b !important;
}

/* Text area specific styling */
.stTextArea > div > div > textarea {
    background-color: #f8fafc !important;
    color: #1e293b !important;
}

/* Placeholder text - visible dark gray */
.stTextArea textarea::placeholder, 
.stTextInput input::placeholder {
    color: #64748b !important;
    opacity: 1 !important;
}


/* ----------------------------------------------------------------------------------
   SELECT BOX (DROPDOWN MENU)
   ---------------------------------------------------------------------------------- */

/* Select box container */
.stSelectbox > div > div {
    background-color: #f8fafc !important;
    border: 2px solid #d1e3f8 !important;
    border-radius: 10px !important;
    color: #1e293b !important;
}

/* Select box dropdown arrow icon */
.stSelectbox svg {
    fill: #64748b !important;
}

/* Select box selected value text */
.stSelectbox [data-baseweb="select"] > div {
    background-color: #f8fafc !important;
    color: #1e293b !important;
}

/* Dropdown popover container */
[data-baseweb="popover"] {
    background-color: white !important;
}

/* Dropdown menu list */
[data-baseweb="menu"] {
    background-color: white !important;
    border: 2px solid #d1e3f8 !important;
    border-radius: 10px !important;
}

/* Individual dropdown option */
[role="option"] {
    background-color: white !important;
    color: #1e293b !important;
}

/* Dropdown option hover state */
[role="option"]:hover {
    background-color: #f0f7ff !important;
    color: #0066cc !important;
}

/* Currently selected option in dropdown */
[aria-selected="true"] {
    background-color: #e6f2ff !important;
    color: #0066cc !important;
}

/* Select box when dropdown is opened */
.stSelectbox [data-baseweb="popover"] {
    background-color: white !important;
}


/* ----------------------------------------------------------------------------------
   RESULT CARDS (ANALYSIS DISPLAY)
   ---------------------------------------------------------------------------------- */

/* Base result card styling */
.result-card { 
    border-radius: 16px; 
    padding: 1.5rem; 
    margin: 1rem 0;
    border-left: 5px solid #0066cc; 
    background: linear-gradient(135deg, #e6f2ff, #cce5ff); 
}

/* Urgent severity result card */
.result-card.urgent { 
    border-left-color: #dc3545; 
    background: linear-gradient(135deg, #fff0f0, #ffe6e6); 
}

/* Moderate severity result card */
.result-card.moderate { 
    border-left-color: #fd7e14; 
    background: linear-gradient(135deg, #fff8f0, #ffedd5); 
}


/* ----------------------------------------------------------------------------------
   BADGES (SEVERITY INDICATORS)
   ---------------------------------------------------------------------------------- */

/* Base badge styling */
.badge { 
    display: inline-block; 
    padding: 0.4rem 0.8rem; 
    border-radius: 20px; 
    font-weight: 600; 
    font-size: 0.8rem; 
}

/* High priority badge (severe/urgent) */
.badge-high { 
    background: #ffe6e6; 
    color: #dc3545; 
}

/* Medium priority badge (moderate) */
.badge-medium { 
    background: #ffedd5; 
    color: #d97706; 
}

/* Low priority badge (mild) */
.badge-low { 
    background: #e6f2ff; 
    color: #0066cc; 
}


/* ----------------------------------------------------------------------------------
   HOSPITAL CARDS
   ---------------------------------------------------------------------------------- */

/* Hospital card container */
.hospital-card { 
    background: white; 
    border-radius: 12px; 
    padding: 1rem; 
    margin-bottom: 0.75rem;
    border: 1px solid #b8d4f0; 
}

/* Hospital card hover state */
.hospital-card:hover { 
    border-color: #0066cc; 
    box-shadow: 0 4px 12px rgba(0,102,204,0.15); 
}


/* ----------------------------------------------------------------------------------
   EXPANDER (COLLAPSIBLE SECTIONS)
   ---------------------------------------------------------------------------------- */

/* Fix expander title text color */
[data-testid="stExpander"] summary {
    color: #1e293b !important;
}

/* ----------------------------------------------------------------------------------
   STREAMLIT ALERT COMPONENTS (ERROR, WARNING, INFO, SUCCESS)
   ---------------------------------------------------------------------------------- */

/* Error message box */
.stAlert[data-baseweb="notification"] > div {
    background-color: #fee !important;
    border-left: 4px solid #dc3545 !important;
    color: #1e293b !important;
}

/* Error message text */
.stAlert p, 
.stAlert div,
.stAlert span {
    color: #1e293b !important;
}

/* Warning message */
.stWarning {
    color: #1e293b !important;
}

/* Info message */
.stInfo {
    color: #1e293b !important;
}

/* Success message */
.stSuccess {
    color: #1e293b !important;
}

/* Alert content */
[data-testid="stMarkdownContainer"] p {
    color: #1e293b !important;
}

/* Specific fix for error/warning/info text */
div[data-testid="stNotification"] p,
div[data-testid="stNotification"] div {
    color: #1e293b !important;
}

/* ----------------------------------------------------------------------------------
   MARKDOWN CONTENT (HEADINGS AND TEXT)
   ---------------------------------------------------------------------------------- */

/* Force all markdown headings to be dark */
h1, h2, h3, h4, h5, h6 {
    color: #1e293b !important;
}

/* Streamlit markdown container text */
div[data-testid="stMarkdownContainer"] * {
    color: #1e293b !important;
}

</style>
""", unsafe_allow_html=True)

# ==================== Helper Functions ====================
def get_urgency(result: dict):
    """Get urgency level from analysis result."""
    severity = (result.get("severity") or "").lower()
    if result.get("urgent") or severity == "severe":
        return "High", "urgent", "badge-high", "🚨"
    elif severity == "moderate":
        return "Medium", "moderate", "badge-medium", "⚠️"
    return "Low", "", "badge-low", "✅"


# ==================== Header ====================
st.markdown("""
<div class="header">
    <h1>🏥 PetMate</h1>
    <p>AI-Powered Pet Health Assistant</p>
</div>
""", unsafe_allow_html=True)

# ==================== Navigation Tabs ====================
tab1, tab2 = st.tabs(["🩺 Symptom Analysis", "🏥 Find Vets"])

# ==================== Tab 1: Symptom Analysis ====================
with tab1:
    pet_type = st.selectbox(
        "Pet Type",
        ["dog", "cat"],
        format_func=lambda x: "Dog" if x == "dog" else "Cat"
    )

    symptoms = st.text_area(
        "Describe symptoms",
        height=120,
        placeholder="E.g., My dog has been vomiting since morning and seems tired..."
    )

    if st.button("Analyze Symptoms", type="primary", use_container_width=True):
        # Call AISymptomAnalyzer for input validation
        is_valid, error_msg = AISymptomAnalyzer.validate_symptom_input(symptoms)

        if not is_valid:
            st.error(error_msg)
        else:
            with st.spinner("Analyzing..."):
                try:
                    # Initialize analyzer if not exists
                    if "analyzer" not in st.session_state:
                        st.session_state.analyzer = AISymptomAnalyzer()

                    # Analyze symptoms
                    result = st.session_state.analyzer.analyze_symptoms(
                        symptoms.strip(),
                        pet_type
                    )
                    st.session_state.result = result

                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # Display Result
    if "result" in st.session_state and st.session_state.result:
        r = st.session_state.result
        level, card_cls, badge_cls, icon = get_urgency(r)

        st.markdown(f"""
        <div class="result-card {card_cls}">
            <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:1rem;">
                <div>
                    <small style="color:#6b7280;">POTENTIAL CONDITION</small>
                    <h3 style="margin:0; color:#1e293b;">{r.get('condition_name', 'Unknown')}</h3>
                </div>
                <span class="badge {badge_cls}">{icon} {level}</span>
            </div>
            <p style="color:#4b5563; margin-bottom:1rem;">{r.get('description', '')}</p>
            <div style="background:white; padding:1rem; border-radius:10px;">
                <strong>💡 Recommendation</strong><br>
                <span style="color:#4b5563;">{r.get('recommended_action', 'Consult a vet.')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 New Analysis", type="secondary", use_container_width=True):
            st.session_state.result = None
            st.session_state.pop('result', None)
            st.rerun()

# ==================== Tab 2: Find Vets ====================
with tab2:
    st.markdown("### Find Nearby Veterinary Hospitals")

    col1, col2 = st.columns([2, 1])
    with col1:
        location = st.text_input(
            "Your Location",
            placeholder="Enter your city (e.g. San Jose, 95114)",
            help="We support: Boston, San Jose, San Francisco, Oakland, Palo Alto"
        )
    with col2:
        radius = st.selectbox("Search Radius", [10, 25, 50], index=2,
                              format_func=lambda x: f"{x} km")

    # Filters
    with st.expander("Filters"):
        emergency = st.selectbox("Type", ["All", "Emergency Only", "Regular Only"])
        min_rating = st.selectbox("Min Rating", [3.0, 3.5, 4.0, 4.5, 5.0], index=2,
                                  format_func=lambda x: f"{x}+")

    if st.button("Search", type="primary", use_container_width=True):
        if not location.strip():
            st.warning("Please enter a city name.")
        else:
            with st.spinner("Searching..."):
                try:
                    # call VetLocator
                    locator = VetLocator()

                    # Get geocoding info with details
                    geocode_info = locator.get_geocode_info(location.strip())

                    if not geocode_info["success"]:
                        st.error(geocode_info["message"])
                        st.info(
                            f"Available cities: "
                            f"{', '.join(geocode_info['available_cities'])}"
                        )
                    else:
                        coords = geocode_info["coordinates"]

                        # Show feedback based on source
                        if geocode_info["source"] == "database":
                            st.info(geocode_info["message"])
                        elif geocode_info["source"] == "fallback":
                            st.warning(geocode_info["message"])

                        # Search hospitals
                        is_emerg = True if emergency == "Emergency Only" else (
                            False if emergency == "Regular Only" else None)

                        hospitals = locator.get_nearby_hospitals(
                            coords, radius, min_rating, is_emerg
                        )
                        hospitals = locator.sort_by_distance(hospitals)

                        st.session_state.hospitals = {
                            "list": hospitals,
                            "city": location
                        }

                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Search error: {e}")

    # Display Results
    if "hospitals" in st.session_state and st.session_state.hospitals:
        data = st.session_state.hospitals
        st.markdown(f"**Found {len(data['list'])} hospitals near {data['city'].title()}**")

        if not data["list"]:
            st.info("No hospitals match your criteria. Try adjusting filters.")
        else:
            for h in data["list"]:
                emerg_badge = "24/7" if h.get("is_emergency") else ""
                specs = ", ".join(h.get("specialties", [])[:4])
                st.markdown(f"""
                <div class="hospital-card">
                    <div style="display:flex; justify-content:space-between;">
                        <strong style="color:#1e293b;">{h['name']}</strong>
                        <span style="color:#dc2626; font-size:0.8rem;">{emerg_badge}</span>
                    </div>
                    <div style="color:#6b7280; font-size:0.85rem; margin:0.5rem 0;">
                        {h['address']}<br>
                        {h['phone']} &nbsp;|&nbsp; {h['rating']} &nbsp;|&nbsp; {h.get('distance', 'N/A')} km
                    </div>
                    <div style="font-size:0.75rem; color:#9ca3af;">{specs}</div>
                </div>
                """, unsafe_allow_html=True)

# ==================== Footer ====================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#5a8fc7; font-size:0.75rem;'>⚠️ For guidance only. Always consult a licensed veterinarian.</p>",
    unsafe_allow_html=True)
