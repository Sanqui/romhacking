# encoding: utf-8
import csv
from collections import defaultdict
from construct import *

def LBitStruct(*args):
    """Construct's bit structs read a byte at a time in the order they appear,
    reading each bit from most to least significant.  Alas, this doesn't work
    at all for a 32-bit bit field, because the bytes are 'backwards' in
    little-endian files.

    So this acts as a bit struct, but reverses the order of bytes before
    reading/writing, so ALL the bits are read from most to least significant.
    
    Shamelessly stolen from Eevee's Gen IV PKM parser.
    """
    return Buffered(
        BitStruct(*args),
        encoder=lambda s: s[::-1],
        decoder=lambda s: s[::-1],
        resizer=lambda _: _,
    )

mode = "print"
#if mode == "import":
#    from pokedex.db import connect, tables, util

# Amounts of maps in each bank.  As far as I know, this information doesn't
# exist in the rom, so I stole it shamelessly from Advancemap.
mapcounts = [54, 5, 5, 6, 7, 7, 8, 7, 7, 13, 8, 17, 10, 24, 13, 13, 14, 2, 2,
             2, 3, 1, 1, 1, 86, 44, 12, 2, 1, 13, 1, 1, 3]

class Instance(): pass
# TODO make these namedtuples
class ItemInstance(Instance):
    verb = "gotten"
    def __init__(self, mem):
        self.item = mem[0x8000]
        self.amount = mem[0x8001]
    
    def __str__(self):
        if self.item in range(len(p.item)):
            return "Item {0} ×{1} ({2})".format(identifier(p.item[self.item].name), self.amount, self.verb)
        else:
            return "Item variable ({0})".format(self.verb)

class ObtainItemInstance(ItemInstance):
    verb = 'obtained'

class FindItemInstance(ItemInstance):
    verb = 'found'

class TrainerBattleInstance(Instance):
    def __init__(self, type, id):
        self.type = type
        self.id = id
    
    def __str__(self):
        return "Trainer({3}) {0} {1} [{2}]".format(p.trainer_class_name[p.trainer[self.id].trainer_class], p.trainer[self.id].name, ", ".join("{0} lv. {1}".format(identifier(p.pokemon_name[pokemon.species]), pokemon.level) for pokemon in p.trainer[self.id].party_pokemon), self.type)

class WildBattleInstance(Instance):
    def __init__(self, pokemon, level, item):
        self.pokemon, self.level, self.item = pokemon, level, item
    
    def __str__(self):
        return "Wild Pokémon {0} lv. {1} {2}".format(identifier(p.pokemon_name[self.pokemon]), self.level, (" holding "+identifier(p.item[self.item].name) if self.item else ""))

class MartInstance(Instance):
    def __init__(self, code, items, addr):
        self.code, self.items, self.addr = code, items, addr
    
    def __str__(self):
        return "Mart({0}) @{2} [{1}]".format(self.code, ", ".join(identifier(p.item[item].name) for item in self.items), hex(self.addr))

class GivenPokemonInstance(Instance):
    def __init__(self, pokemon, level=None, item=None):
        self.pokemon, self.level, self.item = pokemon, level, item
    
    def __str__(self):
        return "Given Pokémon {0} {1} {2}".format(identifier(p.pokemon_name[self.pokemon]), "lv. "+str(self.level) if self.level else "(egg)", (" holding "+identifier(p.item[self.item].name) if self.item else ""))

class EndScript(): pass

codes = {}
params = {'byte': Byte, 'hword': ULInt16, 'word': ULInt32, '(byte)': Byte} # XXX
with open('scriptcodes.csv') as f:
    csv = csv.reader(f, delimiter=';')
    for row in csv:
        c = int(row[0], 16)
        name = row[1]
        pms = tuple(params[param](str(i)) for i, param in enumerate(row[2:]) if param)
        codes[c] = Sequence(name, *pms)
        #print hex(c), name, p

codes[0x5c] = Sequence('trainerbattle', # Hardcoded due to variability
    Byte('type'), 
    ULInt16('id'),
    ULInt16('0'),
    If(lambda ctx: ctx.type not in (3,),
        ULInt32('text')),
    ULInt32('textafter'),
    If(lambda ctx: ctx.type in (4, 7, 8),
        ULInt32('textonlyonepkmn')),
    If(lambda ctx: ctx.type in (1, 2, 8),
        ULInt32('p_cont'))
    )

parsed_scripts = {}

