import streamlit as st
import json
import os
from datetime import datetime
import random
from dotenv import load_dotenv
from openai import OpenAI
from drawing import generate_drawing_with_stability
from sound import play_animal_sound
from dashboard import render_dashboard_tab
from learn import render_learning_book_tab

from kid_feedback import send_email_to_dad

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
BOOK_FILE = "learning_book.txt"

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

# Load content from learning book if available
def load_learning_book():
    if os.path.exists(BOOK_FILE):
        with open(BOOK_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Search for matching content in the learning book
def search_learning_book(question):
    content = load_learning_book()
    paragraphs = content.split("\n\n")
    for para in paragraphs:
        if question.lower() in para.lower():
            return para.strip()
    return None

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

tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Hi Janas! Ask your question",
    "🐾 Which animal would you like to see?",
    "🛠️ ROA W AMMAR's Dashboard",
    "📚 Learning Book"
])



# TAB 1: Ask ROA W AMMAR
with tab1:
    st.title("👨‍👧 Ask ROA W AMMAR")

    st.text_input("🙋 What's your name?", key="child_name")
    st.text_input("What do you want to ask?", key="question_input")
    st.radio("What do you want to do?", ["💬 Just answer", "🎨 Just draw", "💡 Do both"], key="mode")

    if st.button("✨ Go!", key="ask_btn"):
        if not st.session_state.child_name or not st.session_state.question_input:
            st.warning("Please enter your name and a question.")
        else:
            st.session_state.ask_triggered = True

    if st.session_state.get("ask_triggered"):
        child_name = st.session_state.child_name
        question = st.session_state.question_input
        mode = st.session_state.mode

        book_answer = search_learning_book(question)
        if book_answer:
            answer = book_answer
        else:
            kb1 = load_answers_kb()
            kb2 = load_qa_log_kb()
            kb = {**kb1, **kb2}
            answer = get_answer_from_kb(question, kb)
            if not answer:
                answer = get_ai_response_openai(question, child_name)
                save_question_log(child_name, question, answer)

        if mode in ["💬 Just answer", "💡 Do both"]:
            st.success(f"ROA W AMMAR says: {answer}")

            with st.form(key=f"{child_name}_{question}_form"):
                col1, col2 = st.columns(2)
                yes = col1.form_submit_button("👍 I understand it!")
                no = col2.form_submit_button("👎 I don't understand")

                if yes:
                    a, b = random.randint(1, 3), random.randint(1, 3)
                    st.session_state[f"{child_name}_{question}_quiz"] = f"🍌 What is {a} + {b}?"

                if no:
                    sent, debug = send_email_to_dad(child_name, question)
                    st.session_state[f"{child_name}_{question}_sent"] = sent
                    st.session_state[f"{child_name}_{question}_debug"] = debug

            quiz_key = f"{child_name}_{question}_quiz"
            if quiz_key in st.session_state:
                st.info(st.session_state[quiz_key])

            result_key = f"{child_name}_{question}_sent"
            if result_key in st.session_state:
                if st.session_state[result_key]:
                    st.success("📧 Email sent to Dad!")
                else:
                    st.error("⚠️ Failed to send email.")
                st.code(st.session_state.get(f"{child_name}_{question}_debug", "No debug"))

        if mode in ["🎨 Just draw", "💡 Do both"]:
            with st.spinner("Drawing something fun... 🎨"):
                image = generate_drawing_with_stability(question)
                if image:
                    st.image(image if not isinstance(image, list) else image[0], caption="Your drawing!")
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

    if "animal_image" in st.session_state:
        image = st.session_state["animal_image"]
        if isinstance(image, list):
            st.image(image[0], caption=f"{animal.capitalize()} drawing!")
        else:
            st.image(image, caption=f"{animal.capitalize()} drawing!")

# TAB 3: Dashboard
with tab3:
    render_dashboard_tab()

# TAB 4: Learning Book Upload
with tab4:
    render_learning_book_tab()
