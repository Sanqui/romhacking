PRINT_SCRIPTS = True
PRINT_SCRIPT_SYMBOLS = False
MAP_COUNT = 122
MAP_STRINGS = 2429
QUEST_STRINGS = 2361
SPELL_STRINGS = 2847
ITEM_STRINGS = 1875
CARD_STRINGS = 2132

rom = open("hp2.gbc", "rb")

class NotPointerException(ValueError): pass

def readpointer(bank=None):
    if not bank: bank = rom.tell()/0x4000
    s = readshort()
    if 0x4000 > s or 0x8000 <= s:
        raise NotPointerException(s)
    return (bank * 0x4000) + (s - 0x4000)

def readshort():
    return readbyte() + (readbyte() << 8)

def readbyte():
    return ord(rom.read(1))

COMMANDS = {
    0x00: "END",
    0x01: "RET",
    0x03: "SKIP",
    0x04: "SKIPIF",
    0x05: "SKIPIFNOT",
    0x06: "CALL",
    0x07: "JUMP",
    0x08: "JUMPVAR",
    0x09: "EQUAL",
    0x0b: "LESSTHAN",
    0x0f: "SET",
    0x13: "SETX",
    0x14: "SETY",
    0x15: "PARAM0",
    0x16: "PARAM1",
    0x17: "PARAM2",
    0x19: "MOVE",
    0x1b: "STOPMOVE",
    0x1e: "HIDE",
    0x21: "ANIM",
    0x27: "WAIT",
    0x28: "WARP",
    0x2a: "GIVECOMBO",
    0x2c: "QUESTDONE",
    0x2e: "SFX",
    0x2f: "MUSIC",
    0x30: "STOPMUSIC",
    0x33: "MSG",
    0x35: "BOSSBATTLE",
    0x38: "GIVEITEM",
    0x39: "TAKEITEM",
    0x3a: "HOSPITAL",
    0x3b: "FADEGREEN",
#    0x27: "CARDCOMBO1"
    0x3c: "GIVECARD",
    0x3d: "TAKECARD",
    0x3e: "FADERED",
    0x3f: "GIVESICK",
    0x40: "TAKESICK",
    0x41: "GIVEPOINTS",
    0x42: "TAKEPOINTS",
    0x43: "GIVESP",
    0x44: "TAKESP",
    0x46: "SWAPN",
    0x47: "JOINGROUP",
    0x48: "LEAVEGROUP",
    0x49: "RESTORE",
    0x4a: "WHITE",
    0x51: "SELECTMSG",
    0x54: "SHOP/POINTS",
    0x55: "SPECIAL",
    0x56: "LOCK",
    0x57: "UNLOCK",
    0x5f: "BLOCKING",
    0x61: "HEAL", # bool, should msg appear
    0x62: "SETQUEST",
    0x6c: "GETEQUIP",
    0x69: "NUMITEM", # puts number of item in 254
    0x6a: "GIVESPELL",
    0x79: "WARP2",
    0x7f: "SYSMSG",
}

GAME_STRINGS = open("hp2uk.txt").read().split('\n')

map_script_addresses = []

for i in range(0, MAP_COUNT+1): # TODO map count
    rom.seek(0x0c*0x4000 + 1 + i*3)
    bank = readbyte()
    offset = readshort()
    map_script_addresses.append(0x4000*bank + offset)
    
    if PRINT_SCRIPT_SYMBOLS:
        print "{:02X}:{:04X} Script_{}".format(bank, offset,
            GAME_STRINGS[MAP_STRINGS-1+i].replace("'", '').title().replace(' ', ''))
    
# Sorry about this mess, but I don't really care

script_params = [0, 0, 0]
last_numitem = 0

map_num = 0
rom.seek(map_script_addresses[map_num])
k = 0
cur_map_scripts = []

