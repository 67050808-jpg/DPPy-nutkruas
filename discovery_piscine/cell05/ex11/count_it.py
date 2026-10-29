#!usr/bin/env python3
import sys
if len(sys.arghv) <=1:
    print("none")
else:
    for i in sys.argv[1:]:
        print(f"{i} : len.{sys.argv[i]} ")