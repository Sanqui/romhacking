# encoding: utf-8
from construct import *

''' Sources:
http://furlocks-forest.net/wiki/?page=Pokemon_GBA_Save_Format
http://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_data_structure_in_the_GBA

'''

def LittleEndianBitStruct(*args):
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
    0xFC: '=2',
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
        

PokemonGrowth = Struct("growth",
    ULInt16 ("species"),
    ULInt16 ("item"),
    ULInt32 ("experience"),
    BitStruct("move_ppup",
        BitField("4", 2),
        BitField("3", 2),
        BitField("2", 2),
        BitField("1", 2)
    ),
    Byte    ("happiness"),
    ULInt16 ("unk1"),
)

PokemonMoves = Struct("moves",
    Sequence("moves",
        ULInt16 ("move1"),
        ULInt16 ("move2"),
        ULInt16 ("move3"),
        ULInt16 ("move4")
    ),
    Sequence("move_pp",
        Byte ("move1"),
        Byte ("move2"),
        Byte ("move3"),
        Byte ("move4")
    )
)
PokemonEffort = Struct("effort",
    Struct("ev",
        Byte("hp"),
        Byte("attack"),
        Byte("defense"),
        Byte("speed"),
        Byte("spattack"),
        Byte("spdefense")
    ),
    Struct("contest",
        Byte("coolness"),
        Byte("beauty"),
        Byte("cuteness"),
        Byte("smartness"),
        Byte("toughness"),
        Byte("feel")
    )
)

PokemonMisc = Struct("misc",
    LittleEndianBitStruct("pokerus",
        Nibble("immunity"),
        Nibble("time")
    ),
    Struct("catch",
        Byte    ("location"),
        Embed(LittleEndianBitStruct("level",
            Flag ("egg"),
            BitField("level", 7)
        )),
        Embed(LittleEndianBitStruct("pokeball_otgender",
            Flag("otgender"),
            Padding(1),
            Nibble("ball"),
            Padding(2)
        ))
    ),
    LittleEndianBitStruct("iv",
        Padding(2),
        BitField("spdefense", 5),
        BitField("spattack", 5),
        BitField("speed", 5),
        BitField("defense", 5),
        BitField("attack", 5),
        BitField("hp", 5)
    ),
    LittleEndianBitStruct('ribbons',
        Flag("alldifs"),
        Flag("unk5"),
        Flag("unk4"),
        Flag("unk3"), #20
        Flag("effort"),
        Flag("artist"),
        Flag("unk2"),
        Flag("unk1"),
        Flag("champion"),
        BitField("toughrank", 3),
        BitField("smartrank", 3),
        BitField("cuterank", 3),
        BitField("beautyrank", 3),
        BitField("coolrank", 3),
    ),
    Byte('unknown'),
)

