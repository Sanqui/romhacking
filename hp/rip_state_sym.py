# I hate

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

rom = open("hp1.gbc", "rb")

rom.seek(0x4000 * 4 + 0x18b9)
for i in range(0x50):
    bank = readbyte()
    enter = readshort()
    init = readshort()
    state = readshort()
    leave = readshort()
    
    print(f"; State {i:02x}: ")
    print(f"{bank:02x}:{enter:04x} State{i:02x}Enter")
    print(f"{bank:02x}:{init:04x} State{i:02x}Init")
    print(f"{bank:02x}:{state:04x} State{i:02x}")
    print(f"{bank:02x}:{leave:04x} State{i:02x}Leave")
    print()

