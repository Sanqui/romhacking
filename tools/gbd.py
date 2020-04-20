#!/usr/bin/python3
import struct
from sys import argv, stderr
from gbaddr import gbaddr, gbswitch

def readbyte():  return struct.unpack("B",  rom.read(1))[0]
def readshort(): return struct.unpack("<H", rom.read(2))[0]

rom = open(argv[1], "rb")
# TODO load symfile

address = gbaddr(argv[2])
if not isinstance(address, int):
    exit("Failed to convert address.  Please check your ranges.")
address_bank = address // 0x4000
format = argv[3]
count = eval(argv[4])
label = None
if len(argv) > 5:
    try:
        label = int(argv[5])
    except ValueError:
        label = argv[5]

rom.seek(address)
values = []

data_format = format.lstrip("ds")
if data_format == "w":
    for i in range(count):
        values.append(readshort())
elif data_format == "wb":
    for i in range(count):
        values.append((readshort(), readbyte()))
elif data_format == "bw":
    for i in range(count):
        values.append((readbyte(), readshort()))
elif data_format == "b":
    for i in range(count):
        values.append(readbyte())
else:
    stderr.write(f"Unknown format {format}\n")

if type(label) == int and data_format == "b":
    comma = ", "
    if label > 8:
        comma = ","
    lines = []
    line = []
    for i, value in enumerate(values):
        line.append(value)
        if len(line) >= label:
            lines.append(line)
            line = []
    if line:
        lines.append(line)
    for line in lines:
        print(f"    db " + comma.join(f"${x:02x}" for x in line))
else:
    for i, value in enumerate(values):
        if format == "dw":
            value_string = f"${value:04x}"
            if label:
                value_string = f"{label}{i:X} ; {value_string}"
            line = f"    dw {value_string}"
        elif format == "dwb":
            a, b = value
            value_string = f"${a:04x}, ${b:02x}"
            if label:
                #value_string = f"{label}{i:X}, BANK({label}{i:X}) ; {value_string}"
                line = f"    pwb {label}{i:x} ; {b:02x}:{a:04x}"
            else:
                line = f"    dwb {value_string}"
        elif format == "swb":
            a, b = value
            line = f"{b:02x}:{a:04x} {label}{i:x}"
        elif format == "sbw":
            b, a = value
            line = f"{b:02x}:{a:04x} {label}{i:x}"
        elif format == "sw":
            a = value
            line = f"{address_bank:02x}:{a:04x} {label}{i:x}"
        else:
            line = hex(value)
        
        print(line)

print(f"; {gbswitch(rom.tell())}")
