#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Based on Sleek XMPP example code from:
# https://github.com/fritzy/SleekXMPP/blob/develop/examples/echo_client.py
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
import logging
import getpass
from optparse import OptionParser

import slixmpp
import re
import inspect

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from slixmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input


class GtalkRobot(slixmpp.ClientXMPP):

    """
    A simple SleekXMPP bot that will echo messages it
    receives, along with a short thank you message.
    """

    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.current_jid = jid

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        self.add_event_handler("message", self.message)
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0004')  # Data Forms
        self.register_plugin('xep_0060')  # PubSub
        self.register_plugin('xep_0199')  # XMPP Ping

    async def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        await self.get_roster()

    def message(self, msg):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        if msg['type'] in ('chat', 'normal'):
            self.controller(msg)

    commands = None
    command_prefix = 'command_'

    #This method is the default action for all pattern in lowest priviledge
    def command_999_default(self, originalMessage, user, messageText, args):
        """.*?(?s)(?m)"""
        self.replyMessage(originalMessage, user, messageText)

    def replyMessage(self, originalMessage, user, replyText):
        try:
            originalMessage.reply(replyText).send()
        except:
            print(
                "Exception sending message: \n {0}"
                .format(str(sys.exc_info()[1])))

    def initCommands(self):
        if self.commands:
            self.commands.clear()
        else:
            self.commands = list()
        for (name, value) in inspect.getmembers(self):
            if (inspect.ismethod(value) and
                    name.startswith(self.command_prefix)):
                self.commands.append((value.__doc__, value))

    def controller(self, message):
        user = message.getFrom()
        text = message['body']
        if text:
            if not self.commands:
                self.initCommands()
            for (pattern, bounded_method) in self.commands:
                match_obj = re.match(pattern, text)
                if(match_obj):
                    try:
                        bounded_method(message, user, text, match_obj.groups())
                    except:
                        resp = ("Unexpected error: \n {0}".
                                format(str(sys.exc_info()[1])))
                        self.replyMessage(message, user, resp)
                    break

    def startBot(self):
        if self.connect():
            self.process(block=False)
            input("Press Enter to continue...")
            print("Done")
        else:
            print("Unable to connect.")

    def stopBot(self):
        self.disconnect(wait=True)


if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = raw_input("Username: ")
    if opts.password is None:
        opts.password = getpass.getpass("Password: ")

    # Setup the GtalkRobot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = GtalkRobot(opts.jid, opts.password)
    xmpp.startBot()
