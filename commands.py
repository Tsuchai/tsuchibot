import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import random


def quiz_initialize(quiz_id: int, questions: int):
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    num_questions = questions
    quiz_name = ""
    try:
        cursor.execute("SELECT quiz_name FROM masterQuiz WHERE quiz_id = ?", (quiz_id,))
        result = cursor.fetchone()
        if result is not None:
            quiz_name=result[0]
    except Exception as e:
        print(f"Error: {e}")
        return
    try:
        cursor.execute(f"SELECT question, answer FROM {quiz_name} ORDER BY random() LIMIT {num_questions}")

    except Exception as e:
        print(f"Error: {e}")
    selected_rows = cursor.fetchall()
    questions = [row[0] for row in selected_rows]
    answers = [row[1] for row in selected_rows]
    qa_tuple = tuple(zip(questions, answers))
    return qa_tuple

print(quiz_initialize(0, 10))



