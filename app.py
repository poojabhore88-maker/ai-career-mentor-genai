import streamlit as st
import os
import json
from openai import OpenAI
from pypdf import PdfReader
import docx

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="AI Career Mentor", layout="wide")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # set in environment
client = OpenAI(api_key="OPENAI_API_KEY")

MEMORY_FILE = "user_memory.json"

# =========================
# MEMORY FUNCTIONS
# =========================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# =========================
# RESUME PARSING
# =========================
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

# =========================
# OPENAI HELPERS
# =========================
def generate_roadmap(resume, role):
    prompt = f"""
You are an AI Career Mentor.

Analyze the following resume and generate a personalized 6-month learning roadmap
for the target role: {role}.

Include:
- Skill gaps
- Learning phases
- Recommended tools/technologies
- Interview preparation tips

Resume:
{resume}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content

def evaluate_answer(question, answer, role):
    prompt = f"""
You are an interview evaluator for the role of {role}.

Evaluate the candidate's answer based on:
- Clarity
- Technical depth
- Structure
- Communication

Question:
{question}

Answer:
{answer}

Provide:
- Strengths
- Weaknesses
- Improvement suggestions
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

# =========================
# UI
# =========================
st.title("🎓 AI Career Mentor & Interview Simulator")
st.write("Personalized career roadmap and role-specific interview preparation using Generative AI.")

memory = load_memory()

# =========================
# ROADMAP SECTION
# =========================
st.header("1️⃣ Career Roadmap Generator")

uploaded_file = st.file_uploader("Upload your resume (PDF / DOCX / TXT)", type=["pdf", "docx", "txt"])
target_role = st.selectbox(
    "Select Target Role",
    ["AI/ML Engineer", "Data Analyst", "Software Engineer", "Product Manager"]
)

resume_text = ""

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        resume_text = read_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        resume_text = read_docx(uploaded_file)
    else:
        resume_text = uploaded_file.read().decode("utf-8")

if st.button("Generate Career Roadmap"):
    if not resume_text:
        st.warning("Please upload a resume.")
    else:
        roadmap = generate_roadmap(resume_text, target_role)
        st.success("Roadmap Generated")
        st.write(roadmap)

        memory["target_role"] = target_role
        memory["roadmap"] = roadmap
        save_memory(memory)

# =========================
# INTERVIEW SECTION
# =========================
st.header("2️⃣ Interview Simulation")

question = st.text_input(
    "Mock Interview Question",
    value="How do you keep your skills updated as an AI/ML Engineer?"
)

answer = st.text_area("Your Answer")

if st.button("Evaluate Answer"):
    if not answer:
        st.warning("Please enter an answer.")
    else:
        feedback = evaluate_answer(question, answer, target_role)
        st.subheader("AI Feedback")
        st.write(feedback)

        memory["last_question"] = question
        memory["last_answer"] = answer
        memory["last_feedback"] = feedback
        save_memory(memory)

# =========================
# AGENT MEMORY DISPLAY
# =========================
st.header("🧠 Mentor Agent Memory")

if memory:
    st.json(memory)
else:
    st.write("No memory stored yet.")

# =========================
# FOOTER
# =========================
st.caption(
    "Prototype inspired by a custom Mentor GPT | Built for ET GenAI Hackathon – Phase 2"
)
