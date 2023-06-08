import sqlite3


conn = sqlite3.connect('quiz.db')
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE leaderboard (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        score INTEGER
    );
""")
cursor.execute("""
    CREATE TABLE masterQuiz (
        quiz_id INTEGER PRIMARY KEY,
        quiz_name TEXT
    );
""")

conn.commit()
conn.close()




#def create_quiz_table(quiz_id):
   #conn = sqlite3.connect('quiz.db')