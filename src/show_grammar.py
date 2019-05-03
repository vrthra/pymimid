#!/usr/bin/env python3

import sys
import json

MAX_INDENT = 10
space = "|\t"

def show_json(d, indent):
    if indent > MAX_INDENT:
        print(space * indent, json.dumps(d))
    else:
        if isinstance(d, dict):
            for k in d:
                print(space * indent, k, ":")
                show_json(d[k], indent+1)
        elif  isinstance(d, list):
            for i,k in enumerate(d):
                if isinstance(k, (list, dict)):
                    print(space * indent, i, ":")
                    show_json(k, indent+1)
                else:
                    print(space * indent, i,":", json.dumps(k))

MAX_LEN = 140

def show_json_rev(d, indent):
    s = json.dumps(d)
    if len(s) <= MAX_LEN:
        print(space * indent, s)
    else:
        if isinstance(d, dict):
            for k in d:
                s = json.dumps(d[k])
                if len(s) <= MAX_LEN:
                    print(space * indent, k, ":", s)
                else:
                    print(space * indent, k, ":")
                    show_json_rev(d[k], indent+1)
        elif  isinstance(d, list):
            for i,k in enumerate(d):
                if isinstance(k, (list, dict)):
                    s = json.dumps(k)
                    if len(s) <= MAX_LEN:
                        print(space * indent, i, ":", s)
                    else:
                        print(space * indent, i, ":")
                        show_json_rev(k, indent+1)
                else:
                    print(space * indent, i,":", json.dumps(k))

def main(arg, keys):
    d = json.load(open(arg))
    for k in keys: d = d[k]
    show_json_rev(d, 0)

main(sys.argv[1], sys.argv[2:])
