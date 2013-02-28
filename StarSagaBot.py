#!/usr/bin/python
# -*- coding: utf-8 -*-

# StarSagaBot: Star Saga controller based on pygtalkrobot (http://code.google.com/p/pygtalkrobot/)
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

############################################################################################################################

class StarSagaBot(GtalkRobot):
    
    auto = None
    current_user = None
    current_user_name = None
    
    #Regular Expression Pattern Tips:
    # I or IGNORECASE <=> (?i)      case insensitive matching
    # L or LOCALE <=> (?L)          make \w, \W, \b, \B dependent on the current locale
    # M or MULTILINE <=> (?m)       matches every new line and not only start/end of the whole string
    # S or DOTALL <=> (?s)          '.' matches ALL chars, including newline
    # U or UNICODE <=> (?u)         Make \w, \W, \b, and \B dependent on the Unicode character properties database.
    # X or VERBOSE <=> (?x)         Ignores whitespace outside character sets
    
    #"command_" is the command prefix, "001" is the priviledge num, "setState" is the method name.
    # This method is used to log in
    def command_001_signin(self, originalMessage, user, messageText, args):
        #the __doc__ of the function is the Regular Expression of this command, if matched, this command method will be called. 
        #The parameter "args" is a list, which will hold the matched string in parenthesis of Regular Expression.
        '''signin ([\S]*) ([\S]*)$(?i)'''
        name = args[0]
        password = args[1]

        if (name == 'josh' and password == 'troopsneverkidsoffice') or (name == 'hp' and password == 'thenequipmentsomezoo'):
            print('here')
            if self.current_user:
                self.replyMessage(originalMessage, user, 'Sorry, {0} is still logged in.'.format(self.current_user_name))
            else:
                self.replyMessage(originalMessage, user, 'User {0} logged in.'.format(name))
                self.current_user = user
                self.current_user_name = name
        else:
            self.replyMessage(originalMessage, user, 'who are you who who who who')
            
    # This method is used to log out
    def command_002_signout(self, originalMessage, user, messageText, args):
        '''signout'''

        if user == self.current_user:
            self.replyMessage(originalMessage, user, 'Signed out {0}.'.format(self.current_user_name))
            self.current_user = None
            self.current_user_name = None
        else:
            self.replyMessage(originalMessage, user, 'OK, what are you trying to pull?')
    
    #This method is used to response users.
    def command_100_default(self, originalMessage, user, messageText, args):
        '''.*?(?s)(?m)'''
        self.auto.send_keys(messageText)
        self.replyMessage(originalMessage, user, 'sent {0}'.format(messageText))

    def start_system(self):
        self.auto = StarSagaAuto()
        self.auto.start_star_saga()
        self.startBot()
        
    def stop_system(self):
        self.stopBot()
        self.auto.stop_star_saga()
        
############################################################################################################################
if __name__ == "__main__":
    f = open('creds.yaml')
    # use safe_load instead load
    config_map = yaml.safe_load(f)
    f.close()
    print(config_map)
    bot = StarSagaBot(config_map['jid'], config_map['password'])
    bot.start_system()
    bot.stop_system()
