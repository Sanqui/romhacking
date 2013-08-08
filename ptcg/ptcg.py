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
    Byte('type'),
    Short('gfx_pointer'),
    TextPtrAdapter(Short('name')),
    Byte('rarity'),
    Byte('set'),
    Byte('unk1'),
    Byte('hp'),
    Byte('stage'),
    Short('preevo_name_id'),
    If(lambda ctx: ctx.type==1,
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
                        Byte('damage'),
                        Padding(10)
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
        #print hex(ULInt24('pointer!!!!').parse(ptr))
        rom.seek(0x34000 + ULInt24('pointer!!!!').parse(ptr))
        #print rom.read(50)
        #try:
        text = CString('text').parse(rom.read(0x1000))
        #    print i, text[1:]
        #except construct.core.ArrayError:
        #    pass
        texts.append(text)
    
    #exit()

    rom.seek(0x30c5e)
    for i in range(228):
        rom.seek(0x30c5e+(i*2))
        ptr = rom.read(2)
        rom.seek(0x30000 + Short('pointer!!!!').parse(ptr)%0x4000)
        card = Card.parse(rom.read(0xff))
        
        print card
