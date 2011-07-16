#!/usr/bin/python3

# punika is a graphics decompressor for the game Keitai Denjuu Telefang.
# It creates a folder called g and places all game's compressed graphics in it
# in raw, so it can be read by your favorite tile editor (Tile Molester, TLP,
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
    if target > 0x8000 and target < 0xa000:
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
            de = readshort()
            for i in range(0x10):
                carry = de & 1
                de = de // 2
                #print ('de = {}\t[{}]'.format(hex(de), carry))
                if carry:
                    e = rom.read(1)
                    d = rom.read(1)
                    de_ = -(struct.unpack("<H", e+d)[0]  & 0x07ff) 
                    a = ((struct.unpack("<B", d)[0] >> 3) & 0x1f) + 0x03 
                    #print(d, hex(struct.unpack("<B", d)[0] >> 3), hex((struct.unpack("<B", d)[0] >> 3) & 0x1f), hex(a), ';', hex(de_), hex(de_+hl))
                    de_+=len(data)-1
                    for i in range(a):
                        data.append(data[de_])
                        #print("{:>7} <<< {:>4}\t(de_={}, bc={}, a={})".format(hex(hl), hex(data[hl]), hex(de_), hex(bc), hex(a)))
                        de_ += 1
                else:
                    data.append(readbyte())
                    #print ("{:>7} <<< {:>4}\t({})".format(hex(hl),hex(data[hl]), hex(rom.tell()-1%0x4000)))
            
        data = data[:total]

        g = open(os.path.join('g', '{}.gb'.format(hex(gi)[2:].zfill(2))), 'wb')
        g.write(data)
        g.close()

        print('Decompressed {} ({})'.format(hex(gi), hex(l)))

print ("Done..!")
rom.close()
