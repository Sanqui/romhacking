# encoding: utf-8
from construct import *
from operator import iadd
mode = "print"
#if mode == "import":
#    from pokedex.db import connect, tables, util

# Amounts of maps in each bank.  As far as I know, this information doesn't
# exist in the rom, so I stole it shamelessly from Advancemap.
mapcounts = [54, 5, 5, 6, 7, 7, 8, 7, 7, 13, 8, 17, 10, 24, 13, 13, 14, 2, 2,
             2, 3, 1, 1, 1, 86, 44, 12, 2, 1, 13, 1, 1, 3]

#TODO: Do this using Construct as well!
def parse_script_for_item(rom, loc, brute_force=False):
    def readbyte(): return ord(rom.read(1))
    def readshort(): return ord(rom.read(1))+ord(rom.read(1))*256
    try: rom.seek(loc)
    except IOError: return None,None
    item = None
    amount = None
    giveitem = False
    while True:
        code = readbyte()
        if code == 0x1a: # copyvarifnot0
            loc = readshort()
            val = readshort()
            if loc == 0x8000:
                item = val
            elif loc == 0x8001:
                amount = val
        elif code == 0x09: # callstd
            std = readbyte()
            if std in (0, 1):
                giveitem = True
        elif code == 0x02: # end
            if giveitem:
                return item, amount
            else:
                return None, None
        else:
            if not brute_force:
                return None, None


class PokemonStringAdapter(Adapter):
    table = {0x00: ' ',
    0x01: '{PLAYER}',
    0x1B: 'é',
    0x2D: '&',
    0x5C: '(',
    0x5D: ')',
    0x79: '-UP',
    0x7A: '-DOWN',
    0x7B: '←',
    0x7C: '→',
    0xA1: '0',
    0xA2: '1',
    0xA3: '2',
    0xA4: '3',
    0xA5: '4',
    0xA6: '5',
    0xA7: '6',
    0xA8: '7',
    0xA9: '8',
    0xAA: '9',
    0xAB: '!',
    0xAC: '?',
    0xAD: '.',
    0xAE: '-',
    0xB0: '..',
    0xB1: '"',
    0xB2: '"2',
    0xB3: '\'2',
    0xB4: '\'',
    0xB5: 'mA',
    0xB6: 'fE',
    0xB7: '$',
    0xB8: ',',
    0xB9: '×',
    0xBA: '/',
    0xBB: 'A',
    0xBC: 'B',
    0xBD: 'C',
    0xBE: 'D',
    0xBF: 'E',
    0xC0: 'F',
    0xC1: 'G',
    0xC2: 'H',
    0xC3: 'I',
    0xC4: 'J',
    0xC5: 'K',
    0xC6: 'L',
    0xC7: 'M',
    0xC8: 'N',
    0xC9: 'O',
    0xCA: 'P',
    0xCB: 'Q',
    0xCC: 'R',
    0xCD: 'S',
    0xCE: 'T',
    0xCF: 'U',
    0xD0: 'V',
    0xD1: 'W',
    0xD2: 'X',
    0xD3: 'Y',
    0xD4: 'Z',
    0xD5: 'a',
    0xD6: 'b',
    0xD7: 'c',
    0xD8: 'd',
    0xD9: 'e',
    0xDA: 'f',
    0xDB: 'g',
    0xDC: 'h',
    0xDD: 'i',
    0xDE: 'j',
    0xDF: 'k',
    0xE0: 'l',
    0xE1: 'm',
    0xE2: 'n',
    0xE3: 'o',
    0xE4: 'p',
    0xE5: 'q',
    0xE6: 'r',
    0xE7: 's',
    0xE8: 't',
    0xE9: 'u',
    0xEA: 'v',
    0xEB: 'w',
    0xEC: 'x',
    0xED: 'y',
    0xEE: 'z',
    0xF0: ':',
    0xFA: '=',
    0xFB: '*',
    0xFC: '\n',
    0xFD: '@',
    0xFE: '+',} # TODO make this more unicodish
    def _encode(self, obj, context):
        return None # TODO
    def _decode(self, obj, c):
        string = ""
        for byte in obj:
            byte = ord(byte)
            if byte in self.table:
                string += self.table[byte]
            elif byte in (0xff,):
                break
            else:
                string += "{"+str(byte)+"}"
        return string

