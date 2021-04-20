import discord
import os
from discord.ext import commands
import random
import asyncio
from ConvoBot import data_folder, help#, disable_cmds
from CommonQs import *

class battle(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.loop = asyncio.get_event_loop()

        self.timer_task = None #Used for timer
        self.battle_task = None #Used for battle game

        self.battle_ques = 0 #index for question list

        #variables used for each channel {chan1:{var1:1,var2:2...},...}
        #vars are intialized in battle_start.
        #keeps track of different users and their variables
        self.channel_vars = {}

        #tasks started in each channel [[channel,[task1,task2,...]],..]
        #keeps track of different users and their tasks
        self.task_list = [] #task1 = battle_start, task2 = timer_task

        self.channels_playing = [] #represents all text channels that are playing

        self.time_for_q = 3 #time to read each question

        self.common_qs = common_qs
        self.gen_com_comments = gen_com_comments

        #used for internal tracking of how many games have been played
        self.battle_metrics = open(data_folder + "/battle_games_started.txt", "r")
        self.battle_metrics = self.battle_metrics.readlines()
        self.battle_games_started = int(self.battle_metrics[0])
        print('battle games started = '+ str(self.battle_games_started))

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Battle is online')

    @commands.command(brief='Start a battle game.')
    async def battle(self, ctx):

        #prevents user from starting a new game without finishing this one
        if ctx.channel in self.channels_playing:
            await ctx.send(f"You're already playing a game!")
            return

        self.channels_playing.append(ctx.channel) #channel is now playing

        for item in self.task_list:   #cancels all tasks for this channel
            if item[0] == ctx.channel:
                if item[1] is not None:
                    item[1].cancel()
                    item[1] = None

        #starts the battle game (timer + questions)
        self.battle_task = self.loop.create_task(self.battle_start(ctx))

        #keeps track of whether battle game is running
        self.task_list.append([ctx.channel,[self.battle_task,None]])

    @commands.command(brief='Start a battle game.')
    async def battle_start(self, ctx):

        #initializing channel vars
        self.channel_vars[ctx.channel] = {}
        self.channel_vars[ctx.channel]['team'] = 'Team 1'
        self.channel_vars[ctx.channel]['battle_qs'] = 15 #number of questions asked.
        self.channel_vars[ctx.channel]['team1_com'] = 0
        self.channel_vars[ctx.channel]['team2_com'] = 0

        self.battle_ques = 0
        self.battle_games_started += 1

        #shuffles all questions
        random.shuffle(self.common_qs)

        await ctx.send(f"Team 1, you're up!")
        await asyncio.sleep(2)
        await ctx.send(f"Ready...")
        await asyncio.sleep(2)
        await ctx.send(f"Set...")
        await asyncio.sleep(2)
        await ctx.send(f"BATTLE!")
        await asyncio.sleep(1)

        await ctx.send(f"{self.common_qs[self.battle_ques][0]}") #first question
        self.channel_vars[ctx.channel]['battle_qs'] -= 1 #asked a question, lower counter

        #time given per question
        await asyncio.sleep(self.time_for_q)

        await ctx.send(f"15 seconds on the clock!")
        self.timer_task = self.loop.create_task(self.battle_timer(ctx)) #starts timer

        #storing timer_task
        for task in self.task_list:
            if task[0] == ctx.channel:
                task[1][1] = self.timer_task

    @commands.command(brief='Team 1 common answer')
    async def com1(self, ctx):

        #prevents user from starting a new game without finishing this one
        if ctx.channel not in self.channels_playing:
            await ctx.send(f"Wrong command. Please start a new battle game.")
            return

        #since com1 is only used for team 1, this prevents team 2 from using it
        if self.channel_vars[ctx.channel]['team'] == 'Team 2':
            await ctx.send(f"Wrong command! Type .com2 for team 2.")
        else:
            #tracks # of common answers
            self.channel_vars[ctx.channel]['team1_com'] += 1
            #increments to next question
            self.battle_ques += 1

            #resetting timer
            for task in self.task_list:
                if task[0] == ctx.channel:
                    if task[1][1] is not None:
                        task[1][1].cancel()
                        task[1][1] = None

            #if all questions have been asked, end game
            if self.channel_vars[ctx.channel]['battle_qs'] <= 0:
                self.loop.create_task(self.end(ctx))
                return

            #if there are no more questions, end game
            if self.battle_ques >= len(self.common_qs):
                await ctx.send(f"WHOOOOO, you finished all the questions!")
                self.loop.create_task(self.end(ctx))
            else:
                #if empty string, use gen_com_comments response.
                if not f"{self.common_qs[self.battle_ques-1][1][0]}":
                    await ctx.send(f"{random.choice(self.gen_com_comments)}")
                #else go to next question
                else:
                    await ctx.send(f"{random.choice(self.common_qs[self.battle_ques-1][1])}")

                await asyncio.sleep(1)
                await ctx.send(f'Team 2!')
                await ctx.send(f"{self.common_qs[self.battle_ques][0]}") #next question
                self.channel_vars[ctx.channel]['battle_qs'] -= 1 #asked a question, lower counter

                #next teams turn to play
                self.channel_vars[ctx.channel]['team'] = 'Team 2'

                await asyncio.sleep(self.time_for_q)
                self.timer_task = self.loop.create_task(self.battle_timer(ctx))

                #storing timer_task
                for task in self.task_list:
                    if task[0] == ctx.channel:
                        task[1][1] = self.timer_task

    @commands.command(brief='Team 2 common answer')
    async def com2(self, ctx):

        #prevents user from starting a new game without finishing this one
        if ctx.channel not in self.channels_playing:
            await ctx.send(f"Wrong command. Please start a new battle game.")
            return

        #since com2 is only used for team 2, this prevents team 1 from using it
        if self.channel_vars[ctx.channel]['team'] == 'Team 1':
            await ctx.send(f"Wrong command! Type .com1 for team 1.")
        else:
            #tracks # of common answers
            self.channel_vars[ctx.channel]['team2_com'] += 1
            #increments to next question
            self.battle_ques += 1

            #resetting timer
            for task in self.task_list:
                if task[0] == ctx.channel:
                    if task[1][1] is not None:
                        task[1][1].cancel()
                        task[1][1] = None

            #if all questions have been asked, end game
            if self.channel_vars[ctx.channel]['battle_qs'] <= 0:
                self.loop.create_task(self.end(ctx))
                return

            #if there are no more questions, end game
            if self.battle_ques >= len(self.common_qs):
                await ctx.send(f"WHOOOOO, you finished all the questions!")
                self.loop.create_task(self.end(ctx))
            else:
                #if empty string, use gen_com_comments response.
                if not f"{self.common_qs[self.battle_ques-1][1][0]}":
                    await ctx.send(f"{random.choice(self.gen_com_comments)}")
                #else go to next question
                else:
                    await ctx.send(f"{random.choice(self.common_qs[self.battle_ques-1][1])}")

                await asyncio.sleep(1)
                await ctx.send(f'Team 1!')
                await ctx.send(f"{self.common_qs[self.battle_ques][0]}") #next question
                self.channel_vars[ctx.channel]['battle_qs'] -= 1 #asked a question, lower counter

                #next teams turn to play
                self.channel_vars[ctx.channel]['team'] = 'Team 1'

                await asyncio.sleep(self.time_for_q)
                self.timer_task = self.loop.create_task(self.battle_timer(ctx))

                #storing timer_task
                for task in self.task_list:
                    if task[0] == ctx.channel:
                        task[1][1] = self.timer_task

    #timer that runs in the background while playing each turn
    @commands.command(pass_context=True)
    async def battle_timer(self, ctx):

        await asyncio.sleep(12)
        await ctx.send("3")
        await asyncio.sleep(1)
        await ctx.send("2")
        await asyncio.sleep(1)
        await ctx.send("1")
        await asyncio.sleep(1)

        #if all questions have been asked, end game
        if self.channel_vars[ctx.channel]['battle_qs'] <= 0:
            return self.loop.create_task(self.end(ctx))

        #changes team when each turn finishes
        if self.channel_vars[ctx.channel]['team'] == 'Team 1':
            await ctx.send(f'Team 2!')
            self.channel_vars[ctx.channel]['team'] = 'Team 2'
        elif self.channel_vars[ctx.channel]['team'] == 'Team 2':
            await ctx.send(f'Team 1!')
            self.channel_vars[ctx.channel]['team'] = 'Team 1'

        self.battle_ques += 1
        await ctx.send(f"{self.common_qs[self.battle_ques][0]}") #next question
        self.channel_vars[ctx.channel]['battle_qs'] -= 1 #asked a question, lower counter
        await asyncio.sleep(3)

        #if still playing, restart timer for new turn
        if ctx.channel in self.channels_playing:
            self.timer_task = self.loop.create_task(self.battle_timer(ctx))

            #storing timer_task
            for task in self.task_list:
                if task[0] == ctx.channel:
                    task[1][1] = self.timer_task

    #stats for keeping track of common answers for each team
    @commands.command(brief='Stats')
    async def battle_stats(self, ctx):
        await ctx.send(f"Team 1: {self.channel_vars[ctx.channel]['team1_com']} commonalities!")
        await ctx.send(f"Team 2: {self.channel_vars[ctx.channel]['team2_com']} commonalities!")

    #ends game manually
    @commands.command(brief='End the battle  game.')
    async def end(self, ctx):

        for item in self.task_list:   #cancels all tasks for this channel
            if item[0] == ctx.channel:
                if item[1][0] is not None: #cancelling battle_start
                    item[1][0].cancel()
                    item[1][0] = None
                if item[1][1] is not None: #cancelling timer
                    item[1][1].cancel()
                    item[1][1] = None

        if ctx.channel in self.channels_playing:
            self.channels_playing.remove(ctx.channel) #removes channel from playing
            self.loop.create_task(self.battle_finish_msg(ctx))
        else:
            #if the channel isn't playing, say this
            await ctx.send(f"Wrong command! Please start a new battle game.")

        for item in list(self.task_list): #remove the channel from the task list
            if item[0] == ctx.channel:
                self.task_list.remove(item)

    @commands.command(brief='Message when you finish the game')
    async def battle_finish_msg(self, ctx):

        await ctx.send(f"FINISHED")
        await asyncio.sleep(1)
        await ctx.send(f"And the winner is...")
        await asyncio.sleep(2)

        if self.channel_vars[ctx.channel]['team1_com'] > self.channel_vars[ctx.channel]['team2_com']:
             await ctx.send(f"Team 1! You had {self.channel_vars[ctx.channel]['team1_com']} commonalities!")
             await asyncio.sleep(2)
             await ctx.send(f"Team 2, you were close! You had {self.channel_vars[ctx.channel]['team2_com']} commonalities.")
        elif self.channel_vars[ctx.channel]['team2_com'] > self.channel_vars[ctx.channel]['team1_com']:
             await ctx.send(f"Team 2! You had {self.channel_vars[ctx.channel]['team2_com']} commonalities!")
             await asyncio.sleep(2)
             await ctx.send(f"Team 1, you were close! You had {self.channel_vars[ctx.channel]['team1_com']} commonalities.")
        else:
            await ctx.send(f"Both teams! It's a tie!")
            await asyncio.sleep(2)
            await ctx.send(f"You both had {self.channel_vars[ctx.channel]['team1_com']} commonalities.")

        await asyncio.sleep(2)
        await ctx.send(f"What did you think of the game? Fill out the polls in the feedback channel!")
        await ctx.send(f"Type .battle to play again.")

        await asyncio.sleep(5)
        self.loop.create_task(help(ctx))

    @commands.command(brief='writes metrics to file')
    async def battlelog(self, ctx):
        await ctx.send(f"Logged! Games so far: {self.battle_games_started}")
        f = open(data_folder + "/battle_games_started.txt", "w+")
        f.write(str(self.battle_games_started))
        f.close()

def setup(client):
    client.add_cog(battle(client))
