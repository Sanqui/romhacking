#!/usr/bin/python3

# gb2pgm converts graphics in the 2bpp Gameboy format to PGM, the portable
# graymap format, which allows for simple further conversion to common image
# formats using command-line tools like pnmtopng.

import struct
import os
import sys
import math

if len(sys.argv) != 2:
    sys.exit('usage: python3 gb2pgm.py file/directory')
arg = sys.argv[1]
files = []
if os.path.isdir(arg):
    for f in sorted(os.listdir(arg)):
        if f[-4:] != '.pgm':
            files.append(os.path.join(arg, f))
else:
    files = [arg]

for f in files:
    gr = open(f, 'rb')
    gr = gr.read()

    tiles = []
    tile = []

    for curshort in range(len(gr)//2):
        high = bin(gr[curshort*2])[2:].zfill(8)
        low = bin(gr[curshort*2+1])[2:].zfill(8)
        for h, l in zip(high, low):
            pixel = int(l+h, 2)
            tile.append(pixel)
        if len(tile)==8*8:
            tiles.append(tile)
            tile = []
            
    height = (math.ceil(len(tiles)/16))*8
    pgm = """P2
    #
    {} {}
    3
    """.format(8*16, height)
    for row in range(height):
        for col in range(8*16):
            try:
                pgm += str(tiles[16*(row//8)+(col//8)][8*(row%8)+(col%8)] ^ 0x03)+'\t'
            except IndexError:
                pgm += '4\t'
        pgm += '\n'
        
    g = open('{}.pgm'.format(f[:f.rfind('.')]), 'w')
    g.write(pgm)
    g.close()
    print ('Wrote {}.pgm'.format(f[:f.rfind('.')]))
