#!/usr/bin/python
# -*- coding: utf-8 -*-

# StarSagaBot: Star Saga controller based on
# pygtalkrobot (http://code.google.com/p/pygtalkrobot/)
# Copyright (c) 2012 Joshua Buergel <jbuergel@gmail.com>
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

from PyGtalkRobot import GtalkRobot
from StarSagaAuto import StarSagaAuto


class StarSagaBot(GtalkRobot):
    auto = None
    current_user = None
    current_user_name = None
    users = None

    def __init__(self, jid, password, users):
        super().__init__(jid, password)
        self.users = users

    def process_signin(self, originalMessage, user, messageText, args, force):
        name = args[0]
        password = args[1]

        # note that we could reject right away if we have a logged in user.
        # But that leaks (some lame) information, so we will only tell them
        # someone else is logged in if their credentials are OK.
        for check_user in self.users:
            if (check_user['name'] == name and
                    check_user['password'] == password):
                if self.current_user and not force:
                    self.replyMessage(originalMessage,
                                      user,
                                      'Sorry, {0} is still logged in.'.format(
                                      self.current_user_name))
                else:
                    self.replyMessage(originalMessage,
                                      user,
                                      self.auto.screen_shot())
                    self.current_user = user
                    self.current_user_name = name
                return
        # failed to find the user
        self.replyMessage(originalMessage,
                          user,
                          'whoooooooo are you who who who who')

    # This method is used to log in
    def command_001_signin(self, originalMessage, user, messageText, args):
        '''signin ([\S]*) ([\S]*)$(?i)'''
        self.process_signin(originalMessage, user, messageText, args, False)

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

    def start_system(self):
        self.auto = StarSagaAuto()
        self.auto.start_star_saga()
        self.startBot()

    def stop_system(self):
        self.stopBot()
        self.auto.stop_star_saga()

    @classmethod
    def from_config(cls):
        f = open('creds.yaml')
        config_map = yaml.safe_load(f)
        f.close()
        return cls(config_map['jid'],
                   config_map['password'],
                   config_map['users'])

#############################################################################
if __name__ == "__main__":
    bot = StarSagaBot.from_config()
    bot.start_system()
    bot.stop_system()
