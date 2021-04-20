import discord
import os
from discord.ext import commands
import random
import asyncio
from ConvoBot import data_folder, help
from CommonQs import *

class CommonQs(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.loop = asyncio.get_event_loop()

        self.ques = 0 #represents question (item in list)

        self.common = [] #represents # of common answers in the channel, [[channel, #],...]
        self.temp_com = 0
        self.skips = [] #represents # of skips in the channel, [[channel, #],...]
        self.temp_skips = 0

        self.com_task = None #temp task used for timer
        self.task_list = [] #tasks started in each channel [[channel,task],..]

        self.channels_playing = [] #represents all text channels that are playing

        self.common_qs = common_qs
        self.gen_com_comments = gen_com_comments
        self.gen_skip_comments = gen_skip_comments

        #used for internal tracking of how many games have been played
        self.com_metrics = open(data_folder + "/CommonQ_games_started.txt", "r")
        self.com_metrics = self.com_metrics.readlines()
        self.com_games_started = int(self.com_metrics[0])
        print('CommonQs games started = ' + str(self.com_games_started))

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Common is online')

    @commands.command(brief='Start the game. Also used for restarting.')
    async def start(self, ctx):

        #if channel is already playing
        if ctx.channel in self.channels_playing:
            await ctx.send(f"You're already playing a game!")
            return

        self.channels_playing.append(ctx.channel) #channel is now playing

        #initializing channel vars
        self.ques = 0
        self.common.append([ctx.channel,0])
        self.skips.append([ctx.channel,0])

        self.com_games_started += 1

        for item in self.task_list:   #cancels all tasks for this channel
            if item[0] == ctx.channel:
                if item[1] is not None:
                    item[1].cancel()
                    item[1] = None

        #starts timer and keep track of it in task_list
        self.com_task = self.loop.create_task(self.timer(ctx))
        self.task_list.append([ctx.channel,self.com_task])

        random.shuffle(self.common_qs)

        await ctx.send(f"You got 10 minutes to get as many similarities as possible!")
        await ctx.send(f"{self.common_qs[self.ques][0]}") #first question

    @commands.command(pass_context=True)
    async def timer(self, ctx):
        await asyncio.sleep(60)
        await ctx.send("9 mins left!")
        await asyncio.sleep(60)
        await ctx.send("8 mins left!")
        await asyncio.sleep(60)
        await ctx.send("7 mins left!")
        await asyncio.sleep(60)
        await ctx.send("6 mins left!")
        await asyncio.sleep(60)
        await ctx.send("5 mins left!")
        await asyncio.sleep(60)
        await ctx.send("4 mins left!")
        await asyncio.sleep(60)
        await ctx.send("3 mins left!")
        await asyncio.sleep(60)
        await ctx.send("2 mins left!")
        await asyncio.sleep(60)
        await ctx.send("1 mins left!")
        await asyncio.sleep(30)
        await ctx.send("30 seconds!")
        await asyncio.sleep(20)
        await ctx.send("10 seconds!")
        await asyncio.sleep(7)
        await ctx.send("3")
        await asyncio.sleep(1)
        await ctx.send("2")
        await asyncio.sleep(1)
        await ctx.send("1")
        await asyncio.sleep(1)
        await ctx.send("FINISHED!")
        self.loop.create_task(self.com_finish_msg(ctx))

    #cancels timer and finishes game
    @commands.command(pass_context=True)
    async def stop(self, ctx):

        for item in self.task_list:   #cancels all tasks for this channel
            if item[0] == ctx.channel:
                if item[1] is not None:
                    item[1].cancel()
                    item[1] = None

        #removes channel from playing
        if ctx.channel in self.channels_playing:
            self.channels_playing.remove(ctx.channel)
            await ctx.send("FINISHED!")
            self.loop.create_task(self.com_finish_msg(ctx))
        else:
            #if they aren't playing, wrong command
            await ctx.send(f"Wrong command! Please start a new CommonQs game.")

        for item in list(self.task_list): #remove the channel from the task list
            if item[0] == ctx.channel:
                self.task_list.remove(item)

    @commands.command(brief='For when you have a common answer')
    async def com(self, ctx):

        #increases common answers count by 1
        for item in self.common:
            if item[0] == ctx.channel:
                item[1] += 1

        self.ques += 1

        #prevents user from starting a new game without finishing this one
        if ctx.channel not in self.channels_playing:
            await ctx.send(f"Wrong command. Please start a new CommonQs game.")
            return

        #if all questions have been asked, end game
        if self.ques >= len(self.common_qs):
            await ctx.send(f"WHOOOOO, you finished all the questions!")
            self.loop.create_task(self.stop(ctx))
        else:
            #comment for responding to their answer
            if not f"{self.common_qs[self.ques-1][1][0]}": #if empty string, use gen_com_comments response.
                await ctx.send(f"{random.choice(self.gen_com_comments)}")
            else:
                await ctx.send(f"{random.choice(self.common_qs[self.ques-1][1])}")

            await asyncio.sleep(1)
            await ctx.send(f"{self.common_qs[self.ques][0]}") #next question

    @commands.command(brief='For skipping the question')
    async def skip(self,ctx):

        #increases skiped answers count by 1
        for item in self.skips:
            if item[0] == ctx.channel:
                item[1] += 1

        self.ques += 1

        #prevents user from starting a new game without finishing this one
        if ctx.channel not in self.channels_playing:
            await ctx.send(f"Wrong command. Please start a new CommonQs game.")
            return

        #if all questions have been asked, end game
        if self.ques >= len(self.common_qs):
            await ctx.send(f"WHOOOOO, you finished all the questions!")
            self.loop.create_task(self.stop(ctx))
        else:
            if not f"{self.common_qs[self.ques-1][1][0]}": #if empty string, don't say anything for now
                pass
            else:
                #comment for responding to their answer
                await ctx.send(f"{random.choice(self.common_qs[self.ques-1][1])}")
                await asyncio.sleep(1)
            await ctx.send(f"{self.common_qs[self.ques][0]}")  #next question

    @commands.command(brief='Showing your stats (common and skips) so far')
    async def stats(self, ctx):

        for item in self.common:
            if item[0] == ctx.channel:
                self.temp_com = item[1]

        for item in self.skips:
            if item[0] == ctx.channel:
                self.temp_skips = item[1]

        await ctx.send(f"We got to {self.temp_com} commonalities and {self.temp_skips} skips!")

    @commands.command(brief='Message when you finish the game')
    async def com_finish_msg(self, ctx):
        self.loop.create_task(self.stats(ctx))
        await asyncio.sleep(1)
        await ctx.send(f"What did you think of the game? Fill out the polls in the feedback channel!")
        await ctx.send(f"Type .start to play again.")

        await asyncio.sleep(5)
        self.loop.create_task(help(ctx))

    @commands.command(brief='writes metrics to file')
    async def comlog(self, ctx):
        await ctx.send(f"Logged! Games so far: {self.com_games_started}")
        f = open(data_folder + "/CommonQ_games_started.txt", "w+")
        f.write(str(self.com_games_started))
        f.close()

def setup(client):
    client.add_cog(CommonQs(client))