#TODO: Print debug statements if told to!
def parse_script(rom, loc, brute_force=False):
    stuff = []
    gotolocs = []
    def readbyte(): return ord(rom.read(1))
    if loc in parsed_scripts.keys():
        #print(" --- Script at {0} parsed before ---".format(hex(loc)))
        return parsed_scripts[loc]
    #def readshort(): return readbyte() + (readbyte() << 8)
    #def readint(): return readbyte() + (readbyte() << 8) + (readbyte() << 16) + (readbyte() << 24)
    try: rom.seek(loc)
    except IOError:
        #print ('faill!!!')
        return []
    mem = defaultdict(lambda: 0)
    #print (" --- SCRIPT AT {0} ---".format(hex(loc)))
    while True:
        if EndScript in stuff:
            parsed_scripts[loc] = stuff
            return stuff
        c = readbyte()
        if c not in codes.keys():
            #print(" ! UNKNOWN CODE: {0} !".format(hex(c)))
            stuff.append(EndScript)
            return stuff
        code = codes[c]
        cmd = code.parse_stream(rom)
        #print code.name, " ".join(hex(a) for a in cmd if a)
        if code.name == 'end':
            stuff.append(EndScript)
        elif code.name == 'return':
            parsed_scripts[loc] = stuff
            return stuff
        elif code.name == 'call':
            loc = rom.tell()
            stuff += parse_script(rom, cmd[0]-0x8000000)
            rom.seek(loc)
        elif code.name == 'goto':
            if cmd[0] in gotolocs:
                #print(" ! Infinite script loop detected, aborting ! ")
                stuff.append(EndScript)
            else:
                gotolocs.append(cmd[0])
                try:
                    rom.seek(cmd[0]-0x8000000)
                except IOError: stuff.append(EndScript)
        elif code.name == 'jumpstd':
            # Oops, we dunno builtins...
            stuff.append(EndScript)
        elif code.name == 'killscript':
            stuff.append(EndScript)
        elif code.name == 'copyvarifnotzero':
            mem[cmd[0]] = cmd[1]
        elif code.name == 'callstd':
            func = cmd[0]
            if func == 0: stuff.append(ObtainItemInstance(mem))
            elif func == 1: stuff.append(FindItemInstance(mem))
        elif code.name == 'trainerbattle':
            stuff.append(TrainerBattleInstance(cmd[0], cmd[1]-1)) # XXX why -1?, also two more args
            if cmd[6]:
                loc = rom.tell()
                stuff += parse_script(rom, cmd[0]-0x8000000)
                rom.seek(loc)
        elif code.name == 'startwildbattle':
            stuff.append(WildBattleInstance(cmd[0], cmd[1], 0))#, cmd[2]))
        elif code.name in ('pokemart',):# 'pokemart2', 'pokemart3'):
            loc = rom.tell()
            rom.seek(cmd[0]-0x8000000)
            items = filter(None, RepeatUntil(lambda obj, ctx: obj == 0, ULInt16('item')).parse_stream(rom))
            rom.seek(loc)
            stuff.append(MartInstance(code.name, items, cmd[0]))
        elif code.name == 'givepokemon':
            stuff.append(GivenPokemonInstance(cmd[0], cmd[1], cmd[2]))
        elif code.name == 'giveegg':
            stuff.append(GivenPokemonInstance(cmd[0]))


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
    0xB5: '♂',
    0xB6: '♀',
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

PartyPokemon = Struct("party_pokemon",
    ULInt16("ai"),
    ULInt16("level"),
    ULInt16("species"),
    If(lambda ctx: ctx._.party_type in (0, 2),
        ULInt16("item")),
    If(lambda ctx: ctx._.party_type == 1,
        Embed(Struct('moves',
            Array(4, ULInt16("move")),
            Padding(2)))),
    If(lambda ctx: ctx._.party_type == 3,
        Embed(Struct('item_and_moves',
            ULInt16("item"),
            Array(4, ULInt16("move")))))
)

Trainer = Struct("trainer",
    Byte("party_type"),
    Byte("trainer_class"),
    Embed(LBitStruct("gender_and_music",
        Bit('gender'),
        BitField('music', 7)
        )),
    Byte("sprite"),
    PokemonStringAdapter(String('name', 12)),
    Array(4, ULInt16("item")),
    Byte("is_double"),
    Padding(3),
    ULInt16("u2"),
    Padding(2),
    ULInt16("party_size"),
    Padding(2),
    ULInt32("p_party"),
    Pointer(lambda ctx: ctx.p_party-0x8000000,
            Array(lambda ctx: ctx.party_size, PartyPokemon)),
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
    ULInt32("p_script"),
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
        ULInt32("p_script"))
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
    Pointer(lambda ctx:0x1f053c,
        GreedyRange(Trainer)),
    Pointer(lambda ctx:0x1f7184,
        Array(412, PokemonStringAdapter(String('pokemon_name', 11)))),
    Pointer(lambda ctx:0x1f0220,
        Array(60, PokemonStringAdapter(String('trainer_class_name', 13)))),
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
    global p
    p = ROM.parse(rom)
    #print( p.trainer)
    if mode == "print":
        for bank in p.map_bank_table.banks:
            print("Bank {0}, has {1} maps".format(bank.bank_num, len(bank.headers)))
            for i, map in enumerate(bank.headers):
                print(" {0}.{1} {2}: {3} people".format(bank.bank_num, i, identifier(p.map_name[map.name].map_name), map.event_set.num_people))
                for person in map.event_set.personevent:
                    stuff = parse_script(f, person.p_script-0x8000000)
                    for thing in stuff:
                        if isinstance(thing, Instance):
                            print "  [{0}, {1}]\t".format(person.xpos, person.ypos), str(thing)
                for trigger in map.event_set.triggerevent:
                    stuff = parse_script(f, trigger.p_script-0x8000000)
                    for thing in stuff:
                        if isinstance(thing, Instance):
                            print "  [{0}, {1}]T\t".format(trigger.xpos, trigger.ypos), str(thing)
                for sign in map.event_set.signevent:
                    if sign.type in (5, 6, 7):
                        print "  [{0}, {1}]H\t{2} (hidden)".format(sign.xpos, sign.ypos, identifier(p.item[sign.data.item].name))
                    else:
                        stuff = parse_script(f, sign.data-0x8000000)
                        for thing in stuff:
                            if isinstance(thing, Instance):
                                print "  [{0}, {1}]S\t".format(trigger.xpos, trigger.ypos), str(thing)
    f.close()

if __name__ == "__main__":
    from sys import argv
    main(argv[1])
