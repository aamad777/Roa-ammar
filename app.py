import streamlit as st
import json
import os
import random
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from drawing import generate_drawing_with_stability
from sound import play_animal_sound
from dashboard import render_dashboard_tab
from learn import render_learning_book_tab
from kid_feedback import send_email_to_dad
from quiz_game import get_quiz_question
from quiz_sounds import play_correct_sound, play_wrong_sound, play_win_sound
from quiz_scoreboard import log_score, show_scoreboard

# Load environment
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)

QA_LOG = "qa_log.json"
KB_FILE = "answers.json"
BOOK_FILE = "learning_book.txt"

def load_answers_kb():
    try:
        with open(KB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def load_qa_log_kb():
    try:
        with open(QA_LOG, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {item["question"]: item["answer"] for item in data if isinstance(item, dict)}
    except:
        return {}

def load_learning_book():
    if os.path.exists(BOOK_FILE):
        with open(BOOK_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def search_learning_book(question):
    content = load_learning_book()
    for para in content.split("\n\n"):
        if question.lower() in para.lower():
            return para.strip()
    return None

def get_answer_from_kb(question, kb):
    for q in kb:
        if q.lower() in question.lower():
            return kb[q]
    return None

def get_ai_response_openai(question, name):
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant for a child named {name}."},
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

# Set layout
st.set_page_config(page_title="Ask ROA W AMMAR", layout="wide")

# Sidebar navigation
st.sidebar.title("📚 ROA W AMMAR Navigation")
tab = st.sidebar.radio("Choose a tab:", [
    "💬 Ask ROA W AMMAR",
    "🐾 Animal Fun",
    "🛠️ Dad's Dashboard",
    "📚 Learning Book",
    "🧠 Quiz Fun",
    "📊 Scoreboard"
])

if tab == "💬 Ask ROA W AMMAR":
    st.title("👨‍👧 Ask ROA W AMMAR")
    st.text_input("🙋 What's your name?", key="child_name")
    st.text_input("❓ What do you want to ask?", key="question_input")
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
            kb = {**load_answers_kb(), **load_qa_log_kb()}
            answer = get_answer_from_kb(question, kb)
            if not answer:
                answer = get_ai_response_openai(question, child_name)
                save_question_log(child_name, question, answer)

        if mode in ["💬 Just answer", "💡 Do both"]:
            st.success(f"ROA W AMMAR says: {answer}")
            with st.form(key=f"{child_name}_{question}_form"):
                col1, col2 = st.columns(2)
                yes = col1.form_submit_button("👍 I understand it!")
                no = col2.form_submit_button(":( not clear ask dady help 📩)")
                if yes:
                    a, b = random.randint(1, 3), random.randint(1, 3)
                    st.info(f"🍌 Fruit Quiz: What is {a} + {b}?")
                if no:
                    sent, debug = send_email_to_dad(child_name, question, answer)
                    if sent:
                        st.success("📧 Email sent to Dad!")
                    else:
                        st.error("⚠️ Failed to send email.")
                    with st.expander("🔍 Debug Info"):
                        st.code(debug)

        if mode in ["🎨 Just draw", "💡 Do both"]:
            with st.spinner("Drawing something fun... 🎨"):
                image = generate_drawing_with_stability(question)
                if image:
                    st.image(image if not isinstance(image, list) else image[0], caption="Your drawing!")
                else:
                    st.error("Oops! Couldn't draw right now.")

elif tab == "🐾 Animal Fun":
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
                    st.image(image if not isinstance(image, list) else image[0], caption=f"{animal.capitalize()} drawing!")
                else:
                    st.error("Could not draw the animal.")
    if col2.button("🔊 Hear animal sound"):
        if not animal:
            st.warning("Please enter an animal name.")
        else:
            with st.spinner("Fetching sound..."):
                sound_bytes = play_animal_sound(animal)
                if sound_bytes:
                    st.audio(sound_bytes, format="audio/mp3")
                else:
                    st.error("No sound available.")

elif tab == "🛠️ Dad's Dashboard":
    render_dashboard_tab()

elif tab == "📚 Learning Book":
    render_learning_book_tab()

elif tab == "🧠 Quiz Fun":
    st.title("🧠 Fun Quiz Time!")
    name = st.text_input("👧 What's your name?", key="quiz_name")
    category = st.selectbox("📚 Choose a quiz type:", ["Addition", "Subtraction", "Multiplication", "Division"])

    if name:
        if "quiz_score" not in st.session_state:
            st.session_state.quiz_score = 0
        if "quiz_round" not in st.session_state:
            st.session_state.quiz_round = 1
        if "quiz_done" not in st.session_state:
            st.session_state.quiz_done = False
        if "quiz_question" not in st.session_state:
            q, a, opts = get_quiz_question(category)
            st.session_state.quiz_question = q
            st.session_state.quiz_answer = a
            st.session_state.quiz_options = opts

        if st.session_state.quiz_round <= 5:
            st.markdown(f"### ❓ Round {st.session_state.quiz_round}: {st.session_state.quiz_question}")
            cols = st.columns(len(st.session_state.quiz_options))

            for i, option in enumerate(st.session_state.quiz_options):
                if cols[i].button(f"{option}", key=f"option_{st.session_state.quiz_round}_{option}"):
                    if option == st.session_state.quiz_answer:
                        st.session_state.quiz_score += 1
                        st.success("🎉 Correct! You're a math star!")
                        play_correct_sound()
                        st.image("https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif", width=200)
                    else:
                        st.error(f"😢 Oops! The correct answer was {st.session_state.quiz_answer}.")
                        play_wrong_sound()
                        st.image("https://media.giphy.com/media/9Y5BbDSkSTiY8/giphy.gif", width=200)

                    st.session_state.quiz_round += 1
                    if st.session_state.quiz_round <= 5:
                        q, a, opts = get_quiz_question(category)
                        st.session_state.quiz_question = q
                        st.session_state.quiz_answer = a
                        st.session_state.quiz_options = opts
                    else:
                        st.session_state.quiz_done = True

        st.progress((st.session_state.quiz_round - 1) / 5)

        if st.session_state.quiz_done:
            st.balloons()
            st.markdown(f"## 🎊 Great job, {name}!")
            st.markdown(f"You scored **{st.session_state.quiz_score} out of 5**! ⭐")
            stars = "⭐" * st.session_state.quiz_score + "☆" * (5 - st.session_state.quiz_score)
            st.markdown(f"### {stars}")
            st.image("https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif", width=300)
            play_win_sound()
            log_score(name, st.session_state.quiz_score)

            if st.button("🔁 Play Again"):
                for key in list(st.session_state.keys()):
                    if key.startswith("quiz_"):
                        del st.session_state[key]
                st.experimental_rerun()

elif tab == "📊 Scoreboard":
    st.title("📊 Quiz Scoreboard")
    show_scoreboard()