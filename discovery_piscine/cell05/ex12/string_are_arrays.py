#!/usr/bin/env python3
import sys
if len(sys.argv) != 2:
    print("none")
else:
    count = 0
    for i in sys.argv[1]:
        if i == "z":
            count = count + 1
if count == 0:
    print("none")
else:
    print("z"*count)       

