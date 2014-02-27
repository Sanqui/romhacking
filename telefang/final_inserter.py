#!/usr/bin/env python3
import sys
import struct

import requests

# Look at me!  I can copy-paste!  (again!)
class Special():
    def __init__(self, byte, default=0, bts=1, end=False, names=None):
        self.byte = byte
        self.default = default
        self.bts = bts
        self.end = end
        self.names = names if names else {}

specials = {}
specials["&"] = Special(0xe5, bts=2, names={0xc92c: "name", 0xd448: "num"})
specials['S'] = Special(0xe3, default=2)
specials['*'] = Special(0xe1, end=True)
specials['D'] = Special(0xe9)


table = {}
tablejp = {}

for line in open("original.tbl").readlines():
    if line.strip():
        a, b = line.strip('\n').split("=", 1)
        tablejp[b.replace("\\n", '\n')] = int(a, 16)
    
for line in open("patch.tbl").readlines():
    if line.strip():
        a, b = line.strip('\n').split("=", 1)
        table[b.replace("\\n", '\n')] = int(a, 16)

rom = open(sys.argv[1], 'r+b')

vwf_table = []
rom.seek(0x2fb00)
for i in range(256):
    vwf_table.append(struct.unpack("<B", rom.read(1))[0])

def pack_string(string):
    string = string.rstrip('\n')
    
    text_data = b"" 
    line_data = b""
    line_px = 0
    word_data = b""
    word_px = 0
    
    special = ""
    ended = False
    skip = False
    
    even_line = True
    
    for char in string:
        if skip:
            skip = False
            continue
        if special:
            if char in ">»":
                #sys.stderr.write( special + "\n")
                special = special[1:] # lstrip <
                is_literal = True
                try:
                    special_num = int(special, 16)
                except ValueError: # temporary
                    is_literal = False
                    
                if is_literal and not special.startswith("D"):
                    if special_num > 255:
                        print("Warning: Invalid literal special {} (0x{:3x})".format(special_num, special_num))
                        continue
                    word_data += bytes((special_num,))
                    word_px += vwf_table[special_num]
                else:
                    s = special[0]
                    if s not in specials.keys():
                        print("Warning: Invalid special: {}".format(special))
                        special = ""
                        continue
                    s = specials[s]
                    val = special[1:]
                    word_data += bytes((s.byte,))
                    matched = False
                    for value, name in s.names.items():
                        if name == val:
                            val = value
                            matched = True
                    
                    if not matched: val = int(val, 16)
                    
                    if val == "": val = s.default
                    
                    if s.bts:
                        fmt = "<"+("", "B", "H")[s.bts]
                        word_data += struct.pack(fmt, val)
                    
                    if s.end: ended = True
                    
                    if special[0] == "&":
                        if val == 0xd448: # num
                            word_px += 3*8
                        else:
                            word_px += 8*8
                
                special = ""
            else:
                special += char
        else:
            if char == "\\": skip = True
            if char in "<«":
                special = char
            else:
                try:
                    word_data += bytes((table[char],))
                    word_px += vwf_table[table[char]]+1
                except KeyError: # temporary
                    sys.stderr.write("Warning: Unknown char: " + char + "\n")
                    word_data += bytes((table["?"],))
                    word_px += vwf_table[table["?"]]+1
                if char in (" ", "\n"):
                    if line_px + word_px > (16*8 if even_line else 15*8):
                        text_data += line_data[:-1] + bytes((table['\n'],))
                        line_data, line_px = word_data, word_px
                        even_line = not even_line
                    else:
                        line_data += word_data
                        line_px += word_px
                    word_data, word_px = b"", 0
                if char == "\n":
                    text_data += line_data
                    line_data, line_px = b"", 0
                    even_line = not even_line
    if line_px + word_px > (16*8 if even_line else 15*8):
        text_data += line_data[:-1] + bytes((table['\n'],))
        line_data = word_data
    else:
        line_data += word_data
    text_data += line_data
    
    
    if not ended:
        text_data += b"\xe1\x00" # end chars
    
    return text_data

FAR_BANK = 0x1e
page_addresses = [0x40000, 0x99068, 0x100000, 0x114000, 0x11507B, 0x118000, 0x11C000, 0x120000, 0x124000, 0x128000, 0x1281D9, 0x12C000, 0x130000, 0x134000, 0x138000, 0x13C000, 0x140000, 0x144000, 0x145C9A, 0x158000, 0x15C000]
#page_addresses = [0x114000]

pages = []

print("Getting pages from Wikifang...")

for i, page_address in enumerate(page_addresses):
    rq = requests.get("http://wikifang.meowcorp.us/wiki/Wikifang:Telefang_1_Translation_Patch/Text_dump/{:X}?action=raw".format(page_address))
    assert rq.status_code == 200
    pages.append(rq.text)
    print("Getting pages...  {}/{} ({:.4}%) done".format(i+1, len(page_addresses), (float(i+1)/len(page_addresses))*100))

bank_texts = {}
    
for page in pages:
    mediawiki = page[page.find("{|"):]
    rows = mediawiki.split("|-")
    for row in rows:
        cols = row.split("\n|")[1:]
        if len(cols) == 3:
            try:
                ptr = int(cols[0], 16)
            except ValueError: # stuff like (No pointer)
                continue
            bank = ptr//0x4000
            if bank not in bank_texts.keys():
                bank_texts[bank] = {}
            bank_texts[bank][ptr] = (cols[1].rstrip(), cols[2].rstrip())

print("Done parsing mediawiki.")

far_data = b""
banks = {}

used_far_for = []

for bank, texts in bank_texts.items():
    if bank not in banks.keys():
        banks[bank] = [[], []]
    for ptr in sorted(texts.keys()):
        jptext, engtext = texts[ptr]
        #print(engtext)
        #print (engtext)
        string = pack_string(engtext)
        offset = None
        for offset1, string1 in zip(*banks[bank]):
            if string1 == string:
                #print("Yay dupe")
                offset = offset1
                string = b""
                break
        if not offset:
            space_in_bank = 0x4000 - ( len(texts)*2 + (len(b''.join(banks[bank][1]))) )
            if space_in_bank < 0x180:
                if bank not in used_far_for:
                    print ("0x{:2x} bytes left in bank 0x{:2x}, utilizing FAR...".format(space_in_bank, bank))
                used_far_for.append(bank)
                far_offset = 0x4000 + len(far_data)
                far_data += string
                string = b"\xec" + struct.pack("<H", far_offset)
            offset = 0x4000+len(texts)*2+(len(b''.join(banks[bank][1])))
        banks[bank][0].append(offset)
        banks[bank][1].append(string)
        #print (banks[bank][1])

print("Done packing all strings.")

bank_data_dict = {}

for bank in banks.keys():
    offsets, data = banks[bank]
    bank_data = b""
    for offset in offsets:
        bank_data += struct.pack("<H", offset)
    bank_data += b''.join(data)
    assert len(bank_data) <= 0x4000
    bank_data = bank_data.ljust(0x4000-1, b'\x00')
    bank_data_dict[bank] = bank_data

assert len(far_data) <= 0x4000

print ("Done making banks, will insert into ROM...")

rom = open(sys.argv[1], 'r+b')

for bank, data in bank_data_dict.items():
    rom.seek(bank*0x4000)
    rom.write(data)

rom.seek(FAR_BANK*0x4000)
rom.write(far_data)

rom.close()

print("Done?")
