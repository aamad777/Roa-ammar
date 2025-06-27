import streamlit as st
import os

def play_animal_sound(animal_name):
    animal = animal_name.lower()

    # Map known animals to sound file names
    sound_map = {
        "cat": "cat.mp3",
        "dog": "dog.mp3",
        "lion": "lion.mp3",
        "cow": "cow.mp3",
        "sheep": "sheep.mp3"
    }

    sound_file = sound_map.get(animal)
    if sound_file:
        full_path = f"static/sounds/{sound_file}"
        if os.path.exists(full_path):
            with open(full_path, "rb") as f:
                audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3")
        else:
            st.warning(f"Sound file for {animal} not found.")
    else:
        st.warning("Sorry, I don't have a sound for that animal.")
