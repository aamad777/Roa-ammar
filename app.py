import streamlit as st
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from drawing import generate_drawing_with_stability
from sound import get_animal_sound_file, play_success_sound

# 🧠 Session state init
if "question" not in st.session_state:
    st.session_state.question = ""

if "response_text" not in st.session_state:
    st.session_state.response_text = ""

if "play_sound_clicked" not in st.session_state:
    st.session_state.play_sound_clicked = False

# 🌍 Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

# 🤖 Setup OpenAI-compatible client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

# 📚 Load answers
def load_answers():
    try:
        with open("answers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# 🔍 Match to local answers
def get_answer_from_kb(question, kb):
    for q in kb:
        if q.lower() in question.lower():
            return kb[q]
    return None

# 🧠 Use OpenRouter if not in KB
def get_ai_response_openai(question):
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            messages=[
                {"role": "system", "content": "You are a fun and friendly dad helping kids. Keep answers simple, kind, and playful."},
                {"role": "user", "content": question}
            ],
            extra_headers={
                "HTTP-Referer": "https://askdad.com",
                "X-Title": "Ask ROA & AMMAR"
            }
        )
        if response and response.choices and response.choices[0].message.content:
            return response.choices[0].message.content
        else:
            return "Hmm... مش عارفين الجواب حنسال احمد ."
    except Exception as e:
        return f"AI error: {e}"

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="Ask Dad AI", page_icon="👨‍👧‍👦", layout="centered")
st.title("👨‍👧 Ask ROA & Ammar")
st.markdown("Ask me anything, and I'll try to help you in a fun way!")

# Question input
question = st.text_input("What do you want to ask?", key="question_input")
if question:
    st.session_state.question = question

# Option selection
option = st.radio("What do you want to do?", ["💬 Just answer", "🎨 Just draw", "💡 Do both"])

# Submit button
if st.button("✨ Go!"):
    if st.session_state.question:
        kb = load_answers()
        answer = get_answer_from_kb(st.session_state.question, kb)
        response_text = answer if answer else get_ai_response_openai(st.session_state.question)
        st.session_state.response_text = response_text
        st.session_state.play_sound_clicked = False  # Reset on new question

# Show response
if st.session_state.response_text and option in ["💬 Just answer", "💡 Do both"]:
    st.success(f"💬 ROA&AMMAR says: {st.session_state.response_text}")

# Show drawing
if st.session_state.response_text and option in ["🎨 Just draw", "💡 Do both"]:
    if "AI error" not in st.session_state.response_text:
        with st.spinner("Drawing your idea... 🖌️"):
            image_data, error = generate_drawing_with_stability(st.session_state.response_text)
            if image_data:
                st.image(image_data, caption="Your AI drawing! 🎨")
                play_success_sound()
                st.balloons()
            else:
                st.error(f"❌ Drawing failed: {error}")
    else:
        st.error("❗ I need a real answer before I can draw something!")

# Animal sound logic
sound_file = get_animal_sound_file(st.session_state.question)

if sound_file:
    if st.button("🔊 Play animal sound!"):
        st.session_state.play_sound_clicked = True

if st.session_state.play_sound_clicked and sound_file:
    with open(sound_file, 'rb') as f:
        st.audio(f.read(), format='audio/mp3')
    st.session_state.play_sound_clicked = False  # Reset to allow re-click
