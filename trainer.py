#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.Qt import *
from PyQt4 import QtGui
import sys
from TileRecognizer import TileRecognizer

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
    train_tiles = TileRecognizer()
    app = App(args)
    app.exec_()

if __name__ == "__main__":
    main(sys.argv)        
