import discord
import responses
import openai
import config
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






    bot.run(TOKEN)