#!/usr/bin/env python3
import sys
if len(sys.argv) <=1:
    print("none")
else:
    src = input("What was the parameter? ")
    if src == "".join(sys.argv[1:]):
        print("Good job")
    else:
        print("Nope, sorry ..")