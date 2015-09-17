#!/usr/bin/python3

CARDS = """Hesper Starkey
Paracelsus
Archibald Alderton
Elladora Ketteridge
Gaspard Shingleton
Glover Hipworth
Gregory the Smarmy
Laverne DeMontmorency
Ignatia Wildsmith
Sacharissa Tugwood
Glanmore Peakes
Balfour Blane
Felix Summerbee
Greta Catchlove
Honouria Nutcombe
Gifford Ollerton
Jocunda Sykes
Quong Po
Dorcas Wellbeloved
Merwyn the Malicious
Morgan le Fay
Crispin Cronk
Ethelred the EverReady
Beatrix Bloxam
Alberta Toothill
Xavier Rastrick
Yardley Platt
Dymphna Furmage
Fulbert the Fearful
Wendelin the Weird
Tilly Toke
Carlotta Pinkstone
Edgar Stroulger
Havelock Sweeting
Flavius Belby
Justus Pilliwickle
Norvel Twonk
Oswald Beamish
Cornelius Agrippa
Gulliver Pokeby
Newt Scamander
Glenda Chittock
Adalbert Waffling
Perpetua Fancourt
Cassandra Vablatsky
Mopsus
Blenheim Stalk
Alberic Grunnion
Merlin
Elfrida Clagg
Grogan Stump
Burdock Muldoon
Almerick Sawbridge
Artemisia Lufkin
Gondoline Oliphant
Montague Knightley
Harry Potter
Derwent Shimpling
Gunhilda of Gorsemoor
Cliodne
Beaumont Marjoribanks
Chauncey Oldridge
Mungo Bonham
Wilfred Elphick
Bridget Wenlock
Godric Gryffindor
Miranda Goshawk
Salazar Slytherin
Queen Maeve
Helga Hufflepuff
Rowena Ravenclaw
Hengist of Woodcroft
Daisy Dodderidge
Albus Dumbledore
Donaghan Tremlett
Musidora Barkwith
Gideon Crumb
Herman Wintringham
Kirley Duke
Myron Wagtail
Orsino Thruston
Celestina Warbeck
Heathcote Barbary
Merton Graves
Bowman Wright
Joscelind Wadcock
Gwenog Jones
Cyprian Youdle
Devlin Whitehorn
Dunbar Oglethorpe
Leopoldina Smethwyck
Roderick Plumpton
Roland Kegg
Herpo the Foul
Andros the Invincible
Uric the Oddball
Lord Stoddard Withers
Circe
Mirabella Plunkett
Bertie Bott
Thaddeus Thurkell
Unknown""".split('\n')

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

decks = []
for d in range(4):
    sets = []
    for i in range(3):
        set_ = []
        rom.seek(6*0x4000 + 0x1ad5 + i*2)
        x = readshort()
        rom.seek(x)
        num = readbyte()
        x += 1
        for c in range(num):
            rom.seek(x+c)
            rom.seek(6*0x4000 + 0x1aff + readbyte()*4 + d)
            set_.append(readbyte())
        sets.append(set_)
    decks.append(sets)


for d, sets in enumerate(decks):
    print("When collecting deck {}:".format(d))
    for i, set_ in enumerate(sets):
        print(" Set {} cards:".format(i))
        for c in set_:
            print("  - {}. {}".format(c, CARDS[c]))
        print
    print("---")


