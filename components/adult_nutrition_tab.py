"""
Tab 3: Adult Nutrition & Meal Prep
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List
from utils.meal_plan import generate_adult_plan


def render_adult_nutrition_tab(adult_df: pd.DataFrame):
    """
    Render the Adult Nutrition & Meal Prep tab.
    """
    st.header("🥗 Adult Nutrition & Meal Prep")
    
    if adult_df.empty:
        st.warning("No adult food data available. Please upload a valid CSV.")
        return
    
    st.info(
        "ℹ️ This tab shows food comparisons and meal planning support only. "
        "These are not personalized dietary or medical recommendations."
    )
    
    # Food selection
    st.subheader("Select Adult Foods")
    
    all_foods = adult_df["food_item"].tolist()
    
    col1, col2 = st.columns(2)
    
    with col1:
        search_text = st.text_input("Search foods", key="adult_food_search")
        if search_text:
            filtered_foods = [f for f in all_foods if search_text.lower() in f.lower()]
        else:
            filtered_foods = all_foods
        
        selected_foods = st.multiselect(
            "Choose foods to analyze",
            filtered_foods,
            key="selected_adult_foods_input"
        )
    
    with col2:
        # Allergen filter
        all_allergens = adult_df["allergen"].unique().tolist()
        allergens_to_exclude = st.multiselect(
            "Exclude foods with allergens",
            sorted([a for a in all_allergens if a != "none"]),
            key="adult_allergen_filter"
        )
    
    # Apply allergen filter
    if allergens_to_exclude:
        filtered_foods = adult_df[~adult_df["allergen"].isin(allergens_to_exclude)]["food_item"].tolist()
        selected_foods = [f for f in selected_foods if f in filtered_foods]
    
    if not selected_foods:
        st.info("Select foods above to see meal prep options.")
        return
    
    matched_foods = selected_foods
    
    st.info("📋 Food information from your dataset. For detailed nutrition data, upload a CSV with nutritional columns or use an external nutrition database.")
    
    # Display food details
    st.subheader("Selected Foods Information")
    
    # Display food details from CSV
    foods_df = adult_df[adult_df["food_item"].isin(matched_foods)][['food_item', 'allergen', 'measurable_quantity']]
    st.dataframe(foods_df, use_container_width=True, hide_index=True)
    
    st.caption("Food information from your uploaded dataset.")
    
    # Meal prep plan
    st.subheader("Adult Meal Prep Plan")
    
    days = st.slider("Number of days", 1, 7, 1, key="adult_days")
    meal_types = st.multiselect(
        "Meal types",
        ["Breakfast", "Lunch", "Dinner", "Snack"],
        default=["Breakfast", "Lunch", "Dinner"],
        key="adult_meal_types"
    )

    if not meal_types:
        st.info("Please choose at least one meal type to build the plan.")
        return
    
    if st.button("Generate Meal Plan", key="gen_adult_plan"):
        plan = generate_adult_plan(matched_foods, adult_df, days, len(meal_types), meal_types=meal_types)
        st.session_state.adult_plan = plan
    
    if not st.session_state.adult_plan.empty:
        st.subheader("Generated Meal Plan")
        st.dataframe(st.session_state.adult_plan[["day", "meal", "recipe_name", "food_item", "measurable_quantity", "allergen"]], use_container_width=True, hide_index=True)

        st.subheader("Daily Breakdown")
        for day in sorted(st.session_state.adult_plan["day"].unique().tolist()):
            day_rows = st.session_state.adult_plan[st.session_state.adult_plan["day"] == day]
            st.write(f"**Day {day}**")
            for meal in meal_types:
                meal_row = day_rows[day_rows["meal"] == meal]
                if not meal_row.empty:
                    recipe_name = meal_row.iloc[0]["recipe_name"]
                    food_items = meal_row.iloc[0]["food_item"]
                    st.write(f"- {meal}: {recipe_name} ({food_items})")
                else:
                    st.write(f"- {meal}: No item selected")
        
        # Editable plan
        edited_plan = st.data_editor(
            st.session_state.adult_plan,
            use_container_width=True,
            key="adult_plan_editor"
        )
        
        # Download plan
        csv_data = edited_plan.to_csv(index=False)
        st.download_button(
            label="📥 Download Meal Plan as CSV",
            data=csv_data,
            file_name="adult_meal_prep_plan.csv",
            mime="text/csv",
            key="download_adult_plan"
        )
