import streamlit as st
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from drawing import generate_drawing_with_stability
from sound import get_animal_sound_file

<<<<<<< HEAD
# ------------------------
# 🌍 Setup
# ------------------------
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

=======
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
>>>>>>> 9c4d839ec21a0b5dba88d25f4ed03e6ce51c3238
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

<<<<<<< HEAD
# ------------------------
# 📚 Load KB
# ------------------------
=======
# Load knowledge base answers
>>>>>>> 9c4d839ec21a0b5dba88d25f4ed03e6ce51c3238
def load_answers():
    try:
        with open("answers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

<<<<<<< HEAD
=======
# Match question to KB
>>>>>>> 9c4d839ec21a0b5dba88d25f4ed03e6ce51c3238
def get_answer_from_kb(question, kb):
    for q in kb:
        if q.lower() in question.lower():
            return kb[q]
    return None

<<<<<<< HEAD
# ------------------------
# 🤖 AI Response
# ------------------------
def get_ai_response_openai(question, child_name):
=======
# Get AI answer with child’s name injected
def get_ai_response_openai(question):
    name = st.session_state.get("child_name", "kid")
>>>>>>> 9c4d839ec21a0b5dba88d25f4ed03e6ce51c3238
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            messages=[
                {
                    "role": "system",
<<<<<<< HEAD
                    "content": f"You are a fun and friendly dad helping kids. Always say 'Hi {child_name}!' at the beginning and answer in a playful and kind way."
                },
                {
                    "role": "user",
                    "content": f"My name is {child_name}. {question}"
=======
                    "content": f"You are a fun and friendly dad helping kids. Always greet the child by name like 'Hi {name}!' and answer in a playful and kind way."
                },
                {
                    "role": "user",
                    "content": f"My name is {name}. {question}"
>>>>>>> 9c4d839ec21a0b5dba88d25f4ed03e6ce51c3238
                }
            ],
            extra_headers={
                "HTTP-Referer": "https://askdad.com",
<<<<<<< HEAD
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
=======
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
>>>>>>> 9c4d839ec21a0b5dba88d25f4ed03e6ce51c3238
