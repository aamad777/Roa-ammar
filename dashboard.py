import streamlit as st
import os
import json

QA_FILE = "qa_log.json"

def load_qa_log():
    if os.path.exists(QA_FILE):
        with open(QA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_qa_log(data):
    with open(QA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def render_dashboard_tab():
    st.header("🛠️ Dad's Dashboard")
    st.markdown("View or edit past questions, and add new ones for the future.")

    qa_data = load_qa_log()
    updated = False

    # ----------------------
    # ✏️ Add New Q&A
    # ----------------------
    with st.expander("➕ Add a new question and answer"):
        new_question = st.text_input("New Question", key="new_q")
        new_answer = st.text_area("Answer", key="new_a")
        if st.button("✅ Add to Knowledge Base"):
            if new_question.strip() and new_answer.strip():
                qa_data[new_question.strip()] = new_answer.strip()
                save_qa_log(qa_data)
                st.success("New Q&A added!")
            else:
                st.error("Please fill in both question and answer.")

    # ----------------------
    # 📜 View/Edit Existing Q&A
    # ----------------------
    if not qa_data:
        st.info("No questions logged yet.")
    else:
        st.subheader("🗂️ Existing Questions")
        for idx, (question, answer) in enumerate(qa_data.items()):
            with st.expander(f"❓ {question}"):
                new_answer = st.text_area("✏️ Edit Answer:", value=answer, key=f"edit_{idx}")
                if new_answer != answer:
                    qa_data[question] = new_answer
                    updated = True

    if updated:
        if st.button("💾 Save All Changes", key="save_dashboard"):
            save_qa_log(qa_data)
            st.success("All updates saved!")
