#!/usr/bin/env python
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
#

from PIL import Image
import sys
import glob
from time import time

class TileSplitter():
    TILE_WIDTH = 16
    TILE_HEIGHT = 16

    line_length = 0
    
    def __init__(self, file_name):
        self.tiles = []
        image = Image.open(file_name)
        if image.size[0] % self.TILE_WIDTH == 0 and image.size[1] % self.TILE_HEIGHT == 0:
            self.line_length = image.size[0] / self.TILE_WIDTH
            currentx = 0
            currenty = 0
            while currenty < image.size[1]:
                while currentx < image.size[0]:
                    self.tiles.append(image.crop((currentx, currenty, currentx + self.TILE_WIDTH, currenty + self.TILE_HEIGHT)))
                    currentx += self.TILE_WIDTH
                currenty += self.TILE_HEIGHT
                currentx = 0
                
    def save_tiles(self):
        count = 0
        for tile in self.tiles:
            self.save_single_tile(tile, count)
            count += 1
    
    def save_single_tile(self, tile, count):
        tile.save("tiles/{0}_{1}.png".format(time(), count), "PNG")
        
    def get_tile_list(self):
        return self.tiles
