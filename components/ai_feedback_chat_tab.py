"""
Tab 4: AI Feedback Chat
"""
import streamlit as st
import pandas as pd
from typing import List
from utils.llm_agent import get_groq_agent, is_groq_available, parse_feedback_preferences
from utils.feedback_store import append_feedback_entry, get_feedback_file_content
from utils.meal_plan import generate_baby_plan, generate_adult_plan


def render_ai_feedback_chat_tab(baby_df: pd.DataFrame, adult_df: pd.DataFrame):
    """
    Render the AI Feedback Chat tab.
    """
    st.header("🤖 AI Feedback Chat")
    
    st.info(
        "💬 Provide feedback about your meal plans here. The AI will suggest "
        "improvements based on your preferences, dietary needs, and food choices."
    )
    
    # Plan type selection
    plan_type = st.radio(
        "Select which plan to modify",
        ["Baby", "Adult"],
        horizontal=True,
        key="feedback_plan_type"
    )
    
    if plan_type == "Baby":
        current_df = baby_df
        current_plan = st.session_state.baby_plan
        all_foods = baby_df["food_item"].tolist() if not baby_df.empty else []
    else:
        current_df = adult_df
        current_plan = st.session_state.adult_plan
        all_foods = adult_df["food_item"].tolist() if not adult_df.empty else []
    
    if current_df.empty or all_foods is None:
        st.warning(f"No {plan_type.lower()} food data available.")
        return
    
    if all_foods is None or len(all_foods) == 0:
        st.warning("No foods available for feedback.")
        return
    
    # Inclusion and exclusion controls
    st.subheader("Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        inclusions = st.multiselect(
            "Foods to INCLUDE",
            all_foods,
            key=f"inclusions_{plan_type}"
        )
    
    with col2:
        exclusions = st.multiselect(
            "Foods to EXCLUDE",
            [f for f in all_foods if f not in inclusions],
            key=f"exclusions_{plan_type}"
        )
    
    # Chat interface
    st.subheader("Feedback Message")
    
    # Display chat history
    if st.session_state.chat_history:
        with st.expander("💬 Chat History", expanded=False):
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.write(f"**You:** {msg['content']}")
                else:
                    st.write(f"**Assistant:** {msg['content']}")
    
    # User input
    user_feedback = st.text_area(
        "Type your feedback here",
        placeholder="e.g., 'Can we add more vegetables?' or 'Reduce dairy options.'",
        key="feedback_input"
    )
    
    # Process feedback button
    if st.button("Send Feedback", key="send_feedback_btn"):
        if not user_feedback.strip():
            st.warning("Please enter feedback before sending.")
        elif current_plan.empty:
            st.warning(f"Please generate a {plan_type.lower()} meal plan first.")
        else:
            parsed_feedback = parse_feedback_preferences(user_feedback, all_foods)
            resolved_inclusions = list(dict.fromkeys(inclusions + parsed_feedback["include"]))
            resolved_exclusions = list(dict.fromkeys(exclusions + parsed_feedback["exclude"]))

            # Add user message to chat
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_feedback
            })

            # Process with AI
            groq_agent = get_groq_agent()

            if is_groq_available():
                with st.spinner("Processing feedback with AI..."):
                    plan_dict = current_plan.to_dict("records")

                    response = groq_agent.process_feedback(
                        plan_type,
                        plan_dict,
                        all_foods,
                        current_plan["food_item"].unique().tolist() if not current_plan.empty else [],
                        resolved_inclusions,
                        resolved_exclusions,
                        user_feedback
                    )

                    if response:
                        approved_foods = response.get("approved_food_items", [])
                        excluded_foods = list(dict.fromkeys(resolved_exclusions + response.get("excluded_food_items", [])))

                        if approved_foods:
                            if plan_type == "Baby":
                                new_plan = generate_baby_plan(
                                    approved_foods,
                                    baby_df,
                                    st.session_state.baby_plan_days if not st.session_state.baby_plan.empty else 1,
                                    st.session_state.baby_plan_meals if not st.session_state.baby_plan.empty else 3,
                                    excluded_foods
                                )
                                st.session_state.baby_plan = new_plan
                            else:
                                new_plan = generate_adult_plan(
                                    approved_foods,
                                    adult_df,
                                    st.session_state.adult_plan_days if not st.session_state.adult_plan.empty else 1,
                                    st.session_state.adult_plan_meals if not st.session_state.adult_plan.empty else 3,
                                    excluded_foods
                                )
                                st.session_state.adult_plan = new_plan
                        elif resolved_inclusions or resolved_exclusions:
                            if plan_type == "Baby":
                                new_plan = generate_baby_plan(
                                    resolved_inclusions if resolved_inclusions else all_foods,
                                    baby_df,
                                    st.session_state.baby_plan_days if not st.session_state.baby_plan.empty else 1,
                                    st.session_state.baby_plan_meals if not st.session_state.baby_plan.empty else 3,
                                    resolved_exclusions
                                )
                                st.session_state.baby_plan = new_plan
                            else:
                                new_plan = generate_adult_plan(
                                    resolved_inclusions if resolved_inclusions else all_foods,
                                    adult_df,
                                    st.session_state.adult_plan_days if not st.session_state.adult_plan.empty else 1,
                                    st.session_state.adult_plan_meals if not st.session_state.adult_plan.empty else 3,
                                    resolved_exclusions
                                )
                                st.session_state.adult_plan = new_plan

                        ai_response = response.get("summary", "Plan updated.")
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": ai_response
                        })

                        append_feedback_entry(
                            plan_type,
                            user_feedback,
                            approved_foods if approved_foods else resolved_inclusions,
                            excluded_foods,
                            bool(approved_foods or resolved_inclusions or excluded_foods)
                        )

                        st.success("Feedback processed! Plan updated.")
                    else:
                        st.warning("AI processing failed. Updating plan with your selections and typed preferences only.")

                        if resolved_inclusions or resolved_exclusions:
                            if plan_type == "Baby":
                                new_plan = generate_baby_plan(
                                    resolved_inclusions if resolved_inclusions else all_foods,
                                    baby_df,
                                    st.session_state.baby_plan_days if not st.session_state.baby_plan.empty else 1,
                                    st.session_state.baby_plan_meals if not st.session_state.baby_plan.empty else 3,
                                    resolved_exclusions
                                )
                                st.session_state.baby_plan = new_plan
                            else:
                                new_plan = generate_adult_plan(
                                    resolved_inclusions if resolved_inclusions else all_foods,
                                    adult_df,
                                    st.session_state.adult_plan_days if not st.session_state.adult_plan.empty else 1,
                                    st.session_state.adult_plan_meals if not st.session_state.adult_plan.empty else 3,
                                    resolved_exclusions
                                )
                                st.session_state.adult_plan = new_plan

                        append_feedback_entry(
                            plan_type,
                            user_feedback,
                            resolved_inclusions,
                            resolved_exclusions,
                            False
                        )
            else:
                st.warning(
                    "⚠️ Groq API not configured. Using deterministic plan updates based on your selections and typed feedback."
                )

                if resolved_inclusions or resolved_exclusions:
                    if plan_type == "Baby":
                        new_plan = generate_baby_plan(
                            resolved_inclusions if resolved_inclusions else all_foods,
                            baby_df,
                            st.session_state.baby_plan_days if not st.session_state.baby_plan.empty else 1,
                            st.session_state.baby_plan_meals if not st.session_state.baby_plan.empty else 3,
                            resolved_exclusions
                        )
                        st.session_state.baby_plan = new_plan
                    else:
                        new_plan = generate_adult_plan(
                            resolved_inclusions if resolved_inclusions else all_foods,
                            adult_df,
                            st.session_state.adult_plan_days if not st.session_state.adult_plan.empty else 1,
                            st.session_state.adult_plan_meals if not st.session_state.adult_plan.empty else 3,
                            resolved_exclusions
                        )
                        st.session_state.adult_plan = new_plan

                append_feedback_entry(
                    plan_type,
                    user_feedback,
                    resolved_inclusions,
                    resolved_exclusions,
                    bool(resolved_inclusions or resolved_exclusions)
                )

                st.success("Plan updated based on your selections and typed feedback.")

            st.rerun()
    
    # Display updated plan
    if plan_type == "Baby" and not st.session_state.baby_plan.empty:
        st.subheader("Updated Baby Meal Plan")
        st.dataframe(st.session_state.baby_plan, use_container_width=True, hide_index=True)
    elif plan_type == "Adult" and not st.session_state.adult_plan.empty:
        st.subheader("Updated Adult Meal Plan")
        st.dataframe(st.session_state.adult_plan, use_container_width=True, hide_index=True)
    
    # Feedback log download
    st.subheader("Feedback Audit Log")
    
    feedback_content = get_feedback_file_content()
    
    st.download_button(
        label="📥 Download Feedback Log",
        data=feedback_content,
        file_name="feedback.txt",
        mime="text/plain",
        key="download_feedback"
    )
    
    if feedback_content:
        with st.expander("View Feedback Log", expanded=False):
            st.text(feedback_content)
