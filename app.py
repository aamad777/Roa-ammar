import streamlit as st
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from drawing import generate_drawing_with_stability
from sound import get_animal_sound_file

# ------------------------
# 🌍 Setup
# ------------------------
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

# ------------------------
# 📚 Load KB
# ------------------------
def load_answers():
    try:
        with open("answers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def get_answer_from_kb(question, kb):
    for q in kb:
        if q.lower() in question.lower():
            return kb[q]
    return None

# ------------------------
# 🤖 AI Response
# ------------------------
def get_ai_response_openai(question, child_name):
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a fun and friendly dad helping kids. Always say 'Hi {child_name}!' at the beginning and answer in a playful and kind way."
                },
                {
                    "role": "user",
                    "content": f"My name is {child_name}. {question}"
                }
            ],
            extra_headers={
                "HTTP-Referer": "https://askdad.com",
                "X-Title": "Ask ROA W Ammar"
            }
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI error: {e}"

# ------------------------
# 🎨 UI
# ------------------------
st.set_page_config(page_title="Ask ROA W AMMAR", page_icon="👨‍👧‍👦", layout="centered")
st.title("👨‍👧 Ask ROA W AMMAR")

tab1, tab2 = st.tabs(["💬 Hi JANA! Ask your question", "🐾 Which animal would you like to see JANA?"])

# ------------------------
# 🟦 Tab 1: Ask a question
# ------------------------
with tab1:
    child_name = st.text_input("👧 What's your name?", value="")
    question = st.text_input("What do you want to ask?")
    option = st.radio("What do you want to do?", ["💬 Just answer", "🎨 Just draw", "💡 Do both"])
    
    if st.button("✨ Go!", key="go_button"):
        image_data = None
        kb = load_answers()
        answer = get_answer_from_kb(question, kb)
        response_text = answer if answer else get_ai_response_openai(question, child_name)
        
        if option in ["💬 Just answer", "💡 Do both"]:
            st.success(f"💬 Dad says: {response_text}")
        
        if option in ["🎨 Just draw", "💡 Do both"]:
            with st.spinner("Drawing your idea... 🖌️"):
                image_data, error = generate_drawing_with_stability(response_text)
                if image_data:
                    st.image(image_data, caption="Your AI drawing! 🎨")
                    st.balloons()
                else:
                    st.error(f"❌ Drawing failed: {error}")
        
        sound_file = get_animal_sound_file(question)
        if sound_file:
            if st.button("🔊 Play animal sound!", key="sound_from_question"):
                with open(sound_file, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")

# ------------------------
# 🟩 Tab 2: Pick an animal
# ------------------------
with tab2:
    st.markdown("Pick your favorite animal and draw it or hear its sound!")

    animals = ["cat", "dog", "bird", "pinguin", "monkey", "cow"]
    selected_animal = st.selectbox("🦁 Choose an animal:", animals)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎨 Draw this animal"):
            with st.spinner(f"Drawing a {selected_animal}..."):
                image_data, error = generate_drawing_with_stability(selected_animal)
                if image_data:
                    st.image(image_data, caption=f"Here’s your {selected_animal}! 🎨")
                else:
                    st.error(f"Couldn't draw the {selected_animal}. {error}")

    with col2:
        if st.button("🔊 Hear this animal"):
            sound_file = get_animal_sound_file(selected_animal)
            if sound_file:
                with open(sound_file, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
            else:
                st.error(f"Sorry, no sound for {selected_animal} yet!")
