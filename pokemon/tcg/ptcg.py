import construct.core
from construct import *

texts = []

Short = ULInt16

class TextPtrAdapter(Adapter):
    def _encode(self, obj, context):
        return None # TODO
    def _decode(self, obj, c):
        return texts[obj].lstrip('\x06')
    

Card = Struct("card",
    Enum(Byte('type'),
        fire_energy=8,
        grass_energy=9,
        lightning_energy=10,
        water_energy=11,
        fighting_energy=12,
        psychic_energy=13,
        double_colorless_enegry=14,
        pokemon0=0,
        pokemon1=1,
        pokemon2=2,
        pokemon3=3,
        pokemon4=4,
        pokemon5=5,
        pokemon6=6,
        trainer=16,
        ),
    Short('gfx_pointer'),
    TextPtrAdapter(Short('name')),
    Byte('rarity'),
    Byte('set'),
    Byte('unk1'),
    Byte('hp'),
    Byte('stage'),
    Short('preevo_name_id'),
    If(lambda ctx: ctx.type.startswith('pokemon'),
        Struct('pokemon_data', 
            Struct('moves',
                Array(2,
                    Struct('move',
                        BitStruct('energies',
                            Array(8, Nibble('energy')
                            )
                        ),
                        TextPtrAdapter(Short('name')),
                        TextPtrAdapter(Short('desc')),
                        Byte('unk-1'),
                        Byte('unk0'),
                        Byte('damage'),
                        Byte('unk2'),
                        Byte('unk3'),
                        Byte('unk4'),
                        Byte('unk5'),
                        Byte('unk6'),
                        Byte('unk7'),
                        Byte('unk8'),
                        Byte('unk9'),
                    ),
                ),
            ),
            Byte('retreat'),
            Byte('weakness'),
            Byte('resistance'),
            Short('kind_id'),
            Byte('number'),
            Byte('unk2'),
            Byte('level'),
            Short('length'),
            Short('weight'),
            TextPtrAdapter(Short('desc')),
        )
    )
)

with open('ptcg.gbc') as rom:
    # First, let's rip texts!
    
    rom.seek(0x34000)
    for i in range(2990):
        rom.seek(0x34000+(i*3))
        ptr = rom.read(3)
        rom.seek(0x34000 + ULInt24('ptr').parse(ptr))
        text = CString('text').parse(rom.read(0x1000))
        texts.append(text)
    
    #exit()

    rom.seek(0x30c5e)
    for i in range(228):
        rom.seek(0x30c5e+(i*2))
        ptr = rom.read(2)
        rom.seek(0x30000 + Short('ptr').parse(ptr)%0x4000)
        card = Card.parse(rom.read(0xff))
        
        print card
