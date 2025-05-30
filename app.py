import streamlit as st
import google.generativeai as genai
import os

# Google Gemini API Configuration
GOOGLE_API_KEY = "AIzaSyDfKtBHGBeyOrdXa8NpsHU-ThMJ5dFc680"
GEMINI_MODEL_NAME = "gemini-2.5-pro-preview-05-06"
genai.configure(api_key=GOOGLE_API_KEY)

def generate_gemini_content(prompt_text):
    try:
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        st.error(f"Error communicating with Google Gemini API: {e}")
        return "Error: Could not generate content."

# Streamlit UI
st.title("Support Ticket Summarizer 🤖")
st.write("Paste a raw support ticket below, and let the LLM summarize and self-correct.")

ticket_input = st.text_area("Support Ticket Text", height=200)

if st.button("Summarize & Self-Correct"):
    if not ticket_input.strip():
        st.warning("Please enter a support ticket.")
    else:
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY":
            st.error("Please set your Google API Key in the script.")
        else:
            # Phase 1: Initial Summary
            with st.spinner("Generating initial summary..."):
                gen_prompt = f"""
                You are a support assistant. Summarize the following support ticket in 2-3 lines, capturing the core issue and urgency.

                Ticket:
                {ticket_input}
                """
                summary = generate_gemini_content(gen_prompt)

            # Phase 2: Critique and Correction (now with both ticket and summary provided)
            with st.spinner("Critiquing the summary..."):
                critique_prompt = f"""
                You are a quality checker. Review the following support ticket summary in the context of the original ticket. If the summary is vague, incomplete, or misrepresents the ticket, rewrite it to make it clearer and more actionable. Only output the improved summary — no extra explanation.

                Original Ticket:
                {ticket_input}

                Initial Summary:
                "{summary}"
                """
                corrected_summary = generate_gemini_content(critique_prompt)

            # Display corrected summary
            st.subheader("📋 Final Corrected Summary")
            st.success(corrected_summary)

            # Show original summary
            with st.expander("Show Original Summary (before self-correction)"):
                st.write(summary)

            # Analyze issues
            with st.expander("🔍Issues Identified"):

                with st.spinner("Analyzing what was improved..."):
                    analysis_prompt = f"""
                    You are a concise reviewer. Based on the original support ticket, the initial summary, and the corrected summary, list the actual issues found in the initial summary and describe briefly how the corrected version fixed them. Do not mention missing fields that were never present in the ticket. Keep the output short, clear, and in bullet points.

                    Support Ticket:
                    {ticket_input}

                    Initial Summary:
                    "{summary}"

                    Corrected Summary:
                    "{corrected_summary}"
                    """
                    short_critique = generate_gemini_content(analysis_prompt)

                st.markdown("**🛠️ Issues & Fixes:**")
                st.info(short_critique)
