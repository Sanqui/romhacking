'''
#00000000  01 00 00 01 01 d4 ca 6d  9c 46 f2 d8 6b f7 29 49 .......m .F..k.)I
#00000010  31 08 00 45 00 00 35 19  1f 00 00 40 11 0b 73 c0 1..E..5. ...@..s.
#00000020  a8 a0 7e 63 f9 91 06 ec  e9 95 ea 00 21 b1 94    ..~c.... ....!..
#                                                        51                 Q
#00000030  51 05 00 65 00 00 00 00  87 88 00 8e d0 56 01 f4 Q..e.... .....V..
#00000040  70 10 00 00 00 00 00 48                          p......H 


--- RECEIVED ---
<00000000  01 00 00 01 01 d8 6b f7  29 49 31 d4 ca 6d 9c 46 ......k. )I1..m.F
<00000010  f2 08 00 45 00 00 35 f2  9f 00 00 32 11 3f f2 63 ...E..5. ...2.?.c
<00000020  f9 91 06 c0 a8 a0 7e 95  ea ec e9 00 21 f7 3a    ......~. ....!.:
<                                                        51                 Q
<00000030  51 05 00 2c 00 00 00 00  dd 9a 01 e5 d2 56 01 f4 Q..,.... .....V..
<00000040  70 10 00 00 00 00 00 d2                          p....... 
--- END RECEIVED ---


# diff packet header
#00000224  01 00 00 01 01 d4 ca 6d  9c 46 f2 d8 6b f7 29 49 .......m .F..k.)I
#00000234  31 08 00 45 00 01 42 19  44 00 00 40 11 0a 41 c0 1..E..B. D..@..A.
#00000244  a8 a0 7e 63 f9 91 06 ec  e9 95 ea 01 2e c7 1e    ..~c.... ......  
# diff session (battle), first packet
 00000000  01 00 00 01 01 d4 ca 6d  9c 46 f2 d8 6b f7 29 49 .......m .F..k.)I
 00000010  31 08 00 45 00 00 35 42  fe 00 00 40 11 e1 93 c0 1..E..5B ...@....
 00000020  a8 a0 7e 63 f9 91 06 e3  11 96 00 00 21 69 30    ..~c.... ....!i0
                                                         51                 Q
 00000030  51 05 00 ad 00 00 00 00  cb ed 00 e2 b8 59 01 f9 Q....... .....Y..
 00000040  69 1d 00 00 00 00 00 84                          i....... 
'''
ME = 0xc0a8a07e

import sys
from construct import *

Short = UBInt16
Int = UBInt32

XYP2PPacket = Struct("xyp2ppacket",
    #Bytes("magic0", 5),
    Magic("\x01\x00\x00\x01\x01"),
    Int("uniq0"),
    Int("uniq1"),
    Int("uniq2"),
    #Bytes("magic1", 3),
    Magic("\x08\x00\x45"),
    Short("state"),
    Byte("code"),
    Short("unk0"),
    Short("zeroes"),
    Byte("uniq3"),
    Byte("magic2"),
    #Bytes("11", 5),
    #Magic("\x11"),
    Byte("unk1"),
    Byte("unk2"),
    Int("from"),
    Int("to"),
    Int("transaction"),
    Short("length"), # body length + 8
    Short("checksum"),
    )

codes = {53: "handshake", 85: "handshake2", 101: "handshake3", 66: "conninfo_client", 106: "conninfo_host"}

f = open(sys.argv[1])
i = 0
for i in range(400):
    bytes = f.read(0x2f)
    header = XYP2PPacket.parse(bytes)
    length = header.length - 8
    #print "header:"
    #print(header)
    name = "?"
    if header.code in codes:
        name = codes[header.code]
    print "{}packet - from {:08x}, to {:08x}, via {:08x}, packet code {:03} (0x{:02x}, {}), {:03x} bytes".format(">>" if header['from'] == ME else "<<", header['from'], header.to, header.transaction, header.code, header.code, name, length)
    #print "packet body:"
    body0 = f.read(length)
    body1 = f.read(length)
    print "  "+body0.encode('hex')
    #print "  "+body1.encode('hex')
    #if name in "conninfo ".split():
    print "  ascii in body: "+"".join(x for x in body0 if ord(x) in range(0x20, 0x7f)) 
    assert body0 == body1
    #print body0
