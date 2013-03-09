from PIL import Image
import sys
import glob

tile_width = 16
tile_height = 16

for screen in glob.glob('*.png'):
    image = Image.open(screen)
    if image.size[0] % tile_width == 0 and image.size[1] % tile_height == 0:
        currentx = 0
        currenty = 0
        while currenty < image.size[1]:
            while currentx < image.size[0]:
                tile = image.crop((currentx, currenty, currentx + tile_width, currenty + tile_height))
                tile.save("tiles/y{0:03}x{1:03}.png".format(currenty, currentx), "PNG")
                currentx += tile_width
            currenty += tile_height
            currentx = 0