class PrintContext(Construct):
    def _parse(self, stream, context):
        #loc = Anchor('loc').parse(stream)
        print context
        #raise RuntimeError()
        
Item = Struct("item",
    PokemonStringAdapter(String("name", 14)),
    ULInt16("id"),
    ULInt16("price"),
    Byte("special1"),
    Byte("special2"),
    ULInt32("p_description"),
    ULInt16("u1"),
    Enum(Byte("pocket"),
        main = 1,
        pokeballs = 2,
        tms_hms = 3,
        berries = 4,
        key_items = 5
        ),
    Embed(IfThenElse("x", lambda ctx: ctx.pocket != 'pokeballs', 
        Enum(Byte("overworld_usage"),
            mail = 0,
            usable = 1,
            usable_somewhere = 2,
            pokeblock_case = 3,
            unusable = 4
            ),
        Byte("pokeball_number"))),
    ULInt32("p_field_code"),
    Enum(ULInt32("battle_usage"),
        unusable = 0,
        subscreen = 1,
        battle = 2
        ),
    ULInt32("p_battle_code"),
    ULInt32("extra"),
)

PersonEvent = Struct("personevent",
    Byte("number"),
    Byte("sprite"),
    Byte("u1"),
    Byte("u2"),
    ULInt16("xpos"),
    ULInt16("ypos"),
    Byte("u3"),
    Byte("movement_type"),
    Byte("movement"),
    Byte("u4"),
    Byte("is_trainer"),
    Byte("u5"),
    ULInt16("line_of_sight"),
    ULInt32("p_script"),
    ULInt16("id"),
    ULInt16("u6"),
)

WarpEvent = Struct("warpevent",
    ULInt16("xpos"),
    ULInt16("ypos"),
    Byte("kind"),
    Byte("dest_warp"),
    Byte("dest_bank"),
    Byte("dest_map"),
)

'''Enum(Byte("kind"),
        invalid = 0,
        fade = 1,
        stairsup = 2,
        stairsdown = 3,
        stairsupleft = 4,
        stairsdownright = 5,
        doorinside = 6,
        dooroutside = 7,
        caveinside = 8,
        caveoutside = 9,
        caveinsideright = 10,
        caveladderup = 12,
        caveladderdown = 13,
        hole = 14,
        holetarget = 15,
        _default_ = Pass),'''

TriggerEvent = Struct("triggerevent",
    ULInt16("xpos"),
    ULInt16("ypos"),
    Byte("height"),
    Byte("u0"),
    ULInt16("variable"),
    ULInt16("value"),
    ULInt16("u1"),
    ULInt32("script"),
)

SignEvent = Struct("signevent",
    ULInt16("xpos"),
    ULInt16("ypos"),
    Byte("height"),
    Byte("type"),
    ULInt16("u0"),
    IfThenElse("data", lambda ctx: ctx.type in (5, 6, 7),
        Struct("hidden_item",
            ULInt16("item"),
            Byte("id"), 
            Byte("amount")), # Doesn't seem to fit?
        ULInt32("script"))
)

EventSet = Struct("event_set",
    Byte("num_people"),
    Byte("num_warps"),
    Byte("num_triggers"),
    Byte("num_signs"),
    ULInt32("p_people"),
    ULInt32("p_warps"),
    ULInt32("p_triggers"),
    ULInt32("p_signs"),
    Pointer(lambda ctx: ctx.p_people-0x8000000,
        Array(lambda ctx: ctx.num_people, PersonEvent)),
    Pointer(lambda ctx: ctx.p_warps-0x8000000,
        Array(lambda ctx: ctx.num_warps, WarpEvent)),
    Pointer(lambda ctx: ctx.p_triggers-0x8000000,
        Array(lambda ctx: ctx.num_triggers, TriggerEvent)),
    Pointer(lambda ctx: ctx.p_signs-0x8000000,
        Array(lambda ctx: ctx.num_signs, SignEvent)),
)

