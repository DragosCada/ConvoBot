

import discord
import os
from discord.ext import commands
import random
import asyncio

intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)

client = commands.Bot(command_prefix = ".",  intents = intents)
client.remove_command('help')

data_folder = os.path.dirname(os.path.realpath(__file__))

token = open(data_folder + "/token.txt", "r")
token = token.readlines()[0]


@client.command()
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} loaded')

@client.command()
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} unloaded')

@client.command()
@commands.is_owner()
async def reload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} reloaded')

@client.event
async def on_command_error(ctx, error):
     if isinstance(error, commands.MissingRequiredArgument):
         await ctx.send(f'Please fill out the required arguments.')
         return
     raise error


@client.event
async def on_ready():
    print("Bot is ready")


# Commands
@client.command(pass_context=True, aliases=['play'])
async def help(ctx, game=None):

    author = ctx.message.author

    embed = discord.Embed(
        colour = discord.Colour.orange()
    )

    #general help
    if game is None:
        embed.add_field(name='Introduce yourselves!', value='What is your name? How is your day going? What program/year are you in?',inline=False)
        embed.add_field(name='Games available (Type these commands)', value='We recommend you play them in order!',inline=False)
        embed.add_field(name='.play warmup', value='Blurt Out! A short warmup game to get out of your head.',inline=False)
        embed.add_field(name='.play comq', value='CommonQs! Find as many similarities as possible in the span of 10 mins!',inline=False)
        embed.add_field(name='.play battle', value='Meet A Stranger and Battle A Friend! A 2v2 game to see which pair can find more similarities.',inline=False)
        embed.add_field(name='Share this server!', value='Send this to your friends so more people can play: https://discord.com/invite/KWEdfuA',inline=False)

    elif (game == 'commonqs') or (game == 'CommonQs') or (game == 'commonq') or (game == 'Commonqs') or (game == 'commonQs') or (game == 'comqs') or (game == 'comq'):
        embed.set_author(name="CommonQs!")
        embed.add_field(name='How to play', value='The goal is to find as many similarities as possible between each other, in the span of 10 mins. For each question, you should try to find a common answer. Keep answering until you find a common one! If you get one, type .com to go to the next question. If you really cannot find a common one, just type .skip',inline=False)
        embed.add_field(name='.com', value='Use when you get a common answer.',inline=False)
        embed.add_field(name='.skip', value='Allows you to skip questions.',inline=False)
        embed.add_field(name='.start', value='Start a new CommonQs game.',inline=False)
        embed.add_field(name='.stats', value='Shows your stats so far.',inline=False)
        embed.add_field(name='.stop', value='Stop the game and timer.',inline=False)
    elif (game == 'warmup') or (game == 'Warmup') or (game == 'warmUp') or (game == 'WarmUp'):
        embed.set_author(name="Blurt Out!")
        embed.add_field(name='How to play', value='This game is played one person at a time, where you will take turns. If it is your turn, I will give you a random word, and you start saying anything related to that word. Then you say whatever comes to mind for 30 seconds! Just keep talking as much as you can. The other person can help you come up with something if you get stuck. \n \n Ex: POTATO. Answer: Potato, that\'s a funny word I like potatoes, especially french fries, mmmmm man I would die for McDonalds right now also the French is a cool nation their language is kinda jokes, like hon hon hon baguette, know what I mean?',inline=False)
        embed.add_field(name='.warmup #_of_players', value='Start a warm-up game.',inline=False)
        embed.add_field(name='.fin', value='Ends the game early.',inline=False)

    elif (game == 'battle') or (game == 'Battle') or (game == 'BATTLE') or (game == 'bat'):
        embed.set_author(name="Meet A Stranger and Battle A Friend!")
        embed.add_field(name='How to play', value='First, pair up with a stranger, and choose which pair will be team 1 and team 2. Questions will be given, and each pair will have 15 seconds per question to find a common answer between each other. If you get a common answer, type .com1 if you\'re team one and .com2 otherwise. The game goes on for 30 questions, where the team with the most common answers wins! Play fair and have fun!',inline=False)
        embed.add_field(name='.battle', value='Start the game.',inline=False)
        embed.add_field(name='.com1', value='Type when team 1 gets a common answer.',inline=False)
        embed.add_field(name='.com2', value='Type when team 2 gets a common answer.',inline=False)
        embed.add_field(name='.end', value='Ends the game early',inline=False)
    else:
        await ctx.send(f"Please spell the game name right.")

    await ctx.send(embed=embed)


# Shutdowns the bot
@client.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("bye bye")
    await client.logout()

for filename in os.listdir(data_folder + r'/cogs'):
    print(filename)
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
        
client.run(token)
