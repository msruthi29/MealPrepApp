"""
Main Streamlit application for AI-powered Meal Prep & Nutrition App
"""
import streamlit as st
import pandas as pd
import tempfile
import os
from utils.session_data import initialize_session_state, get_active_baby_df, get_active_adult_df, update_baby_dataset, update_adult_dataset
from utils.csv_validation import validate_baby_csv, validate_adult_csv, load_default_csvs
from components.food_items_tab import render_food_items_tab
from components.baby_nutrition_tab import render_baby_nutrition_tab
from components.adult_nutrition_tab import render_adult_nutrition_tab
from components.ai_feedback_chat_tab import render_ai_feedback_chat_tab


# Page configuration
st.set_page_config(
    page_title="MealNest",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
initialize_session_state()

# Sidebar for file uploads and configuration
st.sidebar.markdown("## 📤 Upload Food Data")

# Baby food upload
st.sidebar.markdown("### 👶 Baby Food Items")
baby_file = st.sidebar.file_uploader(
    "Upload baby food CSV",
    type="csv",
    key="baby_food_upload",
    help="Must have columns: food_id, food_item, texture_stage, safe_preparation, allergen"
)

if baby_file:
    try:
        df = pd.read_csv(baby_file)
        is_valid, error_msg, cleaned_df = validate_baby_csv(df)
        
        if is_valid:
            update_baby_dataset(cleaned_df, baby_file.name)
            st.sidebar.success(f"✓ Baby food CSV loaded: {baby_file.name}")
        else:
            st.sidebar.error(f"❌ Invalid baby food CSV: {error_msg}")
    except Exception as e:
        st.sidebar.error(f"❌ Error reading baby food CSV: {str(e)}")

# Adult food upload
st.sidebar.markdown("### 🥗 Adult Food Items")
adult_file = st.sidebar.file_uploader(
    "Upload adult food CSV",
    type="csv",
    key="adult_food_upload",
    help="Must have columns: food_item, allergen, measurable_quantity"
)

if adult_file:
    try:
        df = pd.read_csv(adult_file)
        is_valid, error_msg, cleaned_df = validate_adult_csv(df)
        
        if is_valid:
            update_adult_dataset(cleaned_df, adult_file.name)
            st.sidebar.success(f"✓ Adult food CSV loaded: {adult_file.name}")
        else:
            st.sidebar.error(f"❌ Invalid adult food CSV: {error_msg}")
    except Exception as e:
        st.sidebar.error(f"❌ Error reading adult food CSV: {str(e)}")

# Display active datasets info
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ Active Datasets")

col1, col2 = st.sidebar.columns(2)
with col1:
    st.sidebar.metric(
        "Baby Foods",
        len(get_active_baby_df()),
        st.session_state.baby_source if st.session_state.baby_valid else "Error"
    )

with col2:
    st.sidebar.metric(
        "Adult Foods",
        len(get_active_adult_df()),
        st.session_state.adult_source if st.session_state.adult_valid else "Error"
    )

# Main content area
st.title("🍽️ MealNest")
st.markdown(
    "Plan family meals with easy recipe combinations built from your selected ingredients."
)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🍽️ Food Items",
    "👶 Baby Nutrition & Meal Prep",
    "🥗 Adult Nutrition & Meal Prep",
    "🤖 AI Feedback Chat"
])

with tab1:
    render_food_items_tab(
        get_active_baby_df(),
        get_active_adult_df(),
        st.session_state.baby_source,
        st.session_state.adult_source
    )

with tab2:
    render_baby_nutrition_tab(get_active_baby_df())

with tab3:
    render_adult_nutrition_tab(get_active_adult_df())

with tab4:
    render_ai_feedback_chat_tab(
        get_active_baby_df(),
        get_active_adult_df()
    )

# Footer
st.markdown("---")
st.markdown(
    """
    **Disclaimer:** This app is for meal planning and nutrition-data viewing only, 
    not individualized medical or feeding advice. Consult healthcare professionals 
    for individual dietary concerns or allergy guidance.
    """
)
