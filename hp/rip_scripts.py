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
    0x2e: "PCM",
    0x33: "MSG",
    0x38: "GIVEITEM",
#    0x27: "CARDCOMBO1"
    0x2a: "GIVECOMBO",
    0x3c: "GIVECARD",
    0x55: "SPECIAL",
    0x7f: "SYSMSG",
}

GAME_STRINGS = open("hp1uk.txt").read().split('\n')

for i in range(1, 2): # TODO map count
    rom.seek(9*0x4000 + 1 + i*3)
    bank = readbyte()
    offset = readshort()
    rom.seek(bank*0x4000 + offset) # not a bug
    for k in range(128):
        while True:
            command = readbyte()
            command_name = COMMANDS.get(command, "?")
            params = [readbyte(), readbyte()]
            
            string = ""
            text = ""
            if command_name in ("MSG", "SYSMSG"):
                text = GAME_STRINGS[params[0]*256 + params[1]]
            elif command_name == "GIVEITEM":
                string = GAME_STRINGS[1401+params[0]]
            elif command_name == "GIVECARD":
                string = GAME_STRINGS[1621+params[0]]
            if string: string = "("+string+")"
            print "${:02x} {:11} {:3} {:3}  {}".format(command, command_name, params[0], params[1], string)
            if text: print " "+text
            if command == 0:
                print ""
                break
