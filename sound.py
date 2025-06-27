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

