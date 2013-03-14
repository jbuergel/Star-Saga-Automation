from PIL import Image
import glob
from TileSplitter import TileSplitter

for screen in glob.glob('*.png'):
    splitter = TileSplitter(screen)
    splitter.save_tiles()
