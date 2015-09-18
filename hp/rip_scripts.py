rom = open("hp1.gbc", "rb")

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
    0x03: "SKIP",
    0x04: "SKIPIF",
    0x05: "SKIPIFNOT",
    0x09: "EQUAL",
    0x0b: "LESSTHAN",
    0x0f: "SET",
    0x15: "PARAM0",
    0x16: "PARAM1",
    0x17: "PARAM2",
    0x19: "MOVE",
    0x1e: "HIDE",
    0x21: "ANIM",
    0x27: "WAIT",
    0x28: "WARP",
    0x2a: "GIVECOMBO",
    0x2c: "QUESTDONE",
    0x2e: "SFX",
    0x2f: "MUSIC",
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
    0x49: "RESTORE",
    0x4a: "WHITE",
    0x51: "SELECTMSG",
    0x54: "SHOP/POINTS",
    0x55: "SPECIAL",
    0x61: "HEAL", # bool, should msg appear
    0x62: "SETQUEST",
    0x6c: "GETEQUIP",
    0x69: "NUMITEM", # puts number of item in 254
    0x6a: "GIVESPELL",
    0x79: "WARP2",
    0x7f: "SYSMSG",
}

GAME_STRINGS = open("hp1uk.txt").read().split('\n')

map_script_addresses = []

for i in range(0, 0x44): # TODO map count
    rom.seek(9*0x4000 + 1 + i*3)
    bank = readbyte()
    offset = readshort()
    map_script_addresses.append(0x4000*bank + offset)
    
# Sorry about this mess, but I don't really care

script_params = [0, 0, 0]
last_numitem = 0

map_num = 0
rom.seek(map_script_addresses[map_num])
k = 0
#while True:
for x in range(1048*40):
    if k >= 23441 and map_num == 67: break
    if rom.tell() in map_script_addresses:
        k = 0
        map_num = map_script_addresses.index(rom.tell())
        map_name = GAME_STRINGS[2115+map_num]
        if map_num == 0:
            map_name = ""
        print "--- {:02}. {} ---".format(map_num, map_name)
    command = readbyte()
    if command == 0xff:
        # ends of banks are filled with 0xff
        while command == 0xff:
            command = readbyte() # first byte in bank is byte id
        continue
    k += 1
    end = False
    if command == 0 and rom.tell() in map_script_addresses:
        print "{:05}| END\n".format(k)
        end = True
    elif command == 0:
        params = readshort()
        k += 2
        if params != 0:
            rom.seek(rom.tell()-2)
            k -= 2
        print "{:02}:{:05}| $00 END           0   0\n".format(map_num, k)
        continue
    if not end:
        command_name = COMMANDS.get(command, "?")
        params = [readbyte(), readbyte()]
        k += 2
        
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
            string = GAME_STRINGS[1401+params[0]]
            if command_name == "NUMITEM":
                last_numitem = params[0]
        elif command_name in ("GIVECARD", "TAKECARD"):
            string = GAME_STRINGS[1621+params[0]]
        elif "SKIP" in command_name:
            string = "to {}".format(k + 3*params[0])
        elif command_name == "PARAM0": script_params[0] = params[0]
        elif command_name == "PARAM1": script_params[1] = params[0]
        elif command_name == "PARAM2": script_params[2] = params[0]
        elif command_name == "SETQUEST":
            string = GAME_STRINGS[2021+params[0]]
        elif command_name in ("EQUAL", "LESSTHAN"):
            if params[0] == 0:
                if GAME_STRINGS[2021+params[1]].strip():
                    string = "quest {}".format(GAME_STRINGS[2021+params[1]])
                else:
                    string = "unnamed quest {}".format(params[1])
            elif params[0] == 250:
                string = "result of last battle?"
            elif params[0] == 254:
                #string = "quantity of {}".format(GAME_STRINGS[1401+last_numitem])
                # meh
                string = "result/quantity/item"
        elif command_name == "WARP":
            string = GAME_STRINGS[2116+params[0]]
        elif command_name == "SHOP/POINTS":
            if params[0] == 0:
                string = "shop {}".format(params[1])
            elif params[0] == 1:
                string = "house points"
        elif command_name == "GIVESPELL":
            string = GAME_STRINGS[9+params[0]]
        if string: string = "; "+string+""
        print "{:02}:{:05}| ${:02x} {:11} {:3} {:3}  {}".format(map_num, k, command, command_name, params[0], params[1], string)
        if text: print " "+text
    if command == 0:
        print "     |"
    if end or rom.tell() in map_script_addresses:
        k = 0
        map_num = map_script_addresses.index(rom.tell())
        print "--- {:02}. {} ---".format(map_num, GAME_STRINGS[2117+map_num+1])
