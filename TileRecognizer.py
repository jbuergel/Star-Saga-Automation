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

import pickle
import hashlib
import glob
from PIL import Image

class TileRecognizer():
    trained_data = None
    
    def __init__(self):
        try:
            with open('trained_data', 'rb') as f:
                self.trained_data = pickle.load(f)
        except:
            self.trained_data = {}
        
    def compute_hash_from_file(self, image_path):
        image = Image.open(image_path)
        return self.compute_hash(image)
        
    def compute_hash(self, image):
        tile_hash = hashlib.md5()
        for pixel in image.getdata():
            tile_hash.update(str(pixel).encode('ascii'))
        return tile_hash.hexdigest()

    def find_missing_tiles(self):
        self.missing_tiles = []
        for tile in glob.glob('tiles/*.png'):
            tile_hash = self.compute_hash_from_file(tile)
            if tile_hash not in self.trained_data:
                self.missing_tiles.append(tile)
    
    def get_next_tile(self):
        return self.missing_tiles[0] if self.missing_tiles else None;
    
    def recognize(self, tile):
        tile_hash = self.compute_hash(tile)
        return self.trained_data[tile_hash] if tile_hash in self.trained_data else None
    
    def record_training(self, data):
        if self.missing_tiles:
            tile_hash = self.compute_hash_from_file(self.missing_tiles[0])
            self.trained_data[tile_hash] = data
            with open('trained_data', 'wb') as f:
                pickle.dump(self.trained_data, f)
            self.missing_tiles.pop(0)
            print(self.trained_data)
            self.missing_tiles = [tile for tile in self.missing_tiles if self.compute_hash_from_file(tile) not in self.trained_data]
