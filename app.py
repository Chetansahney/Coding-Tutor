import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
#from google.genai import types
from dotenv import load_dotenv
load_dotenv()  # This loads environment variables from .env

# Configure Gemini
api = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api)

# Initialize the model properly
model = genai.GenerativeModel(model_name="gemini-2.5-pro")

def get_gemini_solution(prompt_text):
    try:
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        return f"❌ Error: {e}"

# -------------------- UI ---------------------
st.set_page_config(page_title="Tutor + OA Practice", layout="wide")
st.title("🧠 AI Coding Tutor + 💼 Company-wise OA Practice")

# -------------------- Toggle Ask Tutor ---------------------
if st.toggle("✍️ Ask Tutor"):
    question = st.text_area("Ask your coding question:", height=200)
    if st.button("💬 Ask Tutor"):
        if not question.strip():
            st.warning("Please enter a valid question.")
        else:
            with st.spinner("Tutor is solving..."):
                prompt = f"""You are a Python tutor. Given this question:
\"\"\"{question}\"\"\"

Do the following:
1. Write clean Python code with comments.
2. Explain the logic step-by-step.
3. Generate 3 related problems.

Respond in this format:
---SOLUTION---
<code>

---EXPLANATION---
<text>

---RELATED QUESTIONS---
1.
2.
3.
4
"""
                st.markdown(get_gemini_solution(prompt))

# -------------------- OA Question Section ---------------------
st.subheader("💼 Company-Specific OA LeetCode Practice")

company_files = {
    "Amazon": "amazon_alltime.csv",
    "Adobe": "adobe_alltime.csv",
    "Google": "google_alltime.csv",
    "Microsoft": "microsoft_alltime.csv",
    "IBM": "ibm_alltime.csv",
    "Facebook": "facebook_alltime.csv",
    "Apple": "apple_alltime.csv",
    "Goldman Sachs": "goldman-sachs_alltime.csv",
    "Flipkart": "flipkart_alltime.csv",
    "Uber": "uber_alltime.csv",
    "JPMorgan Chase": "jpmorgan_alltime.csv"
}

company = st.selectbox("Select a company:", list(company_files.keys()))

@st.cache_data
def load_data(name):
    df = pd.read_csv(company_files[name])
    df = df.dropna(subset=["Title", "Leetcode Question Link"])
    if "ID" not in df.columns:
        df["ID"] = range(1, len(df) + 1)
    return df

df = load_data(company)

if st.button("🎯 Show 10 Random OA Questions"):
    sample = df.sample(n=10) if len(df) > 10 else df
    st.session_state["oa_questions"] = sample.reset_index(drop=True)

if "oa_questions" in st.session_state:
    for i, row in st.session_state["oa_questions"].iterrows():
        with st.expander(row["Title"]):
            st.markdown(f"🔗 [View on LeetCode]({row['Leetcode Question Link']})")

            show_solution_key = f"show_solution_{i}"
            if st.button("💡 Show Solution & Explanation", key=show_solution_key):
                st.session_state[f"show_solution_triggered_{i}"] = True

            if st.session_state.get(f"show_solution_triggered_{i}", False):
                with st.spinner("Gemini is solving..."):
                    prompt = f"Solve this LeetCode coding problem and explain it clearly:\n\n\"{row['Title']}\""
                    response = get_gemini_solution(prompt)
                    st.markdown(response)


        