if not PRINT_SCRIPTS: quit()
#while True:
for x in range(1048*40):
    if k >= 3112 and map_num == MAP_COUNT-2: break
    if rom.tell() in map_script_addresses:
        k = 0
        km = 0
        map_num = map_script_addresses.index(rom.tell())
        map_name = GAME_STRINGS[MAP_STRINGS-1+map_num]
        if map_num == 0:
            map_name = ""
        print "--- {:02}. {}  @{:2x}:{:4x} ---".format(map_num, map_name, rom.tell()/0x4000, rom.tell()%0x4000+0x4000)
        numscripts = readbyte()
        k+=1
        print "{} scripts".format(numscripts)
        cur_map_scripts = []
        for s in range(numscripts):
            cur_map_scripts.append(((readbyte()<<8) + readbyte()) + numscripts*2 + 1)
            k += 2
        print cur_map_scripts
    if k in cur_map_scripts:
        print ""
        print "; script {}/{} of {}".format(cur_map_scripts.index(k), len(cur_map_scripts), map_name)
    command = readbyte()
    if command == 0xff:
        # ends of banks are filled with 0xff
        while command == 0xff:
            command = readbyte() # first byte in bank is byte id
        continue
    k += 1
    km += 1
    end = False
    if command == 0 and rom.tell() in map_script_addresses:
        print "{:04}| END\n".format(k)
        end = True
    elif command == 0:
        params = [readbyte(), readbyte()]
        k += 2
        km += 2
        if params[0] != 0 or params[1] != 0:
            rom.seek(rom.tell()-2)
            k -= 2
            print "          {:02}:{:04}| $00 END\n".format(map_num, km-1, *params)
        else:
            print "          {:02}:{:04}| $00 END         {:3} {:3}\n".format(map_num, km-3, *params)
        continue
    if not end:
        command_name = COMMANDS.get(command, "?")
        params = [readbyte(), readbyte()]
        k += 2
        km += 2
        
        string = ""
        text = ""
        if command_name in ("MSG", "SYSMSG"):
            try:
                text = GAME_STRINGS[params[0]*256 + params[1]]
            except IndexError:
                text = ""
            string = "face {}".format(script_params[0])
        elif command_name == "SELECTMSG":
            num = params[0]*256 + params[1]
            text = "{}\n  {}/{}".format(GAME_STRINGS[num], GAME_STRINGS[num+1], GAME_STRINGS[num+2])
        elif command_name == "MOVE":
            string = "object {}, direction {}".format(script_params[0], script_params[2])
        elif "POINTS" in command_name:
            string = "house {}".format(script_params[0])
        elif command_name in ("GIVEITEM", "NUMITEM", "TAKEITEM"):
            string = GAME_STRINGS[ITEM_STRINGS+params[0]]
            if command_name == "NUMITEM":
                last_numitem = params[0]
        elif command_name in ("GIVECARD", "TAKECARD"):
            string = GAME_STRINGS[CARD_STRINGS+params[0]]
        elif "SKIP" in command_name:
            string = "to {}".format(k - 3 + 3*params[0])
        elif command_name in ("JUMP", "CALL"):
            string = "to {:02}:{:04}".format(script_params[0], params[0]*0x100 + params[1])
        elif command_name == "PARAM0": script_params[0] = params[0]
        elif command_name == "PARAM1": script_params[1] = params[0]
        elif command_name == "PARAM2": script_params[2] = params[0]
        elif command_name == "SETQUEST":
            string = GAME_STRINGS[QUEST_STRINGS+params[0]]
        elif command_name in ("EQUAL", "LESSTHAN"):
            if params[0] == 0:
                if GAME_STRINGS[QUEST_STRINGS+params[1]].strip():
                    string = "quest {}".format(GAME_STRINGS[QUEST_STRINGS+params[1]])
                else:
                    string = "unnamed quest {}".format(params[1])
            elif params[0] == 250:
                string = "result of last battle?"
            elif params[0] == 254:
                #string = "quantity of {}".format(GAME_STRINGS[1401+last_numitem])
                # meh
                string = "result/quantity/item"
        elif command_name in "WARP":
            if params[0] != 0xff:
                string = GAME_STRINGS[MAP_STRINGS+params[0]]
        elif command_name in "WARP2":
            string = GAME_STRINGS[MAP_STRINGS+params[0]]
        elif command_name == "SHOP/POINTS":
            if params[0] == 0:
                string = "shop {}".format(params[1])
            elif params[0] == 1:
                string = "house points"
        elif command_name == "GIVESPELL":
            string = GAME_STRINGS[SPELL_STRINGS+params[0]]
        if string: string = "; "+string+""
        print "@{:2X}:{:4X}  {:02}:{:04}| ${:02x} {:11} {:3} {:3}  {}".format(
            (rom.tell()-3)/0x4000, (rom.tell()-3)%0x4000+0x4000,
            map_num, km-3, command, command_name, params[0] if params[0] or params[1] else "", params[1] or " ", string)
        if text: print " "+text
    if command == 0:
        print "     |"
    if end or rom.tell() in map_script_addresses:
        k = 0
        map_num = map_script_addresses.index(rom.tell())
        print "--- {:02}. {} ---".format(map_num, GAME_STRINGS[MAP_STRINGS-1+map_num])
