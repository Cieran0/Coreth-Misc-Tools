#!/usr/bin/python3
import sys

def padded_hex(x):
    hx = hex(ord(x))[2:]
    if(len(hx) == 2):
        return hx
    else:
        return "0" + hx

string = sys.argv[1].replace("\\n",'\n')
if(len(string)%8 != 0):
    string += '\0'*(8 - len(string)%8)
print(string)
chunks = len(string)//8
print(chunks)
splt = [ string[i*8:i*8+8] for i in range(0, chunks) ]
print(splt)
for s in splt:
    temp = ""
    for x in s:
        temp = padded_hex(x) + temp
    print("0x" + temp)