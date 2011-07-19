#!/usr/bin/python3

# punika is a graphics decompresser for games using the Malias compression,
# roughly designed after LZ77, used in numerous Natsume games.
# Refer to 
# http://wikifang.meowcorp.us/wiki/Wikifang:Telefang_1_Translation_Patch/Malias_compression
# for details.
# punika currently supports Keitai Denjuu Telefang; Medarot 1, 2 and 3.
# punika creates a folder called g and places all game's compressed graphics
# in it raw, so it can be read by your favorite tile editor (Tile Molester, TLP,
# etc.)
# Use the -l option if you want to simply list the locations.
# -- Sanky

import struct
import os
import sys

class InvalidGraphicsError(BaseException):
    pass

def readshort():
    return struct.unpack("<H", rom.read(2))[0]
    
def readbyte():
    return struct.unpack("<B", rom.read(1))[0]
    
def abspointer(bank, offset):
    return bank*0x4000+offset-0x4000

def decompress(offset):
    rom.seek(offset)
    
    try:
        compressed = readbyte()
        data = bytearray() 
        total = readshort()
        if total > 0:
            if compressed == 0x00:
                for i in range(total):
                    data.append(readbyte())
            else:
                if compressed != 0x01:
                    raise InvalidGraphicsError(compressed)
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
                                if loc < 0:
                                    raise InvalidGraphicsError(loc)
                                else:
                                    data.append(data[loc+j])
                        else:
                            data.append(readbyte())
    except (InvalidGraphicsError, struct.error):
        return None, None
                
    return data[:total], compressed
        
graphics = {}


    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: python3 punika.py rom.gbc (-l)')
    if len(sys.argv) == 3:
        if sys.argv[2] == '-l':
            action = 'list'
    else:
        action = 'extract'
    rom = sys.argv[1]

    if not os.path.exists('g'+os.sep):
        os.makedirs('g')
    
    rom = open(rom, 'rb')
    rom.seek(0x134)
    game = rom.read(8)
    if game == b'TELEFANG':
        rom.seek(0x18000)
        for i in range(0x80):
            bank, target = struct.unpack("<BH", rom.read(3))
            if target > 0x7fff and target < 0xa000:
                graphics[i] = {'target':target, 'bank':bank}
            rom.read(1)
        rom.seek(0x1DE1)
        for i in range(0x80):
            pointer = struct.unpack("<H", rom.read(2))[0]
            if i in graphics:
                if pointer > 0x3fff and pointer < 0x8000:
                    graphics[i]['pointer'] = pointer
                else:
                    del graphics[i]
    elif game == b'MEDAROT ':
        rom.seek(0x10f0)
        for i in range(0x80):
            p = readshort()
            rom.seek(p)
            g = {}
            g['bank'] = readbyte()
            g['pointer'] = readshort()
            g['target'] = readshort()
            if g['target'] > 0x7fff and g['target'] < 0xa000 and g['pointer'] > 0x3fff and g['pointer'] < 0x8000:
                graphics[i] = g
            rom.seek(0x10f0+i*0x2)
    elif game == b'MEDAROT2':
        rom.seek((0x3b*0x4000)+0x282b)
        for i in range(0xff):
            g = {}
            g['bank'] = readbyte()
            g['target'] = readshort()
            rom.seek(0x3a20+(i*0x2))
            g['pointer'] = readshort()
            if g['target'] > 0x7fff and g['target'] < 0xa000 and g['pointer'] > 0x3fff and g['pointer'] < 0x8000:
                graphics[i] = g
            rom.seek((0x3b*0x4000)+0x282b+(i*0x4)+4)
    elif game == b'MEDAROT3':
        rom.seek((0x39*0x4000)+0x306a)
        for i in range(0x1ff):
            g = {}
            g['bank'] = readbyte()
            g['target'] = readshort()
            g['vrambank'] = readbyte()
            rom.seek(0x3995+(i*0x2))
            g['pointer'] = readshort()
            if g['target'] > 0x7fff and g['target'] < 0xa000 and g['pointer'] > 0x3fff and g['pointer'] < 0x8000:
                graphics[i] = g
            rom.seek((0x39*0x4000)+0x306a+(i*0x4)+4)
    else:
        os.quit('Unsupported ROM.')
    
    if action == 'list':
        for i, g in graphics.items():
            print ("{:>4} - bank {:>4} + {:>8} ({:>8}) read in {:>7}".format(hex(i),
            hex(g['bank']), 
            hex(g['pointer']), 
            hex(abspointer(g['bank'], g['pointer'])), hex(g['target'])))
    
    elif action == 'extract':
        for gi, g in graphics.items():
            l = abspointer(g['bank'], g['pointer'])

            data, compressed = decompress(l)

            if data is None:
                print("{} ({}) is invalid!".format(hex(gi), hex(l)))
            elif len(data) == 0:
                print('{} ({}) is blank!'.format(hex(gi), hex(l)))
            else:
                g = open(os.path.join('g', '{}.gb'.format(hex(gi)[2:].zfill(2))), 'wb')
                g.write(data)
                g.close()

                print('{} {} ({})'.format("Decompressed" if compressed else "Exctracted", hex(gi), hex(l)))

    print ("Done..!")
    rom.close()
