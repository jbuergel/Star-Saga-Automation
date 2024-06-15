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

from StarSagaAuto import StarSagaAuto
import discord
from discord.ext import commands

# StarSagaBot keeps track of all of our other state, as well as containing the automation
class StarSagaBot():
    auto = None
    current_user = None
    current_user_name = None
    users = None

    def __init__(self, token, users, vboxpath):
        self.users = users
        self.auto = StarSagaAuto(vboxpath)
        self.auto.start_star_saga()
        self.token = token
        print(users)

    def stop_system(self):
        self.auto.stop_star_saga()

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

# Create our Star Saga bot and the discord bot
discord_intents = discord.Intents.default()
discord_intents.message_content = True
discord_bot = commands.Bot(command_prefix='>', intents=discord_intents)

@discord_bot.command()
async def starsaga(ctx):
    if not star_saga_bot.auto.is_running:
        await ctx.author.send('Hello! I\'m afraid something is wrong, Star Saga doesn\'t seem to be running. That\'s not something I can fix, you\'ll have to contact the person who created this bot.')
    else:
        # game is running, is there another user?
        if star_saga_bot.current_user is not None:
            await ctx.author.send('Hello! I\'m afraid that somebody else is playing right now. Try again later! If this persists, you can use the forcestarsaga command, but please be careful with it!')
        else:
            print(ctx.author)

@discord_bot.command()
async def stopsaga(ctx):
    if not star_saga_bot.auto.is_running:
        await ctx.author.send('Hello! I\'m afraid something is wrong, Star Saga doesn\'t seem to be running. That\'s not something I can fix, you\'ll have to contact the person who created this bot.')
    else:
        # game is running, is there another user?
        if star_saga_bot.current_user is not None:
            await ctx.author.send('Hello! I\'m afraid that somebody else is playing right now. Try again later! If this persists, you can use the forcestarsaga command, but please be careful with it!')
        else:
            print(ctx.author)

star_saga_bot = StarSagaBot.from_config()
discord_bot.run(star_saga_bot.token)
star_saga_bot.stop_system()


"""
    # This method is used to log out
    def command_002_signout(self, originalMessage, user, messageText, args):
        '''signout'''
        if user == self.current_user:
            self.replyMessage(originalMessage,
                              user,
                              'Signed out {0}.'.format(
                              self.current_user_name))
            self.current_user = None
            self.current_user_name = None
        else:
            self.replyMessage(originalMessage,
                              user,
                              'Command rejected - you can\'t sign out'
                              ', you aren\'t signed in.')

    # get some help on available commands
    def command_003_help(self, originalMessage, user, messageText, args):
        '''help'''

        self.replyMessage(originalMessage, user, '''Available commands:
        signin [username] [password] - sign in a user.  Only one user may be
            signed in at a time.
        force [username] [password] - signs in a user, ejecting the previous
            user (if any).  Only use if someone is a deadbeat!
        signout - sign out.  Obviously, only the signed in user may sign out.
        help - prints this message.  Duh.
        [anything] - if you are signed in, send that text to Star Saga.
            If you are not signed in, does nothing.
        To send special characters, put 'enter' or 'esc' on their own
            messages.
        ''')

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
