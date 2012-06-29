#!/usr/bin/python3

# 

import struct
import os
import sys
import math

def readshort():
    return struct.unpack("<H", rom.read(2))[0]
    
def readbyte():
    return struct.unpack("<B", rom.read(1))[0]
    
def abspointer(bank, offset):
    return bank*0x4000+offset-0x4000

def readfarpointers(offset, amount=151):
    rom.seek(offset)
    pointers = []
    for i in range(amount):
        offset = readshort()
        bank = readbyte()
        assert 0x3fff < offset < 0x8000
        pointers.append((offset - 0x4000) + 0x4000 * bank)
    return pointers

def readtiles(amount):
    tiles = []
    tile = []

    for i in range(amount*8*4):
        high = readbyte()
        low = readbyte()
        #print(hex(i), hex(s), high, low)
        for i in range(8)[::-1]:
            h = (high >> i) & 0b1
            l = (low >> i) & 0b1
            pixel = (l*2+h)
            tile.append(pixel)
        if len(tile)==8*8:
            tiles.append(tile)
            tile = []
    #print(len(tiles))
    #raise
    return tiles

def readcolor():
    s = readshort()
    blue = (s >> 10)
    green = (s >> 5) % 32
    red = (s) % 32
    return (red, green, blue)

def readpalette():
    pal = []
    for i in range(4):
        pal.append(readcolor())
    return pal
    
def createppm(tiles, width=6, height=4):
    ppm = """P6
{0} {1}
255
""".format(width*8, height*8).encode("ascii")
    for row in range(height*8):
        for col in range(width*8):
            #print("{}x{} [{}][{}] - ".format(row,col, (width)*(row//8)+(col//8), 8*(row%8)+(col%8)), end="")
            try:
                r, g, b = tiles[(width)*(row//8)+(col//8)][8*(row%8)+(col%8)]
                ppm += struct.pack("BBB", r*8, g*8, b*8)
            except IndexError:
                raise
    return ppm
    
if len(sys.argv) != 2:
    sys.exit('usage: python3 pinballsprites.py rom.gbc')
rom = open(sys.argv[1], 'rb')

sprite_pointers = readfarpointers(0x12b50)
palette_pointers = readfarpointers(0x12eda)
palette_map_pointers = readfarpointers(0x12d15)

pokesprites = []
for pointer in sprite_pointers:
    rom.seek(pointer)
    pokesprites.append(readtiles(6*4))
    print("read {}".format(hex(pointer)))
    
pokesilhouettes = []
for pointer in sprite_pointers:
    rom.seek(pointer+6*4*8*2)
    pokesilhouettes.append(readtiles(6*4))
    print("read silhouette {}".format(hex(pointer)))

pokepalettes = []
for pointer in palette_pointers:
    rom.seek(pointer)
    pokepalettes.append((readpalette(), readpalette()))
    
pokepalette_maps = []
for pointer in palette_map_pointers:
    rom.seek(pointer)
    palmap = []
    for i in range(6*4):
        palmap.append(readbyte())
    pokepalette_maps.append(palmap)
    
for sprite, palettes, palmap in zip(pokesprites, pokepalettes, pokepalette_maps):
    for tile, pal in zip(sprite, palmap):
        #print(pal, hex(len(sprite)), hex(len(palmap)), hex(6*4))
        palette = palettes[pal-6]
        for i, pixel in enumerate(tile):
            tile[i] = palette[pixel]
    
silhouettepalette = ((31, 31, 31), (20, 20, 20), (8, 8, 8), (0, 0, 0))
for sprite in pokesilhouettes:
    for tile in sprite:
        for i, pixel in enumerate(tile):
            tile[i] = silhouettepalette[pixel]
        
#height = (math.ceil(len(tiles)/16))*8

for i in range(len(pokesprites)):
    sprite = pokesprites[i]
    ppm = createppm(sprite)
    g = open('s/{}.ppm'.format(i+1), 'wb')
    g.write(ppm)
    g.close()
    
    silhouette = pokesilhouettes[i]
    ppm = createppm(pokesilhouettes[i])
    g = open('s/silhouettes/{}.ppm'.format(i+1), 'wb')
    g.write(ppm)
    g.close()
    print ('Wrote {}'.format(i))
