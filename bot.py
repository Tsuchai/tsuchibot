import discord
import responses
import config
import quiz_logic
from quiz_logic import active_games
from discord import app_commands
from discord.ext import commands
import random #for choose commmand
global chatMessage


async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

def run_discord_bot():
    TOKEN = config.token
    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False
    intents.guilds = True
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)



    @bot.event #Message on startup
    async def on_ready():
        print(f'{bot.user} is up!')
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Error syncing commands: {e}")




    @bot.event #Handles message input and debug line
    async def on_message(message):
        if message.author == bot.user:
            return
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        if message.channel.id in quiz_logic.active_games: #game logic messages
            game = quiz_logic.active_games[message.channel.id]
            await game.process_answer(message.author.id, message.content)
        await bot.process_commands(message)

        print(f"{username} said '{user_message}' ({channel})")
        if isinstance(message.channel, discord.DMChannel) or isinstance(message.channel, discord.GroupChannel):
            # Process messages in direct messages or group chats
            await send_message(message, message.content, True)
        else:
            # Process messages in servers
            await send_message(message, message.content, False)






    @bot.tree.command(name="help", description="Gives an overview of the bot") #help command
    async def help(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello {interaction.user.mention}, this is the help menu.", ephemeral=True)

    @bot.tree.command(name="choose", description="Indecisive? Gives a solution via random number generator") #random number generator command
    @app_commands.describe(first_number = "Goes from this number to the other one!", second_number = "The other one!")
    async def choose(interaction: discord.Interaction, first_number: int, second_number: int):
        try:
            if first_number < second_number:
                randomNumber = (random.randint(first_number,second_number))
            else:
                randomNumber = (random.randint(second_number, first_number))
        except Exception as e:
            randomNumber = str("Invalid inputs! Please only put numbers in.")
        await interaction.response.send_message(randomNumber)

    @bot.tree.command(name="quizplay", description="Play a quiz and choose how many questions you want to play!")
    @app_commands.describe(quiz_id = "Id of the quiz you want to play. Use /quizlist if you are unsure.",questions = "Number of questions you want to play.")
    async def start_game(ctx, quiz_id: int, questions: int):
        if ctx.channel.id in quiz_logic.active_games:
            embed = discord.Embed(
                title="Error",
                description="Game already in progress in this channel!",
                color=discord.Color.light_grey()
            )
            await ctx.channel.send(embed=embed)
            return

        quiz_set = quiz_logic.quiz_initialize(quiz_id, questions)
        if len(quiz_set) == 0:
            embed = discord.Embed(
                title="Error",
                description="Invalid quiz ID!",
                color=discord.Color.light_grey()
            )
            await ctx.channel.send(embed=embed)
            return

        game = quiz_logic.QuizInstance(quiz_id, quiz_set, ctx.channel)
        quiz_logic.active_games[ctx.channel.id] = game

        await game.start()



    # @bot.tree.command(name="quizlist", description="Lists the IDs for all the quizzes!")
    # async def list_quizzes(interaction: discord.Interaction):
    #     embed = discord.Embed(
    #         title="Quiz List",
    #         color=discord.Color.random()
    #     ) quiz list stuff

    bot.run(TOKEN)