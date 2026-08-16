"""
Tab 1: Food Items - Display food names and provide download options.
"""
import streamlit as st
import pandas as pd
from io import StringIO


def render_food_items_tab(baby_df: pd.DataFrame, adult_df: pd.DataFrame, 
                          baby_source: str, adult_source: str):
    """
    Render the Food Items tab.
    
    Shows searchable lists of baby and adult foods with download options.
    """
    st.header("🍽️ Food Items")
    
    col1, col2 = st.columns(2)
    
    # Baby food section
    with col1:
        st.subheader("Baby Food Items")
        
        if baby_df.empty:
            st.warning("No baby food items available.")
        else:
            # Searchable list
            search_baby = st.text_input("Search baby foods", key="search_baby", label_visibility="collapsed")
            baby_foods = baby_df["food_item"].tolist()
            
            if search_baby:
                baby_foods = [f for f in baby_foods if search_baby.lower() in f.lower()]
            
            # Display as simple list
            for i, food in enumerate(baby_foods, 1):
                st.text(f"{i}. {food}")
            
            if not baby_foods:
                st.info("No matching baby foods found.")
            
            # Download button for complete baby CSV
            csv_data = baby_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Baby Food CSV",
                data=csv_data,
                file_name="baby_food_items_under_12_months.csv",
                mime="text/csv",
                key="download_baby_csv"
            )
            
            st.caption(f"Source: {baby_source}")
    
    # Adult food section
    with col2:
        st.subheader("Adult Food Items")
        
        if adult_df.empty:
            st.warning("No adult food items available.")
        else:
            # Searchable list
            search_adult = st.text_input("Search adult foods", key="search_adult", label_visibility="collapsed")
            adult_foods = adult_df["food_item"].tolist()
            
            if search_adult:
                adult_foods = [f for f in adult_foods if search_adult.lower() in f.lower()]
            
            # Display as simple list
            for i, food in enumerate(adult_foods, 1):
                st.text(f"{i}. {food}")
            
            if not adult_foods:
                st.info("No matching adult foods found.")
            
            # Download button for complete adult CSV
            csv_data = adult_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Adult Food CSV",
                data=csv_data,
                file_name="adult_food_items.csv",
                mime="text/csv",
                key="download_adult_csv"
            )
            
            st.caption(f"Source: {adult_source}")
    
    # Instructions
    st.info("💡 Tip: To upload replacement food lists, use the upload controls in the sidebar.")
