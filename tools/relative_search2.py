#!/bin/pypy

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

from sys import argv


text = argv[1]
file = open(argv[2], 'rb')

test_strings = []
for n in range(255):
    test_strings.append( "".join(chr((alphabet.find(char.upper())+n)%256) for char in text))

data = file.read()

print argv[2], hex(len(data))

for i in range(len(data)-len(text)):
    testing_against = data[i:i+len(text)]
    for n, test_string in enumerate(test_strings):
        if testing_against == test_string:
            print "Found at", i, "offset by", n, "as", test_string
