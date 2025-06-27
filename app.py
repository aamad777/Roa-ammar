import streamlit as st
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from drawing import generate_drawing_with_stability
from sound import get_animal_sound_file
from dashboard import render_dashboard_tab

# 🌍 Load environment
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

# ------------------------
# 📚 Answer loading
# ------------------------
def load_answers():
    try:
        with open("answers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def load_qa_log():
    if os.path.exists("qa_log.json"):
        with open("qa_log.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_qa_log(data):
    with open("qa_log.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def log_qa(question, answer):
    data = load_qa_log()
    data[question] = answer
    save_qa_log(data)

# ------------------------
# 🤖 AI
# ------------------------
def get_ai_response_openai(question, child_name):
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a fun and friendly dad helping kids. Always say 'Hi {child_name}!' and answer in a playful, kind way."
                },
                {
                    "role": "user",
                    "content": f"My name is {child_name}. {question}"
                }
            ],
            extra_headers={
                "HTTP-Referer": "https://askdad.com",
                "X-Title": "Ask Dad AI"
            }
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI error: {e}"

# ------------------------
# Match to KB
# ------------------------
def get_answer_from_kb(question, kb):
    for q in kb:
        if q.lower() in question.lower():
            return kb[q]
    return None

# ------------------------
# 🌈 UI
# ------------------------
st.set_page_config(page_title="Ask Dad AI", page_icon="👨‍👧‍👦", layout="centered")
st.title("👨‍👧 Ask Dad AI")

tab1, tab2, tab3 = st.tabs([
    "💬 Hi kids! Ask your question",
    "🐾 Which animal would you like to see?",
    "🛠️ Dad's Dashboard"
])

# ------------------------
# 🟦 Tab 1 – Ask a question
# ------------------------
with tab1:
    child_name = st.text_input("👧 What's your name?", value="Jana")
    question = st.text_input("What do you want to ask?")
    option = st.radio("What do you want to do?", ["💬 Just answer", "🎨 Just draw", "💡 Do both"])

    if st.button("✨ Go!", key="go_button"):
        image_data = None
        kb1 = load_answers()
        kb2 = load_qa_log()
        kb = {**kb1, **kb2}

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

        # Save this Q&A to dashboard
        log_qa(question, response_text)

# ------------------------
# 🟩 Tab 2 – Animal Fun
# ------------------------
with tab2:
    st.markdown("Pick your favorite animal and draw it or hear its sound!")

    animals = ["cat", "dog", "lion", "elephant", "monkey", "cow"]
    selected_animal = st.selectbox("🦁 Choose an animal:", animals)

    if "animal_image" not in st.session_state:
        st.session_state.animal_image = None

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎨 Draw this animal"):
            with st.spinner(f"Drawing a {selected_animal}..."):
                image_data, error = generate_drawing_with_stability(selected_animal)
                if image_data:
                    st.session_state.animal_image = image_data
                    st.balloons()
                else:
                    st.error(f"Couldn't draw the {selected_animal}. {error}")

    with col2:
        if st.button("🔊 Hear this animal"):
            sound_file = get_animal_sound_file(selected_animal)
            if sound_file:
                with open(sound_file, "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
            else:
                st.error(f"No sound found for {selected_animal}.")

    if st.session_state.animal_image:
        st.image(st.session_state.animal_image, caption=f"Here's your {selected_animal}! 🎨")

# ------------------------
# 🛠️ Tab 3 – Dashboard
# ------------------------
with tab3:
    render_dashboard_tab()
