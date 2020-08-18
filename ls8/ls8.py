#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

if len(sys.argv) != 2:
    print("Please enter a filename:")
    print("python3 ls8.py [filename]")
    sys.exit()

cpu = CPU()

cpu.load()
cpu.run()
