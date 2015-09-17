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
    0x04: "SKIPIF",
    0x05: "SKIPIFNOT",
    0x09: "CMP",
    0x0f: "SET",
    0x15: "FACE/DIR",
    0x17: "SELECTOBJ",
    0x19: "MOVE",
    0x1e: "HIDE",
    0x21: "ANIM",
    0x27: "WAIT",
    0x2e: "PCM",
    0x33: "MSG",
    0x35: "BOSSBATTLE",
    0x38: "GIVEITEM",
#    0x27: "CARDCOMBO1"
    0x2a: "GIVECOMBO",
    0x3c: "GIVECARD",
    0x41: "GIVEPOINTS",
    0x42: "TAKEPOINTS",
    0x55: "SPECIAL",
    0x61: "HEAL", # bool, should msg appear
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
    
map_num = 0
rom.seek(map_script_addresses[map_num])
k = 0
#while True:
for x in range(1048*40):
    if rom.tell() in map_script_addresses:
        k = 0
        map_num = map_script_addresses.index(rom.tell())
        map_name = GAME_STRINGS[2115+map_num]
        if map_num == 0:
            map_name = ""
        print "--- {:02}. {} ---".format(map_num, map_name)
    command = readbyte()
    if command == 0xff: continue
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
        print "{:05}| $00 END           0   0\n".format(k)
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
        elif command_name == "GIVEITEM":
            string = GAME_STRINGS[1401+params[0]]
        elif command_name == "GIVECARD":
            string = GAME_STRINGS[1621+params[0]]
        if string: string = "("+string+")"
        print "{:05}| ${:02x} {:11} {:3} {:3}  {}".format(k, command, command_name, params[0], params[1], string)
        if text: print " "+text
    if command == 0:
        print "     |"
    if end or rom.tell() in map_script_addresses:
        k = 0
        map_num = map_script_addresses.index(rom.tell())
        print "--- {:02}. {} ---".format(map_num, GAME_STRINGS[2117+map_num+1])
