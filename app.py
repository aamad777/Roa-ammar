import streamlit as st
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from drawing import generate_drawing_with_stability

# 🎵 Play sound when drawing is ready
def play_success_sound():
    sound_path = "static/sounds/success.mp3"
    if os.path.exists(sound_path):
        with open(sound_path, 'rb') as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')

# 🌍 Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

# 🤖 Setup OpenAI-compatible client for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

# 📚 Load local knowledge base
def load_answers():
    try:
        with open("answers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading answers:", e)
        return {}

# 🔍 Match user question to known answers
def get_answer_from_kb(question, kb):
    for q in kb:
        if q.lower() in question.lower():
            return kb[q]
    return None

# 💡 Use OpenRouter if no match found
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
                "X-Title": "Ask Dad AI"
            }
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI error: {e}"

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="Ask Dad AI", page_icon="👨‍👧‍👦", layout="centered")
st.title("👨‍👧 Ask Dad AI")
st.markdown("Ask me anything, and I'll try to help you in a fun way!")

# Input
question = st.text_input("What do you want to ask?", key="question_input")

# Option selection
option = st.radio("What do you want to do?", ["💬 Just answer", "🎨 Just draw", "💡 Do both"])

# On click
if st.button("✨ Go!"):
    if question:
        kb = load_answers()
        answer = get_answer_from_kb(question, kb)
        ai_answer = None
        response_text = answer if answer else get_ai_response_openai(question)

        # Show answer
        if option in ["💬 Just answer", "💡 Do both"]:
            st.success(f"💬 Dad says: {response_text}")

        # Draw
        if option in ["🎨 Just draw", "💡 Do both"]:
            with st.spinner("Drawing your idea... 🖌️"):
                image_data, error = generate_drawing_with_stability(response_text)
                if image_data:
                    st.image(image_data, caption="Your AI drawing! 🎨")
                    play_success_sound()
                    st.balloons()
                else:
                    st.error(f"❌ Drawing failed: {error}")
