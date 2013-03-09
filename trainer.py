#!/usr/bin/python
# -*- coding: utf-8 -*-

import pickle
import glob
import hashlib
from PIL import Image, ImageQt
from PyQt4.Qt import *
from PyQt4 import QtGui
import sys

class TrainTiles():
    trained_data = None
    
    def __init__(self):
        try:
            with open('trained_data', 'rb') as f:
                self.trained_data = pickle.load(f)
            print(self.trained_data)
        except:
            print('No trained data exists.')
            self.trained_data = {}
        
    def compute_hash(self, image_path):
        image = Image.open(image_path)
        tile_hash = hashlib.md5()
        for pixel in image.getdata():
            tile_hash.update(str(pixel).encode('ascii'))
        return tile_hash.hexdigest()

    def find_missing_tiles(self):
        self.missing_tiles = []
        for tile in glob.glob('tiles/*.png'):
            tile_hash = self.compute_hash(tile)
            if tile_hash not in self.trained_data:
                self.missing_tiles.append(tile)
    
    def get_next_tile(self):
        return self.missing_tiles[0] if self.missing_tiles else None;
        
    def record_training(self, data):
        if self.missing_tiles:
            tile_hash = self.compute_hash(self.missing_tiles[0])
            self.trained_data[tile_hash] = data
            with open('trained_data', 'wb') as f:
                pickle.dump(self.trained_data, f)
            self.missing_tiles.pop(0)
            print(self.trained_data)
            self.missing_tiles = [tile for tile in self.missing_tiles if self.compute_hash(tile) not in self.trained_data]

class MainWindow(QMainWindow):
    
    tile = None
    
    def display_tile(self):
        missing_tile = train_tiles.get_next_tile()
        print(missing_tile)
        if missing_tile:
            if not self.tile:
                self.tile = QLabel(self.cw)
                self.tile.setScaledContents(True)
                self.tile.setGeometry(120, 10, 48, 48)
            self.tile.setPixmap(QPixmap(missing_tile))

    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)
        self.width = 600
        self.btn1 = QPushButton("Train", self.cw)
        self.btn1.setGeometry(QRect(5, 5, 100, 30))
        self.connect(self.btn1, SIGNAL("clicked()"), self.doit)
        self.missing_tiles = train_tiles.find_missing_tiles()
        self.text_input = QLineEdit(self.cw)
        self.text_input.setGeometry(5, 40, 100, 30)
        self.text_input.setValidator(QRegExpValidator(QRegExp("[\\S ]?")))
        self.connect(self.text_input, SIGNAL("returnPressed()"), self.doit)
        self.display_tile()

    def doit(self):
        train_tiles.record_training(self.text_input.text())
        self.text_input.setText("")
        self.display_tile()

class App(QApplication):
    def __init__(self, *args):
        QApplication.__init__(self, *args)
        self.main = MainWindow()
        self.connect(self, SIGNAL("lastWindowClosed()"), self.byebye )
        self.main.show()

    def byebye( self ):
        self.exit(0)

def main(args):
    global app
    global train_tiles
    train_tiles = TrainTiles()
    app = App(args)
    app.exec_()

if __name__ == "__main__":
    main(sys.argv)        
