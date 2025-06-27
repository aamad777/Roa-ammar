import streamlit as st
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from drawing import generate_drawing_with_stability
from sound import get_animal_sound_file

# Session initialization
if "question" not in st.session_state:
    st.session_state.question = ""

if "response_text" not in st.session_state:
    st.session_state.response_text = ""

if "image_data" not in st.session_state:
    st.session_state.image_data = None

if "child_name" not in st.session_state:
    st.session_state.child_name = "Jana"

# Load .env variables
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initialize OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

# Load knowledge base answers
def load_answers():
    try:
        with open("answers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# Match question to KB
def get_answer_from_kb(question, kb):
    for q in kb:
        if q.lower() in question.lower():
            return kb[q]
    return None

# Get AI answer with child’s name injected
def get_ai_response_openai(question):
    name = st.session_state.get("child_name", "kid")
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a fun and friendly dad helping kids. Always greet the child by name like 'Hi {name}!' and answer in a playful and kind way."
                },
                {
                    "role": "user",
                    "content": f"My name is {name}. {question}"
                }
            ],
            extra_headers={
                "HTTP-Referer": "https://askdad.com",
                "X-Title": "Ask ROA W AMMAR"
            }
        )
        if response and response.choices and response.choices[0].message.content:
            return response.choices[0].message.content
        else:
            return f"Hi {name}! Hmm... I couldn't get a good answer from my AI friend."
    except Exception as e:
        return f"AI error: {e}"

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="Ask ROA W AMMAR", page_icon="👨‍👧‍👦", layout="centered")
st.title("👨‍👧 Ask ROA W AMMAR")
st.markdown("Ask me anything, and I'll try to help you in a fun way!")

# Input child name
child_name = st.text_input("👧 What's your name?", value=st.session_state.child_name)
st.session_state.child_name = child_name

# Input question
question = st.text_input("What do you want to ask?", key="question_input")
if question:
    st.session_state.question = question

# Choose action
option = st.radio("What do you want to do?", ["💬 Just answer", "🎨 Just draw", "💡 Do both"])

# Run logic
if st.button("✨ Go!"):
    if st.session_state.question:
        st.session_state.image_data = None
        kb = load_answers()
        answer = get_answer_from_kb(st.session_state.question, kb)
        response_text = answer if answer else get_ai_response_openai(st.session_state.question)
        st.session_state.response_text = response_text

# Show answer
if st.session_state.response_text and option in ["💬 Just answer", "💡 Do both"]:
    st.success(f"💬 ROA W AMMAR says: {st.session_state.response_text}")

# Draw image (one time)
if st.session_state.response_text and option in ["🎨 Just draw", "💡 Do both"]:
    if "AI error" not in st.session_state.response_text:
        if not st.session_state.image_data:
            with st.spinner("Drawing your idea... 🖌️"):
                image_data, error = generate_drawing_with_stability(st.session_state.response_text)
                if image_data:
                    st.session_state.image_data = image_data
                    st.balloons()
                else:
                    st.error(f"❌ Drawing failed: {error}")
        if st.session_state.image_data:
            st.image(st.session_state.image_data, caption="Your AI drawing! 🎨")
    else:
        st.error("❗ I need a real answer before I can draw something!")

# Play animal sound if available
sound_file = get_animal_sound_file(st.session_state.question)
if sound_file:
    if st.button("🔊 Play animal sound!"):
        with open(sound_file, 'rb') as f:
            st.audio(f.read(), format='audio/mp3')
