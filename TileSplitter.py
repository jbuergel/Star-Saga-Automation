#!/usr/bin/python
# -*- coding: utf-8 -*-

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
