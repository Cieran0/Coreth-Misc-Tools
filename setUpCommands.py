#!/usr/bin/python3
instructs = []
params = []
paramSize =[]
lines = []
fCalls = []

def readCommands():
    f = open("Coreth-Misc-Tools/RawInstructions.hpp","r")
    lines = f.readlines()[3:]
    for line in lines:
        instructs.append(line.split(' ')[1])
        params.append((line.split('(')[1])[:-3])
    f.close()
    return lines

def writeCommandsAndSwitch():
    lines = readCommands()
    f = open("CVM/include/commands.h","w")
    f.write('#pragma once\n')
    f.write('#include "cvm.h"\n')
    for line in lines:
        f.write(line)
    f.close()
    f = open("CVM/main.cpp","r")
    lines = f.readlines()
    f.close()
    indexInstruct = 0
    indexEnd = 0
    for i in range(0,len(lines)):
        if(indexInstruct == 0 and lines[i] == "char* INSTRUCTIONS[] = {\n"):
            indexInstruct = i
        elif(indexEnd == 0 and lines[i] == "};\n"):
            indexEnd = i

    if(indexInstruct == 0 or indexEnd == 0):
        exit(-1)

    linesStart = lines[:indexInstruct+1]
    linesEnd = lines[indexEnd:]
    for i in range(0, len(instructs)):
        if i < len(instructs) -1:
            linesStart.append(f'\t"{instructs[i]}",\n')
        else:
            linesStart.append(f'\t"{instructs[i]}"\n')

    lines = []
    lines = linesStart+linesEnd
    indexInstruct = 0
    indexEnd = 0
    for i in range(0,len(lines)):
        if(indexInstruct == 0 and lines[i] == "void ExecuteCurrentInstruction(){\n"):
            indexInstruct = i
        elif(indexInstruct != 0 and indexEnd == 0 and lines[i] == "}\n"):
            indexEnd = i


    if(indexInstruct == 0 or indexEnd == 0):
        exit(-1)

    linesStart = lines[:indexInstruct+1]
    linesEnd = lines[indexEnd:]

    lines = []
    lines = linesStart+genSwitch()+linesEnd


    f = open("CVM/main.cpp","w")
    f.writelines(lines)
    f.close()

    f = open("CasmParser/Casmparser.java","r")
    lines = f.readlines()
    f.close()
    indexInstruct = 0
    indexEnd = 0
    for i in range(0,len(lines)):
        if(indexInstruct == 0 and lines[i] == "    public static final String[] INSTRUCTIONS = {\n"):
            indexInstruct = i
        elif(indexEnd == 0 and lines[i] == "    };\n"):
            indexEnd = i

    if(indexInstruct == 0 or indexEnd == 0):
        exit(-1)
    linesStart = lines[:indexInstruct+1]
    linesEnd = lines[indexEnd:]
    for i in range(0, len(instructs)):
        if i < len(instructs) -1:
            linesStart.append(f'\t"{instructs[i]}",\n')
        else:
            linesStart.append(f'\t"{instructs[i]}"\n')

    f = open("CasmParser/Casmparser.java","w")
    f.writelines(linesStart+linesEnd)
    f.close()

def toNum(uNum):
    return int(uNum[1:])//8

def getNumFrom(numList):
    if(len(numList) == 1):
        return [toNum(numList[0])]
    newList = []
    for i in range(0,len(numList)):
        newList.append(toNum(numList[i]))
    return newList

def getParamFromSize(size, totalSize):
    if size == 1:
        return f'*(IP+{totalSize+1})'
    if size == 8:
        return f'*((u64*)(IP+{totalSize+1}))'
    return ''


def createFunctionCall(index):
    if index == 0:
        return ['break;']
    elif index == 255:
        return ['end = true;', 'break;']
    fLines = []
    fCall = f'{instructs[index]}('
    totalSize = 0
    for i in range(0,len(paramSize[index])):
        if(i > 0):
            fCall += ', '
        fCall += getParamFromSize(paramSize[index][i], totalSize)
        totalSize += paramSize[index][i]
    fCall += (f');')
    fLines.append(fCall)
    if(totalSize > 0 and instructs[index][:3] != "jmp" and instructs[index] != "call"):
        fLines.append(f'inc_IP({totalSize});')
    fLines.append('break;')
    return fLines

def genFCalls():
    for i in range(0,len(params)):
        if(params[i] == ''):
            paramSize.append([0])
        else:
            paramSize.append(getNumFrom(params[i].split(' ')[0::2]))
        fCalls.append(createFunctionCall(i))
    return fCalls

def genSwitch():
    fCalls = genFCalls()
    switch = []
    switch.append('\tswitch (*IP)\n')
    switch.append('\t{\n')
    for i in range(0,len(fCalls)):
        switch.append(f'\t\tcase {i}:\n')
        for line in fCalls[i]:
            switch.append(f'\t\t\t{line}\n')
    switch.append('\t\tcase 255:\n')
    switch.append('\t\t\tend=true;\n')
    switch.append('\t\t\tbreak;\n')
    switch.append('\t\tdefault:\n')
    switch.append('\t\t\tbreak;\n')
    switch.append('\t}\n')
    switch.append('\tinc_IP(1);\n')
    return switch

def main():
    writeCommandsAndSwitch()
main()