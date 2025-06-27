import os
import streamlit as st

# Find animal sound based on question
def get_animal_sound_file(question):
    known_animals = ["cat", "dog", "cow", "duck", "sheep", "lion"]
    for animal in known_animals:
        if animal in question.lower():
            path = f"static/animal_sounds/{animal}.mp3"
            if os.path.exists(path):
                return path
    return None

# Optional: play celebration sound (from previous features)
def play_success_sound():
    path = "static/sounds/success.mp3"
    if os.path.exists(path):
        with open(path, 'rb') as f:
            st.audio(f.read(), format='audio/mp3')
