#!/usr/bin/python2

# gba2png converts 4bpp and 8bpp GBA graphics into PNGs.

import struct
import os
import sys
import math

import png

WIDTH=16
bpp = 4

if len(sys.argv) != 2:
    sys.exit('usage: python2 gba2png.py file/directory')
arg = sys.argv[1]
files = []
if os.path.isdir(arg):
    for f in sorted(os.listdir(arg)):
        if f[-4:] != '.png':
            files.append(os.path.join(arg, f))
else:
    files = [arg]

for f in files:
    for bpp in (4, 8):
        gr = open(f, 'rb')
        numbytes = len(gr.read())
        gr.seek(0)

        tiles = []
        tile = []

        for tilerow in range(numbytes//bpp):
            row = []
            if bpp == 4:
                for i in range(4):
                    byte = ord(gr.read(1))
                    row.append(byte & 0x0f)
                    row.append(byte>>4)
            else:
                for i in range(8):
                    byte = ord(gr.read(1))
                    row.append(byte)
            #for plane in range(bpp):
            #    bp = ord(gr.read(1))
            #    for b in range(8):
            #        row[7-b] |= bool(bp & (1 << b)) << plane
            #print row
            tile += row
            if len(tile) == 8*8:
                tiles.append(tile)
                tile = []
        
        if tiles:
            if len(tiles) == 16:
                width = 4
            elif len(tiles) == 64:
                width = 8
            elif len(tiles) == 100:
                width = 8
            else:
                width = WIDTH
            
            rows = []
            height = int((math.ceil(float(len(tiles))/width)))*8
            for rowi in range(height):
                row = []
                for coli in range(8*width):
                    try:
                        #print tiles[WIDTH*(rowi//8)+(coli//8)][8*(rowi%8)+(coli%8)] * (256 // (1<<bpp))
                        row.append(tiles[width*(rowi//8)+(coli//8)][8*(rowi%8)+(coli%8)] * (256 // (1<<bpp))) # XXX other bpp
                    except IndexError:
                        row.append(0)
                rows.append(row)
            
            #print rows
            
            fname = '{}-{}bpp.png'.format(f[:f.rfind('.')], bpp)
            png.from_array(rows, 'L').save(fname)
            print ('Wrote '+fname)
        else:
            print "{} doesn't constitute a single tile".format(f)
