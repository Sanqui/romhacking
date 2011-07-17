#!/usr/bin/python3

# punika is a graphics decompresser for the game Keitai Denjuu Telefang, which
# uses the Malias compression, roughly designed after LZ77.
# Refer to 
# http://wikifang.meowcorp.us/wiki/Wikifang:Telefang_1_Translation_Patch/Malias_compression
# for details.
#
# punika  creates a folder called g and places all game's compressed graphics
# in it raw, so it can be read by your favorite tile editor (Tile Molester, TLP,
# etc.)
# -- Sanky

import struct
import os
import sys

if len(sys.argv) != 2:
    sys.exit('usage: python3 punika.py rom.gbc')
rom = sys.argv[1]

if not os.path.exists('g'+os.sep):
    os.makedirs('g')


def readshort():
    return struct.unpack("<H", rom.read(2))[0]
    
def readbyte():
    return struct.unpack("<B", rom.read(1))[0]
    
def abspointer(bank, offset):
    return bank*0x4000+offset-0x4000

graphics = {}

rom = open(rom, 'rb')
rom.seek(0x18000)
for i in range(0x128):
    bank, target = struct.unpack("<BH", rom.read(3))
    if target > 0x7fff and target < 0xa000:
        graphics[i] = {'target':target, 'bank':bank}
    rom.read(1)
rom.seek(0x1DE1)
for i in range(0x128):
    pointer = struct.unpack("<H", rom.read(2))[0]
    if i in graphics:
        if pointer > 0x3fff and pointer < 0x8000:
            graphics[i]['pointer'] = pointer
        else:
            del graphics[i]

#for i, g in graphics.items():
#    print ("{:>4} - bank {:>4} + {:>8} ({:>8}) read in {:>7}".format(hex(i),
#    hex(g['bank']), 
#    hex(g['pointer']), 
#    hex(abspointer(g['bank'], g['pointer'])), hex(g['target'])))
    
for gi, g in graphics.items():
    l = abspointer(g['bank'], g['pointer'])
    rom.seek(l)

    if rom.read(1) == b'\x00':
        print ("Reading uncompressed data is unimplemented yet.")
    else:
        #print ('Decompressing {} ({}).'.format(hex))
        data = bytearray()  
        total = readshort()
        loc = 0        

        while len(data) < total: 
            modes = readshort()
            for mode in bin(modes)[2:].zfill(16)[::-1]:
                if int(mode) == 1:
                    e = rom.read(1)
                    d = rom.read(1)
                    loc = -(struct.unpack("<H", e+d)[0]  & 0x07ff) 
                    num = ((struct.unpack("<B", d)[0] >> 3) & 0x1f) + 0x03 
                    loc += len(data)-1
                    for j in range(num):
                        data.append(data[loc+j])
                else:
                    data.append(readbyte())
            
        data = data[:total]

        g = open(os.path.join('g', '{}.gb'.format(hex(gi)[2:].zfill(2))), 'wb')
        g.write(data)
        g.close()

        print('Decompressed {} ({})'.format(hex(gi), hex(l)))

print ("Done..!")
rom.close()