class PokemonDataAdapter(Adapter):
    orders = ["GAEM", "GAME", "GEAM", "GEMA", "GMAE", "GMEA", "AGEM", "AGME", "AEGM", "AEMG", "AMGE", "AMEG ", "EGAM", "EGMA", "EAGM", "EAMG", "EMGA", "EMAG ", "MGAE", "MGEA", "MAGE", "MAEG", "MEGA", "MEAG"]
    def _encode(self, obj, context):
        return None # TODO
    def _decode(self, obj, c):
        checksum = ULInt16("checksum").parse(obj)
        # 2 byte padding
        data = b""
        cryptxor = c.ot_id ^ c.personality
        for integer in StrictRepeater(48//4, ULInt32('i')).parse(obj[4:]):
            data += ULInt32('i').build(integer ^ cryptxor)
        ss = []
        for s in self.orders[c.personality % 24]:
            if s == "G": ss.append(PokemonGrowth)
            elif s=="A": ss.append(PokemonMoves)
            elif s=="E": ss.append(PokemonEffort)
            elif s=="M": ss.append(PokemonMisc)
        datastruct = Struct("data", *ss)
        # TODO validate checksum
        return datastruct.parse(data)

Pokemon = Struct("pokemon",
    ULInt32 ("personality"),
    #Struct("personality_values",
    #    Value("gender", lambda c: Struct('gender', Padding(3), Byte('gender').parse(c._.personality)))
    #),
    ULInt32 ("ot_id"),
    PokemonStringAdapter(String  ("nickname", 10)),
    Enum    (ULInt16("language"),
        jp=   0x0201,
        us=   0x0202,
        fr=   0x0203,
        it=   0x0204,
        de=   0x0205,
        es=   0x0206,
        _default_=  Pass),
    PokemonStringAdapter(String  ("ot_name", 7)),
    BitStruct('markings',
        Padding(4),
        Flag('heart'),
        Flag('square'),
        Flag('triangle'),
        Flag('circle')
    ),
    
    PokemonDataAdapter(Bytes("data", 2+2+48))
)
PartyPokemon = Struct("partypokemon",
    Embed(Pokemon),
    Struct("situational",
        LittleEndianBitStruct('staus',
            Padding(24),
            BitField('sleep', 3),
            Flag("poison"),
            Flag("burn"),
            Flag("freeze"),
            Flag("paralysis"),
            Flag("toxic")
        ),#ULInt32 ('status'),
        Byte ('level'),
        Byte ('pokerusleft'),
        ULInt16 ('curhp'),
        ULInt16 ('hp'),
        ULInt16 ('attack'),
        ULInt16 ('defense'),
        ULInt16 ('speed'),
        ULInt16 ('spattack'),
        ULInt16 ('spdefense')
    )
)
# Save 

class PokemonAdapter(Adapter):
    def _encode(self, obj, context):
        return None # TODO
    def _decode(self, obj, c):
        if obj.personality == 0 and obj.ot_id == 0: # XXX dirty
            return None
        else:
            return obj 


SaveStruct = Struct("save",
    PokemonStringAdapter(String("trainer_name", 7)),
    Padding(1),
    Flag("female"),
    ULInt32("trainer_id"),
    Pointer(lambda ctx: 0x0028,
        Struct("pokedex", 
            LittleEndianBitStruct('owned',
                Padding(6), *tuple(Flag(str(386-i)) for i in range(386))
            ),
            LittleEndianBitStruct('seen',
                Padding(6), *tuple(Flag(str(386-i)) for i in range(386))
            )
        )
    ),
    # Pointer(lambda ctx: 0x00a8, # Battle tower
    # Pointer(lambda ctx: 0x0498, # Mossdeep
    Pointer(lambda ctx: 0x0f80,
        Struct("map",
            ULInt16("x"),
            ULInt16("y"),
            ULInt32("address"),
            # map data
        )
    ),
    Pointer(lambda ctx: 0x11b4,
        Struct("pokemon_party",
            Byte("count"),
            Padding(3),
            MetaRepeater(lambda ctx: ctx.count,
                PartyPokemon
            )
        )
    ),
    Struct("currencies",
        Pointer(lambda ctx: 0x1410,
            Embed(Struct("money",
                ULInt32("money"),
                ULInt16("coins")
            ))
        ),
        Pointer(lambda ctx: 0x2350, ULInt16("ash")),
    ),
    # Pointer(lambda ctx: 0x1418, # Inventory
    # Pointer(lambda ctx: 0x1778, # Pokéblocks
    #Pointer(lambda ctx: 0x2590, # Soil
    #    Struct("soil",
    #        Byte("berry_id"),
    #        BitStruct("state",
    #            BitField("phase", 3),
    #            Padding(4),
    #            Flag("initial")
    #        ),
    #        ULInt16("phase_minutes_left"),
    #        Byte("berries"),
    #        Embed(BitStruct("water",
    #            Struct("phaseswatered",
    #                Flag("1"),
    #                Flag("2"),
    #                Flag("3"),
    #                Flag("4"),
    #            ),
    #            Nibble("timesregrown")
    #        )),
    #        Padding(2)
    #    )
    # ),
    # Pointer(lambda ctx: 0x2988, # Secret base
    # Pointer(lambda ctx: 0x277c, # Television
    # Pointer(lambda ctx: 0x3d7c, # Contest winners
    Pointer(lambda ctx: 0x3f1c,
        Sequence("daycare",
            PokemonAdapter(Pokemon), PokemonAdapter(Pokemon)
        )
    ),
    Pointer(lambda ctx: 0x4038,
        Struct("link_battle",
            PokemonStringAdapter(String("name", 7)),
            Padding(1),
            ULInt16("unk"), # unknown
            ULInt16("wins"),
            ULInt16("loses"),
            ULInt16("draws")
        )
    ),
    # Pointer(lambda ctx: 0x4610, # Mystery Event
    Struct("storage",
        Pointer(lambda ctx: 0x4d80,
            Embed(Struct('boxes',
                Byte("selected_box"),
                Padding(3),
                StrictRepeater(14, Sequence('box',
                    StrictRepeater(30, PokemonAdapter(Pokemon))
                    )
                )
            ))
        ),
        Pointer(lambda ctx: 0xd0c4,
            Sequence("names",
                StrictRepeater(14, PokemonStringAdapter(String("boxnamename", 9)))
            )
        ),
        Pointer(lambda ctx: 0xd142,
            Sequence("wallpapers",
                StrictRepeater(14, Byte('wp'))
            )
        ),
    )
)

# Meta-save

SaveBlock = Struct("saveblock",
    Bytes   ("data", 0x1000-0xc),
    Byte    ("block_id"),
    Byte    ("unk"),
    ULInt16 ("checksum"),
    #ULInt16("validation"),
    Const(ULInt32("validation"), 0x08012025),
    ULInt32 ("saveid")
)

if __name__ == "__main__":
    from sys import argv
    f = open(argv[1], "rb")
    s = f.read()
    f.close()

    #print(s[0:7255])

    saves = {}

    for block in GreedyRepeater(Bytes('block', 0x1000)).parse(s):
        try:
            block = SaveBlock.parse(block)
            if block.saveid not in saves:
                saves[block.saveid] = dict()
            saves[block.saveid][block.block_id] = block.data
        except adapters.ConstError:
            pass
    for save_id, blocks in saves.iteritems():
        save = b""
        for i in range(len(blocks)):
            save += blocks[i][0:3968]
            #print(len(save), len(blocks))
        saves[save_id] = save

    #print(repr(saves[1][0x0f80:0x0f80+0x80]))
    #print(len(saves[1]))
    print(SaveStruct.parse(saves[max(saves)]))
