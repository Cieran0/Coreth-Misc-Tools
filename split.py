#!/usr/bin/python
import subprocess
import sys

output = subprocess.check_output(['java', '-jar', '../casmParser/Main.jar', '../Examples/example.casm']).decode('utf-8')
outputBytes = output.split(',')
for i in range(0,len(outputBytes)):
    print(f"[{i}] {outputBytes[i]}")