MapHeader = Struct("map_header",
    ULInt32("p_map"),
    ULInt32("p_event_set"),
    ULInt32("p_scripts"),
    ULInt32("p_connections"),
    ULInt16("music"),
    ULInt16("map_pointer_index"),
    Byte("name"),
    Byte("cave"),
    Byte("weather"), # TODO enum
    Byte("permissions"), # TODO fly, teleport etc.
    Byte("u1"),
    Byte("u2"),
    Byte("display_name"),
    Byte("battle_type"),
    Pointer(lambda ctx: ctx.p_event_set-0x8000000, EventSet),
)

MapBank = Struct("map_bank",
    Array(lambda ctx: mapcounts[ctx.bank_num],
        Struct("headers", ULInt32("p_header"),
        Embed(Pointer(lambda ctx: ctx.p_header-0x8000000, MapHeader))))
)

def inc_bank(ctx):
    ctx._.banks += 1
    return ctx._.banks-1

MapBankTable = Struct("map_bank_table",
    Value('banks', lambda ctx: 0), # A hack.
    Array(len(mapcounts),
        Struct("banks", Value('bank_num', inc_bank), ULInt32("p_bank"),
        Embed(Pointer(lambda ctx: ctx.p_bank-0x8000000, MapBank))))
)

ROM = Struct("rom",
    #Pointer(lambda ctx: 0x3e7010,
    #    Array(lambda ctx:79, PokemonStringAdapter(CString('map_name', terminators="\xff")))),
    Pointer(lambda ctx:0x3C5580,
        GreedyRange(Item)
    ),
    Pointer(lambda ctx:0x3e73e0,
        GreedyRange(Struct('map_name',
            ULInt32("unk"),
            ULInt32("p_map_name"),
            Pointer(lambda ctx: ctx.p_map_name-0x8000000, PokemonStringAdapter(CString('map_name', terminators="\xff")))))),
            
    Pointer(lambda ctx: 0x3085A0, #0x307f78, #0x308588, 0x3085A0
        MapBankTable)
)

def cap(name): return name.replace('\n','').replace('  ',' ').title()
def identifier(name): return cap(name).replace(' ', '-').replace('.','').lower()

def main(rom):
    f = open(rom, "rb")
    rom = f.read()
    
    p = ROM.parse(rom)
    #print(p.item)
    if mode == "print":
        for bank in p.map_bank_table.banks:
            print("Bank {0}, has {1} maps".format(bank.bank_num, len(bank.headers)))
            for i, map in enumerate(bank.headers):
                print(" {0}.{1} {2}: {3} people".format(bank.bank_num, i, identifier(p.map_name[map.name].map_name), map.event_set.num_people))
                for person in map.event_set.personevent:
                    if person.sprite == 59:
                        item, amount = parse_script_for_item(f, person.p_script-0x8000000)
                        if item != None:
                            print("  [{0}, {1}]\t{2} ×{3}".format(person.xpos, person.ypos, identifier(p.item[item].name), amount))
                    else:
                        item, amount = parse_script_for_item(f, person.p_script-0x8000000, brute_force=True)
                        if item != None and item in range(len(p.item)):
                            print("  [{0}, {1}]\t{2} ×{3} (from npc)".format(person.xpos, person.ypos, identifier(p.item[item].name), amount))
                for sign in map.event_set.signevent:
                    if sign.type in (5, 6, 7):
                        print("  [{0}, {1}]\t{2} (hidden)".format(sign.xpos, sign.ypos, identifier(p.item[sign.data.item].name)))
    
    f.close()

if __name__ == "__main__":
    from sys import argv
    main(argv[1])
