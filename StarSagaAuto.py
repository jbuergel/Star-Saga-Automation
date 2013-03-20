#!/usr/bin/python
# -*- coding: utf-8 -*-

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

from vboxapi import VirtualBoxManager
from time import sleep, time
import os
import subprocess
from TileRecognizer import TileRecognizer
from TileSplitter import TileSplitter
import re

class StarSagaAuto:
    
    virtual_box_manager = None
    session = None
    vbox = None
    machine = None
    recognizer = TileRecognizer()
    
    scancodes = {
        'a':  0x1e,
        'b':  0x30,
        'c':  0x2e,
        'd':  0x20,
        'e':  0x12,
        'f':  0x21,
        'g':  0x22,
        'h':  0x23,
        'i':  0x17,
        'j':  0x24,
        'k':  0x25,
        'l':  0x26,
        'm':  0x32,
        'n':  0x31,
        'o':  0x18,
        'p':  0x19,
        'q':  0x10,
        'r':  0x13,
        's':  0x1f,
        't':  0x14,
        'u':  0x16,
        'v':  0x2f,
        'w':  0x11,
        'x':  0x2d,
        'y':  0x15,
        'z':  0x2c,
        '0':  0x0b,
        '1':  0x02,
        '2':  0x03,
        '3':  0x04,
        '4':  0x05,
        '5':  0x06,
        '6':  0x07,
        '7':  0x08,
        '8':  0x09,
        '9':  0x0a,
        ' ':  0x39,
        '-':  0xc,
        '=':  0xd,
        '[':  0x1a,
        ']':  0x1b,
        ';':  0x27,
        '\'': 0x28,
        ',':  0x33,
        '.':  0x34,
        '/':  0x35,
        '\t': 0xf,
        '\n': 0x1c,
        '`':  0x29
    }

    extScancodes = {
        'ESC' :    [0x01],
        'BKSP':    [0xe],
        'SPACE':   [0x39],
        'TAB':     [0x0f],
        'CAPS':    [0x3a],
        'ENTER':   [0x1c],
        'LSHIFT':  [0x2a],
        'RSHIFT':  [0x36],
        'INS':     [0xe0, 0x52],
        'DEL':     [0xe0, 0x53],
        'END':     [0xe0, 0x4f],
        'HOME':    [0xe0, 0x47],
        'PGUP':    [0xe0, 0x49],
        'PGDOWN':  [0xe0, 0x51],
        'LGUI':    [0xe0, 0x5b], # GUI, aka Win, aka Apple key
        'RGUI':    [0xe0, 0x5c],
        'LCTR':    [0x1d],
        'RCTR':    [0xe0, 0x1d],
        'LALT':    [0x38],
        'RALT':    [0xe0, 0x38],
        'APPS':    [0xe0, 0x5d],
        'F1':      [0x3b],
        'F2':      [0x3c],
        'F3':      [0x3d],
        'F4':      [0x3e],
        'F5':      [0x3f],
        'F6':      [0x40],
        'F7':      [0x41],
        'F8':      [0x42],
        'F9':      [0x43],
        'F10':     [0x44 ],
        'F11':     [0x57],
        'F12':     [0x58],
        'UP':      [0xe0, 0x48],
        'LEFT':    [0xe0, 0x4b],
        'DOWN':    [0xe0, 0x50],
        'RIGHT':   [0xe0, 0x4d],
    }
    
    shiftedScancodes = {
        '*':  0x09,
    }
    
    KEY_UP = 0x80
    
    def standard_keypress(self, output_keys, key):
        key_code = self.scancodes.get(key, None)
        if key_code:
            output_keys.append(key_code)
            output_keys.append(key_code + self.KEY_UP)
        return key_code
          
    def shifted_keypress(self, output_keys, key):
        key_code = self.shiftedScancodes.get(key, None)
        if key_code:
            l_shift = self.extScancodes.get('LSHIFT', None)
            output_keys.extend(l_shift)
            output_keys.append(key_code)
            output_keys.append(key_code + self.KEY_UP)
            output_keys.append(l_shift[-1] + self.KEY_UP)
        return key_code
          
    def extended_keypress(self, output_keys, extended_code):
        key_code = self.extScancodes.get(extended_code.upper(), None)
        if key_code:
            output_keys.extend(key_code)
            output_keys.append(key_code[-1] + self.KEY_UP)
        return key_code
    
    def send_keys(self, chars):
        keys = []
        if not self.extended_keypress(keys, chars):
            for key in chars:
                if not self.standard_keypress(keys, key):
                    self.shifted_keypress(keys, key)
        if keys:
            self.session.console.keyboard.putScancodes(keys)
            sleep(0.1)
            
    def send_enter(self):
        self.send_keys(['ENTER'])

    def start_star_saga(self):
        self.virtual_box_manager = VirtualBoxManager(None, None)
        self.vbox = self.virtual_box_manager.vbox
        self.machine = self.vbox.findMachine("Dos622")
        self.session = self.virtual_box_manager.mgr.getSessionObject(self.vbox)
        progress = self.machine.launchVMProcess(self.session, "gui", "")
        progress.waitForCompletion(-1)
        sleep(10.0)
        self.send_keys('b')
        self.send_keys('n')
        self.send_keys('o')
            
    def stop_star_saga(self):
        self.session.console.powerDown()
        
    def screen_shot_to_file(self, file_name):
        (width, height, color_depth) = self.session.console.display.getScreenResolution(0)
        screen_array = self.session.console.display.takeScreenShotPNGToArray(0, width, height)
        f = open(file_name, 'wb')
        f.write(screen_array)
        f.close()
        
    def screen_shot(self):
        file_name = 'screen{0}.png'.format(time())
        self.screen_shot_to_file(file_name)
        splitter = TileSplitter(file_name)
        response = []
        count = 0
        for tile in splitter.get_tile_list():
            value = self.recognizer.recognize(tile)
            if value is not None:
                response.append(value)
            else:
                print('TILE NOT RECOGNIZED')
                response.append('?')
                splitter.save_single_tile(tile, count)
            count += 1
            if count % splitter.line_length == 0:
                response.append('\n')
        os.remove(file_name)
        return re.sub('#[\\s]*([0-9]+)', lambda m: 'http://www.houseofslack.com/josh/starsaga/passages/{0}.png'.format(m.group(1)), ''.join(response))
        
############################################################################################################################
if __name__ == "__main__":
    auto = StarSagaAuto()
    auto.start_star_saga()
    print(auto.screen_shot())
    auto.stop_star_saga()
