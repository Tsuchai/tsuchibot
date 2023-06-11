import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import random
active_games = {}


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

def get_quiz_id(quiz_id: int):
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT quiz_display_name FROM masterQuiz WHERE quiz_id = ?", (quiz_id,))
        result = cursor.fetchone()
        if result is not None:
            quiz_name = result[0]
            return quiz_name
    except Exception as e:
        print(f"Error: {e}")
        return


class QuizInstance:
    def __init__(self, quiz_id: int, qa_tuple: list, channel: discord.TextChannel):
        self.quiz_id = quiz_id
        self.quiz_title = ""
        self.qa_tuple = qa_tuple
        self.questions = []
        self.answers = []
        self.num_questions = 0
        self.question_index = 0
        self.players = {}
        self.channel = channel

    async def load_questions(self):
        self.questions, self.answers = map(list, zip(*self.qa_tuple))
        self.num_questions = len(self.questions)
        self.quiz_title = get_quiz_id(self.quiz_id)

    async def start(self):
        await self.load_questions()
        await self.send_question()

    async def send_question(self):
        question = self.questions[self.question_index]
        embed = discord.Embed(
            title=self.quiz_title,
            description=question,
            color=discord.Color.light_grey()
        )
        await self.channel.send(embed=embed)

    async def process_answer(self, player_id: int, answer: str):
        correct_answer = self.answers[self.question_index]
        if answer.lower() == correct_answer.lower():
            self.update_score(player_id)
            await self.advance_to_next_question()

    async def advance_to_next_question(self):
        self.question_index += 1

        if self.question_index >= self.num_questions:
            #Game over, calculate final score
            await self.end()
        else:
            await self.send_question()

    def update_score(self, player_id: int):
        if player_id in self.players:
            self.players[player_id] += 1
        else:
            self.players[player_id] = 1

    async def end(self):
        high_score_name = await self.high_score()
        embed = discord.Embed(
            title=self.quiz_title,
            description=f"Game over! {high_score_name} won with {max(self.players.values())} points!",
            color=discord.Color.light_grey()
        )
        await self.channel.send(embed=embed)
        if self.channel.id in active_games:
            del active_games[self.channel.id]

    async def high_score(self):
        highest_score = max(self.players.values(), default=0)
        highest_score_players = [player_id for player_id, score in self.players.items() if score == highest_score]

        guild = self.channel.guild

        if len(highest_score_players) == 1:
            player_id = highest_score_players[0]
            player = await guild.fetch_member(player_id)
            return player.mention  # or player.name for just the name

        elif len(highest_score_players) == 2:
            player_ids = highest_score_players[:2]
            player_mentions = []
            for player_id in player_ids:
                player = await guild.fetch_member(player_id)
                player_mentions.append(player.mention)  # or player.name for just the names
            return " and ".join(player_mentions)

        else:
            player_ids = highest_score_players[:-1]
            player_mentions = []
            for player_id in player_ids:
                player = await guild.fetch_member(player_id)
                player_mentions.append(player.mention)  # or player.name for just the names
            return ", ".join(player_mentions) + f", and <@{highest_score_players[-1]}>"











