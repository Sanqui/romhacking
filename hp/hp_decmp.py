# Dumps text from the HP2.

from sys import argv, exit
import os.path as path
import csv

#NUM_LANGUAGES = 10
NUM_LANGUAGES = 2
NUM_STRINGS = 3796

def absp(bank, memory):
   return (bank*0x4000)+memory-0x4000 

def relp(address):
    return (address // 0x4000, 0x4000 + address % 0x4000)

class NotPointerException(ValueError): pass

def readpointer(bank=None):
    if not bank: bank = rom.tell()/0x4000
    s = readshort()
    if 0x4000 > s or 0x8000 <= s:
        raise NotPointerException(s)
    return (bank * 0x4000) + (s - 0x4000)

def readbyte():
    return ord(rom.read(1))

def readshort():
    return readbyte() + (readbyte() << 8)

def writebyte(byte):
    rom.write(bytes([byte]))

def writeshort(short):
    writebyte(short & 0xff)
    writebyte(short >> 8)

def decompress_string(address, compressed=True):
    rom.seek(address)
    if not compressed:
        string = ""
        byte = readbyte()
        if byte & 0x7f == 0x7f:
            return string
        else:
            string += chr(byte)
        
    else:
        curbit = 8
        curbyte = -1
        def readbit():
            nonlocal curbit, curbyte
            if curbit >= 8:
                curbyte = readbyte()
            curbit = curbit & 7
            out = curbyte & (1<<curbit)
            curbit += 1
            return bool(out)
        
        string = ""
        keyptr = 0
        while True:
            bit = readbit()
            keyptr = key[(keyptr << 1) + bit]
            if keyptr & 0x80:
                char = keyptr & 0x7f
                if char == 0x7f:
                    return string
                else:
                    string += chr(char)
                    keyptr = 0
        

language_strings = []

if __name__ == "__main__":
    if len(argv) < 3 or argv[2] not in ("extract", "insert"):
        exit("usage: hp_decmp.py rom.gbc (extract|insert)")
    command = argv[2]
    rom = open(argv[1], 'r+b')
    rom.seek(0x134)
    name = rom.read(11)
    #if name == b"HARRYPOTTER":
    #    keyaddress = 0x823e7
    #    address = absp(0x20,0x648b) # EN US
    #    #keyaddress = 0x9a3e7
    #    #address = keyaddress + 0xa4 # EN UK
    if name == b"HPCOSECRETS":
        rom.seek(0x3ff0)
        hack_tag = rom.read(9)
        if hack_tag.startswith(b"Sanqui"):
            compressed = False
            num_languages = 1
        else:
            compressed = True
            num_languages = NUM_LANGUAGES
        langbanksaddress = absp(0x06, 0x44e4)
        
        #keyaddress = 0x76c7e
        #address = keyaddress + 0xa4 # EN US PARTIAL, ONLY STORES SEPARATE STRINGS
        #keyaddress = absp(0x1f,0x6c7e)
        #address = absp(0x1f, 0x6d22) # EN UK
    else:
        exit("Unsupported game {}".format(name))

    rom.seek(langbanksaddress)
    lang_banks = list(rom.read(num_languages))
    
    for lang_bank in lang_banks:
        #print(f"== Lang Bank 0x{lang_bank:02x} ==")
        
        keyaddress = absp(lang_bank, 0x6c7d)
        rom.seek(keyaddress)
        key_length = readbyte()*2
        key = rom.read(key_length) #0xa4)
        
        rom.seek(absp(lang_bank, 0x4001))
        string_addresses = []
        for i in range(NUM_STRINGS):
            bankoffset = readbyte()
            address = readshort()
            string_addresses.append(absp(lang_bank+bankoffset, 0x4000+address))
            
        strings = []
        for i, address in enumerate(string_addresses):
            #print(hex(address))
            string = decompress_string(address, compressed=compressed)
            strings.append(string)
            if i == 1:
                #print(f" (Language: {string})")
                print("Reading language:", string)
            #print(hex(address), hex(rom.tell()), string)
        language_strings.append(strings)
    
    if command == "extract":
        print("Done, outputting hp2.csv")
        
        if path.exists("hp2.csv"):
            print("Warning: hp2.csv exists, please delete")
        else:
            f = open("hp2.csv", "w")
            writer = csv.writer(f)
            writer.writerow(["num", "original", "new"])
            for i in range(NUM_STRINGS):
                string = language_strings[0][i]
                if string == "&":
                    string = language_strings[1][i]
                writer.writerow([i, string, ""])
    elif command == "insert":
        if compressed:
            exit("Can only insert in custom ROM.")
        f = open("hp2.csv", "r")
        reader = csv.reader(f)
        new_strings = []
        next(reader)
        for row in reader:
            string = row[2]
            if not string.strip():
                string = row[1]
            new_strings.append(string)
        
        if len(new_strings) != NUM_STRINGS:
            print(f"Warning: wrong count of strings in csv ({len(new_strings)}, not {NUM_STRINGS})")
        
        lang_bank = lang_banks[0]
        
        #rom.seek(absp(lang_bank, 0x4001))
        starting_bank = lang_bank + 2 # + readbyte() + 2
        starting_address = 0x4000 #readshort()
        
        new_offsets = []
        rom.seek(absp(starting_bank, starting_address))
        numbanks = 0
        for string in new_strings:
            if ((rom.tell()%0x4000) + len(string) + 1) > 0x4000:
                numbanks += 1
                rom.write(b'\xff'* (0x4000 - (rom.tell() % 0x4000)))
            bank_offset = (rom.tell() // 0x4000) - lang_bank
            offset = rom.tell() % 0x4000 + 0x4000
            new_offsets.append((bank_offset, offset))
            string = string.replace('’', "'").replace('…', '...')
            try:
                rom.write(string.encode('ascii'))
            except UnicodeEncodeError:
                print(f"Warning: string contains non-ASCII: {string}")
                rom.write(string.encode('ascii', 'replace'))
            writebyte(0xff)
        
        rom.seek(absp(lang_bank, 0x4001))
        for bank_offset, offset in new_offsets:
            writebyte(bank_offset)
            writeshort(offset)
    
        print(f"Done, wrote {numbanks} banks of new text.")
        
