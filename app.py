import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from drawing import generate_drawing_with_stability
from sound import play_animal_sound
from dashboard import render_dashboard_tab

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initialize OpenRouter-compatible OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

# File paths
QA_LOG = "qa_log.json"
KB_FILE = "answers.json"

# Make sure QA log exists
if not os.path.exists(QA_LOG):
    with open(QA_LOG, "w", encoding="utf-8") as f:
        json.dump([], f)

# Load answers.json knowledge base
def load_answers_kb():
    try:
        with open(KB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Couldn't load knowledge base: {e}")
        return {}

# Load qa_log.json as knowledge base too
def load_qa_log_kb():
    try:
        with open(QA_LOG, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {item["question"]: item["answer"] for item in data if isinstance(item, dict)}
    except Exception as e:
        st.warning(f"Couldn't load QA log: {e}")
        return {}

# Get match from knowledge base
def get_answer_from_kb(question, kb):
    for q in kb:
        if q.lower() in question.lower():
            return kb[q]
    return None

# Call OpenRouter API for fallback answer
def get_ai_response_openai(question, name):
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a fun and friendly ROA W AMMAR helping a Jana named {name}. Keep answers kind, playful, and short."
                },
                {"role": "user", "content": question}
            ],
            extra_headers={
                "HTTP-Referer": "https://askROA W AMMAR.streamlit.app",
                "X-Title": "Ask ROA W AMMAR"
            }
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI error: {e}"

# Save Q&A to qa_log.json
def save_question_log(name, question, answer):
    try:
        with open(QA_LOG, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = []

    data.append({
        "name": name,
        "question": question,
        "answer": answer,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(QA_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ----------------------------
# UI Starts
# ----------------------------
st.set_page_config(page_title="Ask ROA W AMMAR", page_icon="👨‍👧", layout="centered")

tab1, tab2, tab3 = st.tabs(["💬 Hi Janas! Ask your question", "🐾 Which animal would you like to see?", "🛠️ ROA W AMMAR's Dashboard"])

# TAB 1: Ask ROA W AMMAR
with tab1:
    st.title("👨‍👧 Ask ROA W AMMAR")

    child_name = st.text_input("🙋 What's your name?", key="child_name")

    question = st.text_input("What do you want to ask?", key="question_input")

    mode = st.radio("What do you want to do?", ["💬 Just answer", "🎨 Just draw", "💡 Do both"])

    if st.button("✨ Go!", key="ask_btn"):
        if not child_name or not question:
            st.warning("Please enter your name and a question.")
        else:
            kb1 = load_answers_kb()
            kb2 = load_qa_log_kb()
            kb = {**kb1, **kb2}

            answer = get_answer_from_kb(question, kb)
            if answer:
                response = f"ROA W AMMAR says: {answer}"
            else:
                answer = get_ai_response_openai(question, child_name)
                response = f"ROA W AMMAR says: {answer}"
                save_question_log(child_name, question, answer)

            if mode in ["💬 Just answer", "💡 Do both"]:
                st.success(response)

            if mode in ["🎨 Just draw", "💡 Do both"]:
                with st.spinner("Drawing something fun... 🎨"):
                    image = generate_drawing_with_stability(question)
                    if image:
                        if isinstance(image, list):
                            st.image(image[0], caption="Your drawing!")
                        else:
                            st.image(image, caption="Your drawing!")
                    else:
                        st.error("Oops! Couldn't draw right now. Try again!")

# TAB 2: Animal Sound and Drawing
with tab2:
    st.title("🐾 Pick an animal!")

    animal = st.text_input("Which animal do you like?", key="animal_input")

    col1, col2 = st.columns(2)

    if col1.button("🎨 Draw this animal"):
        if not animal:
            st.warning("Please enter an animal name.")
        else:
            with st.spinner("Drawing your animal..."):
                image = generate_drawing_with_stability(animal)
                if image:
                    st.session_state["animal_image"] = image
                    st.session_state["last_drawn_animal"] = animal
                else:
                    st.error("Could not draw the animal.")

    if col2.button("🔊 Hear animal sound"):
        if not animal:
            st.warning("Please enter an animal name.")
        else:
            with st.spinner("Fetching animal sound..."):
                sound_bytes = play_animal_sound(animal)
                if sound_bytes:
                    st.audio(sound_bytes, format="audio/mp3")
                else:
                    st.error("No sound available for that animal.")

    # Show image if saved
    if "animal_image" in st.session_state:
        image = st.session_state["animal_image"]
        if isinstance(image, list):
            st.image(image[0], caption=f"{animal.capitalize()} drawing!")
        else:
            st.image(image, caption=f"{animal.capitalize()} drawing!")

# TAB 3: Dashboard
with tab3:
    render_dashboard_tab()
