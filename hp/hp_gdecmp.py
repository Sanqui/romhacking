from hp_decmp import *
import struct

def readbyte():
    return ord(rom.read(1))
def readshort():
    return struct.unpack("<H", rom.read(2))[0]

class GraphicsDecompressedException(Exception): pass
class InvalidGraphicsError(Exception): pass

def decomp():
    a = readbyte()
    c = a & 3
    vrambank = c & 0x10
    cmode = ((a & 8) // 8) + 1
    print("Compressed mode {}".format(cmode))
    if cmode == 1:
        return
        c = readbyte()
        if c-1 != 0:
            a = readbyte()
            if a == 0:
                c -= 1
                #fd1
            #bit 7,a
        else:
            a = readbyte()
            if a == 0: raise GraphicsDecompressedException()
            #bit 7, a
            #ld b, a
            #jr nz, blah
            
                
    elif cmode == 2:
        data = bytearray()
        try:
            for i in range(1024):
                modes = readbyte()
                #print(hex(modes), bin(modes))
                for mode in bin(modes)[2:].zfill(8):
                    if int(mode) == 0:
                        data.append(readbyte())
                    else:
                        c = readbyte()
                        a = readbyte()
                        if (c + a) == 0:
                            raise GraphicsDecompressedException()
                            
                        b = (a & 0x0f)
                        a = (abs(a & 0xf0) // 0x10)+3
                        loc = len(data)-(b*0x100+c)
                        for i in range(a):
                            data.append(data[loc+i])
        except GraphicsDecompressedException:
            return data
        except IndexError:
            print ("IndexError: {}/{} [{} {}], {}/{}".format(loc, len(data), hex(b), hex(c), i, a))
            return
        except InvalidGraphicsError:
            return
    return

if __name__ == "__main__":
    rom = open(argv[1], 'rb')
    rom.seek(0x134)
    name = rom.read(11)
    offsets = []
    if name == b"HPCOSECRETS":
        rom.seek(absp(0x09, 0x5000))
        for i in range(0x800):
            bank, offset = readbyte(), readshort()
            print(hex(bank), hex(offset))
            offsets.append(absp(bank, offset))
        #offset = absp(0xa4, 0x5eb5)
        #offset = absp(0x97, 0x5293)
    else:
        exit("Unsupported game {}".format(name))
    
    for i, offset in enumerate(offsets):    
        print(hex(i), hex(offset))
        rom.seek(offset)
        data = decomp()
        if data:
            with open('d/{}.gb'.format(hex(i)[2:].zfill(3)), 'wb') as f:
                f.write(data)
        else:
            print("Invalid gfx!")
