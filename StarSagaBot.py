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
    users = None

    def __init__(self, token, users, vboxpath):
        logging.basicConfig(filename='Logs/starsagabot.log', level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info('Constructing star saga bot.')
        self.users = users
        self.auto = StarSagaAuto(vboxpath)
        self.token = token
        self.logger.info('Completed constructing star saga bot.')

    async def start_system(self):
        self.logger.info('Starting star saga automation.')
        await self.auto.start_star_saga()        
        self.logger.info('Completed star saga automation.')

    async def stop_system(self):
        self.logger.info('Stopping star saga bot.')
        await self.auto.stop_star_saga()
        self.logger.info('Completed stopping star saga bot.')

    def validate_user(self, user, function_name):
        self.logger.info('Function entry: {0}, {1}'.format(function_name, user))
        if str(user) not in self.users:
            self.logger.info('Invalid user: {0}, {1}'.format(function_name, user))
            return 'Hello! I\'m afraid that you aren\'t on my list of users. Sorry about that!'
        elif not self.auto.is_running:
            self.logger.info('Star Saga not running: {0}, {1}'.format(function_name, user))
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
COMMAND_PREFIX = '$'
discord_bot = commands.Bot(command_prefix=COMMAND_PREFIX, description='A bot that can send commands to Star Saga and return what it sees.', intents=discord_intents)

#####################################################
# event and command handlers

@discord_bot.command(brief='Start a session.', description='Start a session with the game. Will fail if another user has a session. While playing, you send commands via DMs to the bot, and it will respond with screens. For special characters, type them out, such as \'ESC\' or \'ENTER\'.')
async def starsaga(ctx):
    async with star_saga_bot.lock:
        error_message = star_saga_bot.validate_user(ctx.author, 'starsaga')
        if error_message:
            await ctx.author.send(error_message)
        else:
            # game is running, is there another user?
            if star_saga_bot.current_user is not None:
                star_saga_bot.logger.info('Failed to start session due to another player')
                await ctx.author.send('Hello! I\'m afraid that {0} is playing right now. Try again later! If this persists, you can use the forcestarsaga command, but please be careful with it!'.format(star_saga_bot.current_user))
            else:
                # OK, they're on the list, and nobody else has locked the bot, so they're now the 
                # current user
                star_saga_bot.current_user = str(ctx.author)
                star_saga_bot.logger.info('Starting session for {0}'.format(ctx.author))
                await ctx.author.send('Great, you\'re now the current player. While you\'re the current player, messages sent in this chat will be relayed to the game, and I\'ll send along the resulting screen. When done, please send "$stopsaga" to complete your session.')
                await ctx.author.send(star_saga_bot.auto.screen_shot())

@discord_bot.command(brief='Stop a session,', description='Ends a session with the game. Will fail if you aren\'t the current user or if you\'re not on the first screen.')
async def stopsaga(ctx):
    async with star_saga_bot.lock:
        error_message = star_saga_bot.validate_user(ctx.author, 'stopsaga')
        if error_message:
            await ctx.author.send(error_message)
        else:
            # Is this the current user?
            if star_saga_bot.current_user == str(ctx.author):
                # this is the logged in user, check if we're on the correct screen
                if star_saga_bot.auto.check_ready_screen:
                    await ctx.author.send('Great, I\'ve logged you off.')
                    star_saga_bot.logger.info('Ending session for {0}'.format(ctx.author))
                    star_saga_bot.current_user = None
                else:
                    star_saga_bot.logger.info('Failing to end session, not on ready screen')
                    await ctx.author.send('The game doesn\'t seem to be on the ready screen, please navigate to it before stopping your session.')
            else:
                star_saga_bot.logger.info('Failing to end session, not current player')
                await ctx.author.send('I\'m sorry, you don\'t seem to be the current player, so this is an invalid command. {0} is currently playing.'.format(star_saga_bot.current_user))

@discord_bot.command(brief='Print current screen', description='Gets the current screen. Fails if another user has a session.')
async def screen(ctx):
    async with star_saga_bot.lock:
        error_message = star_saga_bot.validate_user(ctx.author, 'screen')
        if error_message:
            await ctx.author.send(error_message)
        else:
            # Is this the current user or is there no user?
            if (star_saga_bot.current_user is None) or (star_saga_bot.current_user == str(ctx.author)):
                star_saga_bot.logger.info('Sending screen shot')
                await ctx.author.send(star_saga_bot.auto.screen_shot())
            else:
                star_saga_bot.logger.info('Failing to screen shot, not current player')
                await ctx.author.send('I\'m sorry, you don\'t seem to be the current player, so this is an invalid command. {0} is currently playing.'.format(star_saga_bot.current_user))

@discord_bot.command(brief='Force start a session', description='Forces a session with the game. Always succeeds. Useful for getting the game back to a known state.')
async def forcestarsaga(ctx):
    async with star_saga_bot.lock:
        error_message = star_saga_bot.validate_user(ctx.author, 'starsaga')
        if error_message:
            await ctx.author.send(error_message)
        else:
            # This is a force, so they're now the current user
            star_saga_bot.current_user = str(ctx.author)
            star_saga_bot.logger.info('Force starting session for {0}'.format(ctx.author))
            await ctx.author.send('Great, you\'re now the current player. While you\'re the current player, messages sent in this chat will be relayed to the game, and I\'ll send along the resulting screen. When done, please send "$stopsaga" to complete your session.')

@discord_bot.event
async def on_ready():
    star_saga_bot.lock = asyncio.Lock()

@discord_bot.event
async def on_message(message):
    processed = False
    # is this a direct message to us?
    if isinstance(message.channel, discord.DMChannel):
        # it is, check to see if it starts with our prefix - if it does, we'll just delegate
        # to the command processor
        if message.content[0] != COMMAND_PREFIX:
            # we're going to consider this message processed, even if we end up ignoring it
            processed = True
            async with star_saga_bot.lock:
                # this is a bare message - check to see if this user is logged in
                # note that we don't have to check to see if this user is a known user to us
                # because they couldn't own the session if they weren't
                if (star_saga_bot.current_user == str(message.author)):
                    # great! we're going to forward this message to the game and then relay
                    # back the resulting screen
                    await star_saga_bot.auto.send_keys(message.content)
                    await message.author.send(star_saga_bot.auto.screen_shot())
                # check to see if this is one of our known users - if so
                # we'll let them know that they're not steering the ship right now
                elif str(message.author) in star_saga_bot.users:
                    star_saga_bot.logger.info('Ignoring DM, not current player')
                    await message.author.send('I\'m sorry, you don\'t seem to be the current player, so I\'m ignoring this message. {0} is currently playing.'.format(star_saga_bot.current_user))
                # not a known user - how did they DM us? Dunno, but we'll just silently ignore it
                else:
                    star_saga_bot.logger.info('DM from unknown user')
                    pass
    if not processed:
        # delegate everything else to the command processor
        await discord_bot.process_commands(message)

#####################################################
# time to start things up

star_saga_bot = StarSagaBot.from_config()
asyncio.run(star_saga_bot.start_system())
star_saga_bot.logger.info('Starting discord bot.')
discord_bot.run(star_saga_bot.token)
star_saga_bot.logger.info('Done with discord bot.')
asyncio.run(star_saga_bot.stop_system())
star_saga_bot.logger.info('Done stopping system.')
