#!/usr/bin/python3
import sys
import os

SELF_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(SELF_DIR + '/../pythonx')

from indenty.scanner import Scanner, Indents


KIND_STR = ["Unknown", "Spaces", "Tabs"]

file = open(sys.argv[1])
lines = file.readlines()
file.close()

scanner = Scanner()
scanner.modelines = 5
indents = scanner.scan(lines)
if indents:
    kind = KIND_STR[indents.kind]
    if indents.kind != Indents.UNKNOWN:
        print("%s %u" % (kind, indents.width))
    else:
        print("%s" % kind)
