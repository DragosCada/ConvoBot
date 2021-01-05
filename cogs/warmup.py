import discord
import os
from discord.ext import commands
import random
import asyncio
from ConvoBot import data_folder, help
from CommonQs import *

class warmup(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.loop = asyncio.get_event_loop()

        self.warmup_task = None #a temp task
        self.task_list = {} #tasks started in each channel {{channel: task},..]

        self.channels_playing = [] #represents all text channels that are playing

        self.random_words = open(data_folder + "/random_words.txt", "r")
        self.random_words = self.random_words.readlines()

        self.channel_vars = {}

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Warmup is online')

    #warmup game
    @commands.command(brief='Start a warm-up game.')
    async def warmup(self, ctx, *, players=None):
        self.task_list[ctx.channel] = {}
        self.task_list[ctx.channel]['warmup_task'] = None

        self.channel_vars[ctx.channel] = {}
        self.channel_vars[ctx.channel]['random_index1'] = random.randint(0, len(self.random_words)-1)
        self.channel_vars[ctx.channel]['random_index2'] = random.randint(0, len(self.random_words)-1)
        self.channel_vars[ctx.channel]['random_index3'] = random.randint(0, len(self.random_words)-1)
        self.channel_vars[ctx.channel]['random_index4'] = random.randint(0, len(self.random_words)-1)

        if players is None:
            await ctx.send(f"Please select one of these options: .warmup 2, .warmup 3, .warmup 4")
            return
        elif (players == '2') or (players == '3') or (players == '4'):
            self.channels_playing.append(ctx.channel) #channel is now playing
        else:
            await ctx.send(f"Please select one of these options: .warmup 2, .warmup 3, .warmup 4")
            return

        if self.task_list[ctx.channel]['warmup_task'] is not None: #resets timer if you .start
            self.task_list[ctx.channel]['warmup_task'].cancel()
            self.task_list[ctx.channel]['warmup_task'] = None

        self.warmup_task = self.loop.create_task(self.warmup_start(ctx, players))

        self.task_list[ctx.channel]['warmup_task'] = self.warmup_task

    #warmup game
    @commands.command(brief='Start a warm-up game.')
    async def warmup_start(self, ctx, players=None):

        await ctx.send(f"Let's get ready to BLURT OUT!")
        await asyncio.sleep(2)

        if players == '2':
            await ctx.send(f"First, choose among yourselves who will be Player 1 and Player 2.")
        elif players == '3':
            await ctx.send(f"First, choose among yourselves who will be Player 1, 2, and 3.")
        elif players == '4':
            await ctx.send(f"First, choose among yourselves who will be Player 1, 2, 3, and 4")

        await asyncio.sleep(7)
        await ctx.send(f"Okay. Player 1, you're up! You have 30 seconds to say anything that comes to mind, starting with this word...")
        await asyncio.sleep(7)
        await ctx.send(f"{self.random_words[self.channel_vars[ctx.channel]['random_index1']]}")
        await asyncio.sleep(3)
        await ctx.send(f"30 seconds on the clock!")
        await asyncio.sleep(20)
        await ctx.send(f"10 seconds on the clock!")
        await asyncio.sleep(7)
        await ctx.send(f"3")
        await asyncio.sleep(1)
        await ctx.send(f"2")
        await asyncio.sleep(1)
        await ctx.send(f"1")
        await asyncio.sleep(1)
        await ctx.send(f"FINISHED")
        await asyncio.sleep(2)
        await ctx.send(f"Player 2, you're next! You have 30 seconds to say anything that comes to mind, starting with this word...")
        await asyncio.sleep(7)
        await ctx.send(f"{self.random_words[self.channel_vars[ctx.channel]['random_index2']]}")
        await asyncio.sleep(3)
        await ctx.send(f"30 seconds on the clock!")
        await asyncio.sleep(20)
        await ctx.send(f"10 seconds on the clock!")
        await asyncio.sleep(7)
        await ctx.send(f"3")
        await asyncio.sleep(1)
        await ctx.send(f"2")
        await asyncio.sleep(1)
        await ctx.send(f"1")
        await asyncio.sleep(1)
        await ctx.send(f"FINISHED")
        await asyncio.sleep(2)

        if (players == '3') or (players == '4'):
            await ctx.send(f"Let's go Player 3! You have 30 seconds to say anything that comes to mind, starting with this word...")
            await asyncio.sleep(7)
            await ctx.send(f"{self.random_words[self.channel_vars[ctx.channel]['random_index3']]}")
            await asyncio.sleep(3)
            await ctx.send(f"30 seconds on the clock!")
            await asyncio.sleep(20)
            await ctx.send(f"10 seconds on the clock!")
            await asyncio.sleep(7)
            await ctx.send(f"3")
            await asyncio.sleep(1)
            await ctx.send(f"2")
            await asyncio.sleep(1)
            await ctx.send(f"1")
            await asyncio.sleep(1)
            await ctx.send(f"FINISHED")
            await asyncio.sleep(2)

            if players == '4':
                await ctx.send(f"And in this corner... we have Player 4! You have 30 seconds to say anything that comes to mind, starting with this word...")
                await asyncio.sleep(7)
                await ctx.send(f"{self.random_words[self.channel_vars[ctx.channel]['random_index4']]}")
                await asyncio.sleep(3)
                await ctx.send(f"30 seconds on the clock!")
                await asyncio.sleep(20)
                await ctx.send(f"10 seconds on the clock!")
                await asyncio.sleep(7)
                await ctx.send(f"3")
                await asyncio.sleep(1)
                await ctx.send(f"2")
                await asyncio.sleep(1)
                await ctx.send(f"1")
                await asyncio.sleep(1)
                await ctx.send(f"FINISHED")
                await asyncio.sleep(2)

        self.loop.create_task(self.fin(ctx))

    @commands.command(brief='End a warm-up game.')
    async def fin(self, ctx):
        if ctx.channel in self.channels_playing:
            if self.task_list[ctx.channel]['warmup_task'] is not None:
                self.task_list[ctx.channel]['warmup_task'].cancel()
                self.task_list[ctx.channel]['warmup_task'] = None
            self.task_list.pop(ctx.channel)
            self.channels_playing.remove(ctx.channel)
        else:
            await ctx.send(f"Wrong command! Please start a new warmup game.")
            return

        await ctx.send(f"Alright, now you're warmed up! Check out the other games.")

        await asyncio.sleep(3)
        self.loop.create_task(help(ctx))

def setup(client):
    client.add_cog(warmup(client))
