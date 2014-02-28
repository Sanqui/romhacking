#!/usr/bin/python3

# puneedle is a graphics decompressor for malias2.
# http://wikifang.meowcorp.us/wiki/Wikifang:Telefang_2_Translation_Patch/Malias2_compression
# (described by kmeisthax)
# dumps stuff into g2/
# some false positives--gotta find a pointer table..
# (also palettes?  and a way to convert them all to pngs?  that would be neat.)

import struct
import os
import sys

class InvalidGraphicsError(BaseException):
    pass

def readint():
    return struct.unpack("<I", rom.read(4))[0]

def readshort():
    return struct.unpack("<H", rom.read(2))[0]
    
def readbyte():
    return struct.unpack("<B", rom.read(1))[0]
    
def abspointer(bank, offset):
    return bank*0x4000+offset-0x4000

def decompress(offset):
    rom.seek(offset)
    
    magic = readshort()
    if magic != 0x654c: raise InvalidGraphicsError("Wrong magic.")
    total = readint()
    if total > 0x10000: raise InvalidGraphicsError("Insane size: "+hex(total))
    print("total is", hex(total))
    data = bytearray()
    first = True
    try: 
        if total > 0:
            while len(data) < total: 
                modes = readbyte()
                #print(bin(modes))
                for i in range(4):
                    mode = ((modes >> (i*2+1)) % 2 << 1) + ((modes >> i*2)%2)
                    #print("mode: ", mode)
                    if first and mode in (0, 1): raise InvalidGraphicsError("Begins with mode "+str(mode))
                    first = False
                    if mode == 0:
                        lz = readshort()
                        loc = (lz & 0b111111111111)+5 
                        num = (lz >> 12)+3
                        #print(bin(lz), hex(loc), hex(num))
                        for j in range(num):
                            data.append(data[len(data)-loc])
                    elif mode == 1:
                        lz = readbyte()
                        loc = (lz & 0b11)+1
                        num = (lz >> 2)+2
                        #print(bin(lz), hex(loc), hex(num))
                        for j in range(num):
                            #print(j, data, len(data), len(data)-loc, len(data)-loc+j)
                            data.append(data[len(data)-loc])
                    elif mode == 2:
                        data.append(readbyte())
                    elif mode == 3:
                        for i in range(mode):
                            data.append(readbyte())
    except IndexError:# raise
        raise InvalidGraphicsError()
                
    return data[:total]
        
graphics = {}


    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: python3 puneedle.py rom.gbc')
    rom = sys.argv[1]

    if not os.path.exists('g2'+os.sep):
        os.makedirs('g2')
    
    rom = open(rom, 'rb')
    #rom.seek(0x134)
    #game = rom.read(8)
    
    rom.seek(0x5036d6)
    i = 0
    while True:
        l = rom.tell()
        try:
            s = readshort()
        except struct.error:
            break
        if s == 0x654c:
            print("Magic found at {}".format(hex(rom.tell())))
            try:
                g = decompress(l)
            except InvalidGraphicsError as ex:
                print("Not OK:", str(ex))
            else:
                print("OK")
                with open("g2/{:04}-{}.gba".format(i, hex(l)), 'bw') as f:
                    f.write(g)
                i += 1
                
        rom.seek(l+1)

    print ("Done..!", i)
    rom.close()
