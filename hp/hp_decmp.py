# Dumps text from the HP1/2 games.
# For any other languages, please edit source.
# Prints junk at end so that all strings (including those without
# pointers) can be found.

from sys import argv, exit

def absp(bank, memory):
   return (bank*0x4000)+memory-0x4000 

def relp(offset):
    return (offset // 0x4000, 0x4000 + offset % 0x4000)

if __name__ == "__main__":
    rom = open(argv[1], 'rb')
    rom.seek(0x134)
    name = rom.read(11)
    if name == b"HARRYPOTTER":
        keyoffset = 0x823e7
        offset = absp(0x20,0x648b) # EN US
        #keyoffset = 0x9a3e7
        #offset = keyoffset + 0xa4 # EN UK
    elif name == b"HPCOSECRETS":
        keyoffset = 0x76c7e
        offset = keyoffset + 0xa4 # EN US PARTIAL, ONLY STORES SEPARATE STRINGS
        #keyoffset = absp(0x1f,0x6c7e)
        #offset = absp(0x1f, 0x6d22) # EN UK
    else:
        exit("Unsupported game {}".format(name))

    rom.seek(keyoffset)
    key = rom.read(0xa4)

    c = 0x01
    for i in range(0x30000):
        b = 0x00
        while True:
            rom.seek(offset)
            a = ord(rom.read(1))
            #print(hex(de),'reada: ',hex(a),'c:',hex(c),end="")
            a = a & c # only c
            b = key[(b * 2) + int((a & c) > 0)]
            #print(' bkey:',hex(b))
            c = c << 1
            if c > 255:
                offset += 1
                c = 1
            if (b << 1) > 255:
                a = (b << 1) % 256 + 1
                #print(hex(a))
                a = (a >> 1)
                if a == 0x7f:
                    print()
                    if c > 0x01:
                        offset += 1
                    c = 0x01
                    b = 0x00
                else:
                    print(chr(a), end="")
                break
