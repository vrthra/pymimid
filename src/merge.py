#!/usr/bin/env python3
import json

def process_alt(alt):
    return set([tuple(rule) for rule in alt])

def merge(grammars):
    merged = {}
    for grammar in grammars:
        for k in grammar:
            g_alt = process_alt(grammar[k])
            m_alt = merged.get(k, set())
            merged[k] = g_alt | m_alt
    return {k:list(merged[k]) for k in merged}

def main(args):
    grammars = []
    for a in args:
        with open(a) as f:
            j = json.load(f)
            grammars.append(j['grammar'])
    print(json.dumps(merge(grammars)))

import sys
main(sys.argv[1:])
