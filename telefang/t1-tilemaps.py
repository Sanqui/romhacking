#!/usr/bin/python3

# t1-tilemaps is a tilemap decompresser for Telefang 1.
# http://wikifang.meowcorp.us/wiki/User:Kmeisthax/Findings/2013/4/23/Tilemap_compression --kmeisthax

import struct
import os
import sys

class InvalidPointerException(Exception): pass

def readshort():
    return struct.unpack("<H", rom.read(2))[0]

def readbeshort():
    return struct.unpack(">H", rom.read(2))[0]
    
def readbyte():
    return struct.unpack("<B", rom.read(1))[0]
    
def abspointer(bank, offset):
    if offset < 0x4000 or offset >= 0x8000:
        raise InvalidPointerException(offset)
    return bank*0x4000+offset-0x4000

MODE_LITERAL = 0
MODE_REPEAT = 1
MODE_INC = 2
MODE_DEC = 3

def decompress_tmap(offset):
    rom.seek(offset)
    compressed = readbyte()
    #print hex(offset), compressed
    tmap = b""

    if compressed: # compressed
        while True:
            b = readbyte()
            if b == 0xff:
                break
            elif b == 0xfe:
                tmap += '\xfe'
            command = (b >> 6) & 0b11
            count = b & 0b00111111
            if command == MODE_LITERAL:
                for i in range(count+1):
                    tmap += chr(readbyte())
            elif command == MODE_REPEAT:
                byte = readbyte()
                for i in range(count+2):
                    tmap += chr(byte)
            elif command == MODE_INC:
                byte = readbyte()
                for i in range(count+2):
                    tmap += chr((byte+i)&0xff)
            elif command == MODE_DEC:
                byte = readbyte()
                for i in range(count+2):
                    tmap += chr((byte-i)%0xff)
    else:  
        while True:
            b = readbyte()
            if b == 0xff:
                break
            tmap += chr(b)  
    #while True:
    #    byte = readbyte()
                
    return compressed, tmap

def compress_tmap(tmap):
    compressed = b"\x01"
    literal_bytes = []
    while tmap:
        curbyte = ord(tmap[0])
        methods = {MODE_REPEAT: 0, MODE_INC: 0, MODE_DEC: 0}
        # repeat
        for i, byte in zip(range(64), tmap[1:]):
            if ord(byte) != curbyte:
                break
            methods[MODE_REPEAT] += 1
        
        # inc
        for i, byte in zip(range(64), tmap[1:]):
            if ord(byte) != (curbyte+1+i)&0xff:
                break
            methods[MODE_INC] += 1
        
        # dec
        for i, byte in zip(range(64), tmap[1:]):
            if ord(byte) != (curbyte-1-i)&0xff:
                break
            methods[MODE_DEC] += 1
        
        best = max(methods, key=methods.get)
        if methods[best] >= 1:
            if literal_bytes:
                compressed += chr((MODE_LITERAL << 0x6) + len(literal_bytes)-1)
                for byte in literal_bytes:
                    compressed += chr(byte)
                literal_bytes = []
            compressed += chr((best << 0x6) + methods[best]-1)
            compressed += chr(curbyte)
            tmap = tmap[methods[best]+1:]
        else:
            literal_bytes.append(curbyte)
            tmap = tmap[1:]
        
        # TODO literals over 64 bytes
        
        #print best, methods, hex(curbyte),  literal_bytes, compressed
    compressed += b'\xff'
    return compressed

MODE = ('dump', 'mediawiki', 'compress')[1]
SET = ('tilemaps', 'attrmaps')[1]

if SET == 'tilemaps':
    BANK = 0x3e
    NUMTILEMAPS = 0xc3
elif SET == 'attrmaps':
    BANK = 0x08
    NUMTILEMAPS = 0xC3

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('usage: python3 t1-tilemaps.py rom.gbc')
    rom = sys.argv[1]

    if not os.path.exists(SET+os.sep):
        os.makedirs(SET)
    
    if MODE == 'dump' or MODE == 'mediawiki':
        
        rom = open(rom, 'rb')
        rom.seek(0x134)
        game = rom.read(8)
        if game == b'TELEFANG':
            pass
        else:
            os.exit('Unsupported ROM.')
        
        if MODE == 'mediawiki':
            print("""
""")
        
        for i in range(NUMTILEMAPS):
            rom.seek((BANK*0x4000)+(2*i))
            try:
                loc = abspointer(BANK, readshort())
            except InvalidPointerException:
                break
            
            compressed, tmap = decompress_tmap(loc)
            
            if MODE == 'dump':
                print hex(i), hex(loc), compressed, len(tmap), 'bytes'
                with open('tilemaps/{:02x}'.format(i), 'wb') as f:
                    f.write(tmap)
            elif MODE == 'mediawiki':
                print "\n\n===", hex(i),"==="
                print hex(i), hex(loc), compressed, len(tmap), 'bytes<br>'
                print "Use: "
                print
                print "<pre>"
                column = 0
                for byte in tmap:
                    if SET == 'attrmaps':
                        print "{:01x}".format(ord(byte)),
                    else:
                        print "{:02x}".format(ord(byte)),
                    column += 1
                    if column == 0x20 or byte == "\xfe":
                        print
                        column = 0
                print "</pre>"
        rom.close()
            
    
    elif MODE=='compress':
        '''lastloc = BANK*0x4000+0x200
        rom = open(rom, 'r+b')
        for i in range(NUMTILEMAPS):
            with open("tilemaps/{:02x}".format(i), 'rb') as f:
                tilemap = compress_tmap(f.read())
            rom.seek(lastloc)
            rom.write(tilemap)
            rom.seek(BANK*0x4000+(i*2))
            rom.write(struct.pack("<H", 0x4000+(lastloc%0x4000))[0])
            
            print hex(i), len(tilemap), hex(lastloc)
            lastloc += len(tilemap)
        
        rom.close()'''
            
            
        
        
        
        with open('tilemaps/0a', 'rb') as f:
            ctmap = compress_tmap(f.read())
        with open('tilemaps/0a.rle', 'wb') as f:
            f.write(ctmap)
    
    
    print ("Done..!")




#0xf8652







