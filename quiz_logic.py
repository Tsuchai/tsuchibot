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
            quiz_name = result[0]
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
            description=f"Game over! These are the ending scores: \n" + await self.high_score_list(),
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

            if highest_score == 1:
                return player.mention + f": {highest_score} point"  # or player.name for just the name
            else:
                return player.mention + f": {highest_score} points"

        elif len(highest_score_players) == 2:
            player_ids = highest_score_players[:2]
            player_mentions = []
            for player_id in player_ids:
                player = await guild.fetch_member(player_id)
                player_mentions.append(player.mention)

            if highest_score == 1:
                return " and ".join(player_mentions) + f": {highest_score} point"
            else:
                return " and ".join(player_mentions) + f": {highest_score} points"


        else:
            player_ids = highest_score_players[:-1]
            player_mentions = []
            for player_id in player_ids:
                player = await guild.fetch_member(player_id)
                player_mentions.append(player.mention)

            if highest_score == 1:
                return ", ".join(player_mentions) + f", and <@{highest_score_players[-1]}>" + f": {highest_score} point"
            else:
                return ", ".join(player_mentions) + f", and <@{highest_score_players[-1]}>" + f": {highest_score} points"

        #use this function in a loop to get every member who participated in the quiz
        #ex: pop first place player, and iterate through until all players have been listed (can dynamically scale this
        #i.e. top 5/10, etc)

    async def high_score_list(self):
        player_list = ""
        player_list_count = 1
        while self.players:
            if player_list_count <= 3:
                unicode_emoji = chr(0x1F947 + player_list_count - 1)
                high_score = await self.high_score()
                player_list += f"{unicode_emoji} {high_score}\n"
                player_list_count += 1
            else:
                high_score = await self.high_score()
                player_list += f"{player_list_count}. {high_score}\n"
                player_list_count += 1
            highest_score_players = [player_id for player_id, score in self.players.items() if
                                     score == max(self.players.values())]
            for player_id in highest_score_players:
                del self.players[player_id]
        return player_list















