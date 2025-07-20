import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API key
load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")

# Configure Gemini
client = genai.Client(api_key=API_KEY)
model = "gemini-2.5-pro"

# Prompt builder
def build_content(question: str):
    prompt = f"""You are an expert Python tutor.

Given the coding question below:

\"\"\"{question}\"\"\"

Please:
1. Write a clean Python solution with comments.
2. Explain how it works step-by-step.
3. Generate 3 other related coding questions.

Respond in this format:
---SOLUTION---
<code>

---EXPLANATION---
<text>

---RELATED QUESTIONS---
1.
2.
3.
"""
    return [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        )
    ]

# Parser
def parse_sections(text: str):
    sections = {"solution": "", "explanation": "", "related": ""}
    current = None
    for line in text.splitlines():
        if line.startswith("---SOLUTION---"):
            current = "solution"
        elif line.startswith("---EXPLANATION---"):
            current = "explanation"
        elif line.startswith("---RELATED QUESTIONS---"):
            current = "related"
        elif current:
            sections[current] += line + "\n"
    return sections

# Streamlit UI
st.set_page_config(page_title="🧑‍🏫 AI Coding Tutor", layout="wide")
st.title("🧑‍🏫 AI Coding Tutor - Gemini 2.5 Pro")

question = st.text_area("Enter a coding question:", height=200)

if st.button("Generate Answer"):
    if not question.strip():
        st.warning("Please enter a valid coding question.")
    else:
        with st.spinner("Thinking..."):
            try:
                contents = build_content(question)

                tools = [types.Tool(googleSearch=types.GoogleSearch())]
                config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=-1),
                    tools=tools,
                    response_mime_type="text/plain",
                )

                full_text = ""
                for chunk in client.models.generate_content_stream(
                    model=model, contents=contents, config=config
                ):
                    full_text += chunk.text

                result = parse_sections(full_text)

                st.markdown("### ✅ Solution")
                st.code(result["solution"], language="python")

                st.markdown("### 🧠 Explanation")
                st.write(result["explanation"])

                st.markdown("### ❓ 3 Related Questions")
                st.markdown(result["related"])

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
