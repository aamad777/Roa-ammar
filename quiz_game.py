
import streamlit as st
import random

def get_quiz_question(category):
    a, b = random.randint(1, 10), random.randint(1, 10)

    if category == "Addition":
        question = f"What is {a} + {b}?"
        answer = a + b
    elif category == "Subtraction":
        a, b = max(a, b), min(a, b)
        question = f"What is {a} - {b}?"
        answer = a - b
    elif category == "Multiplication":
        question = f"What is {a} × {b}?"
        answer = a * b
    elif category == "Division":
        b = random.randint(1, 10)
        a = b * random.randint(1, 10)
        question = f"What is {a} ÷ {b}?"
        answer = int(a / b)
    else:
        question = "Invalid category"
        answer = None

    # Generate options
    options = [answer]
    while len(options) < 3:
        fake = answer + random.choice([-3, -1, 1, 2, 4])
        if fake not in options and fake >= 0:
            options.append(fake)
    random.shuffle(options)

    return question, answer, options
