"""
Session state management for the meal prep app.
"""
import streamlit as st
import pandas as pd
from typing import Optional
from utils.csv_validation import load_default_csvs


def initialize_session_state():
    """Initialize all session state variables if not already present."""
    if "baby_df" not in st.session_state:
        try:
            baby_df, adult_df = load_default_csvs()
            st.session_state.baby_df = baby_df
            st.session_state.baby_source = "Default"
            st.session_state.baby_valid = True
            
            st.session_state.adult_df = adult_df
            st.session_state.adult_source = "Default"
            st.session_state.adult_valid = True
        except Exception as e:
            st.error(f"Failed to load default CSVs: {str(e)}")
            st.session_state.baby_df = pd.DataFrame()
            st.session_state.baby_source = "Error"
            st.session_state.baby_valid = False
            
            st.session_state.adult_df = pd.DataFrame()
            st.session_state.adult_source = "Error"
            st.session_state.adult_valid = False
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize selected foods
    if "selected_baby_foods" not in st.session_state:
        st.session_state.selected_baby_foods = []
    
    if "selected_adult_foods" not in st.session_state:
        st.session_state.selected_adult_foods = []
    
    # Initialize plan settings
    if "baby_plan_days" not in st.session_state:
        st.session_state.baby_plan_days = 1
    
    if "baby_plan_meals" not in st.session_state:
        st.session_state.baby_plan_meals = 3
    
    if "adult_plan_days" not in st.session_state:
        st.session_state.adult_plan_days = 1
    
    if "adult_plan_meals" not in st.session_state:
        st.session_state.adult_plan_meals = 3
    
    # Initialize generated plans
    if "baby_plan" not in st.session_state:
        st.session_state.baby_plan = pd.DataFrame()
    
    if "adult_plan" not in st.session_state:
        st.session_state.adult_plan = pd.DataFrame()
    
    # Initialize allergen filters
    if "baby_allergen_filter" not in st.session_state:
        st.session_state.baby_allergen_filter = []
    
    if "adult_allergen_filter" not in st.session_state:
        st.session_state.adult_allergen_filter = []
    
    # Initialize nutrient cache
    if "nutrient_cache" not in st.session_state:
        st.session_state.nutrient_cache = {}


def get_active_baby_df() -> pd.DataFrame:
    """Get the current active baby food dataframe."""
    if "baby_df" not in st.session_state:
        initialize_session_state()
    return st.session_state.baby_df


def get_active_adult_df() -> pd.DataFrame:
    """Get the current active adult food dataframe."""
    if "adult_df" not in st.session_state:
        initialize_session_state()
    return st.session_state.adult_df


def update_baby_dataset(df: pd.DataFrame, source: str):
    """Replace the active baby food dataset."""
    st.session_state.baby_df = df
    st.session_state.baby_source = source
    st.session_state.baby_valid = True
    st.session_state.selected_baby_foods = []


def update_adult_dataset(df: pd.DataFrame, source: str):
    """Replace the active adult food dataset."""
    st.session_state.adult_df = df
    st.session_state.adult_source = source
    st.session_state.adult_valid = True
    st.session_state.selected_adult_foods = []


def add_chat_message(role: str, content: str):
    """Add a message to chat history."""
    st.session_state.chat_history.append({"role": role, "content": content})


def get_chat_history() -> list:
    """Get the chat history."""
    if "chat_history" not in st.session_state:
        initialize_session_state()
    return st.session_state.chat_history


def clear_chat_history():
    """Clear the chat history."""
    st.session_state.chat_history = []
