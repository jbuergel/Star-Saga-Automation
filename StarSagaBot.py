#!/usr/bin/python
# -*- coding: utf-8 -*-

# StarSagaBot: The controlling bot for Star Saga automation, which handles
# the Discord integration as well as creating the virtualbox automation.
# Copyright (c) 2012-24 Joshua Buergel <jbuergel@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import time
import yaml
import logging
import asyncio

from StarSagaAuto import StarSagaAuto
import discord
from discord.ext import commands

#####################################################
# StarSagaBot keeps track of all of our other state, as well as containing the automation

class StarSagaBot():
    auto = None
    current_user = None
    current_user_name = None
    users = None

    def __init__(self, token, users, vboxpath):
        logging.basicConfig(filename='Logs/starsagabot.log', level=logging.INFO)
        logging.info('Constructing star saga bot.')
        self.users = users
        self.auto = StarSagaAuto(vboxpath)
        self.auto.start_star_saga()
        self.token = token
        self.lock = asyncio.Lock()
        logging.info('Completed constructing star saga bot.')

    def stop_system(self):
        logging.info('Stopping star saga bot.')
        self.auto.stop_star_saga()
        logging.info('Completed stopping star saga bot.')

    def validate_user(self, user, function_name):
        logging.info('Function entry: {0}, {1}'.format(function_name, user))
        if user not in self.users: 
            logging.info('Invalid user: {0}, {1}'.format(function_name, user))
            return 'Hello! I\'m afraid that you aren\'t on my list of users. Sorry about that!'
        elif not self.auto.is_running:
            logging.info('Star Saga not running: {0}, {1}'.format(function_name, user))
            return 'Hello! I\'m afraid something is wrong, Star Saga doesn\'t seem to be running. That\'s not something I can fix, you\'ll have to contact the person who created this bot.'
        else:
            return None

    @classmethod
    def from_config(cls):
        try:
            f = open('config.yaml')
            config_map = yaml.safe_load(f)
            f.close()
            return cls(config_map['discordtoken'],
                       config_map['users'],
                       config_map['vboxpath'])
        except Exception as e:
            print('Failed to start bot')
            raise

#####################################################
# Create the discord bot, but do not start it yet

discord_intents = discord.Intents.default()
discord_intents.message_content = True
logging.info('Constructing discord bot.')
discord_bot = commands.Bot(command_prefix='$', description='A bot that can send commands to Star Saga and return what it sees.', intents=discord_intents)
logging.info('Completed constructing discord bot.')

#####################################################
# event and command handlers

@discord_bot.command(brief='Start a session.', description='Start a session with the game. Will fail if another user has a session.')
async def starsaga(ctx):
    async with star_saga_bot.lock:
        error_message = star_saga_bot.validate_user(ctx.author, 'starsaga')
        if error_message:
            await ctx.author.send(error_message)
        else:
            # game is running, is there another user?
            if star_saga_bot.current_user is not None:
                logging.info('Failed to start session due to another player')
                await ctx.author.send('Hello! I\'m afraid that {0} is playing right now. Try again later! If this persists, you can use the forcestarsaga command, but please be careful with it!'.format(star_saga_bot.current_user))
            else:
                # OK, they're on the list, and nobody else has locked the bot, so they're now the 
                # current user
                star_saga_bot.current_user = ctx.author
                logging.info('Starting session for {0}'.format(ctx.author))
                await ctx.author.send('Great, you\'re now the current player. While you\'re the current player, messages sent in this chat will be relayed to the game, and I\'ll send along the resulting screen. When done, please send "$stopsaga" to complete your session.')

@discord_bot.command(brief='Stop a session,', description='Ends a session with the game. Will fail if you aren\'t the current user or if you\'re not on the first screen.')
async def stopsaga(ctx):
    async with star_saga_bot.lock:
        error_message = star_saga_bot.validate_user(ctx.author, 'stopsaga')
        if error_message:
            await ctx.author.send(error_message)
        else:
            # Is this the current user?
            if star_saga_bot.current_user == ctx.author:
                # this is the logged in user, check if we're on the correct screen
                if star_saga_bot.auto.check_ready_screen:
                    await ctx.author.send('Great, I\ve logged you off.')
                    logging.info('Ending session for {0}'.format(ctx.author))
                    star_saga_bot.current_user = None
                else:
                    logging.info('Failing to end session, not on ready screen')
                    await ctx.author.send('The game doesn\'t seem to be on the ready screen, please navigate to it before stopping your session.')
            else:
                logging.info('Failing to end session, not current player')
                await ctx.author.send('I\'m sorry, you don\'t seem to be the current player, so this is an invalid command. {0} is currently playing.'.format(star_saga_bot.current_user))

@discord_bot.command(brief='Print current screen', description='Gets the current screen. Fails if another user has a session.')
async def screen(ctx):
    async with star_saga_bot.lock:
        error_message = star_saga_bot.validate_user(ctx.author, 'screen')
        if error_message:
            await ctx.author.send(error_message)
        else:
            # Is this the current user or is there no user?
            if (star_saga_bot.current_user is None) or (star_saga_bot.current_user == ctx.author):
                logging.info('Sending screen shot')
                await ctx.author.send(star_saga_bot.auto.screen_shot())
            else:
                logging.info('Failing to screen shot, not current player')
                await ctx.author.send('I\'m sorry, you don\'t seem to be the current player, so this is an invalid command. {0} is currently playing.'.format(star_saga_bot.current_user))

@discord_bot.command(brief='Force start a session', description='Forces a session with the game. Always succeeds. Useful for getting the game back to a known state.')
async def forcestarsaga(ctx):
    async with star_saga_bot.lock:
        error_message = star_saga_bot.validate_user(ctx.author, 'starsaga')
        if error_message:
            await ctx.author.send(error_message)
        else:
            # This is a force, so they're now the current user
            star_saga_bot.current_user = ctx.author
            logging.info('Force starting session for {0}'.format(ctx.author))
            await ctx.author.send('Great, you\'re now the current player. While you\'re the current player, messages sent in this chat will be relayed to the game, and I\'ll send along the resulting screen. When done, please send "$stopsaga" to complete your session.')

@discord_bot.event
async def on_message(message):
    logging.info(message)

#####################################################
# time to start things up

star_saga_bot = StarSagaBot.from_config()
logging.info('Starting discord bot.')
discord_bot.run(star_saga_bot.token)
logging.info('Done with discord bot.')
star_saga_bot.stop_system()
logging.info('Done stopping system.')


"""
    # This method is used to log in
    def command_004_force_signin(self, originalMessage,
                                 user, messageText, args):
        '''force ([\S]*) ([\S]*)$(?i)'''
        self.process_signin(originalMessage, user, messageText, args, True)

    # This method is used to pass through things to the game
    def command_100_default(self, originalMessage, user, messageText, args):
        '''.*?(?s)(?m)'''
        if user == self.current_user:
            self.auto.send_keys(messageText)
            self.replyMessage(originalMessage, user, self.auto.screen_shot())
        else:
            self.replyMessage(originalMessage,
                              user,
                              'Command rejected - you aren\'t logged in!')
"""
