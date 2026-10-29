#!/usr/bin/env python3
import sys
if len(sys.argv) < 2:
    print("none")
else:
    for word in sys.argv[1:]:
        if not word.endswith("ism"):
            print(word + "ism")
