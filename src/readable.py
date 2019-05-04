#!/usr/bin/env python3

# generalize stuff like loops.

def shrink_whiles(arr):
    last = None
    new_arr = []
    for a in arr:
        if last is None:
            last = a
            new_arr.append(a)
            continue
        else:
            if last == a:
                continue
            else:
                new_arr.append(a)
    return new_arr


def summarize_repeating(my_tokens):
    tokens = my_tokens
    res = []
    while tokens:
        for i, token in enumerate(tokens):
            if ':while_' in token:
                res.append(([], '*'))
                break
            else:
                res.append(token)
        for j, token in enumerate(tokens[i:]):
            if ':while_' in token:
                arr = res[-1][0]
                if arr == []:
                    arr.append(token)
                else:
                    if token == arr[0]:
                        res.append(([token], '*'))
                    else:
                        arr.append(token)
            else:
                break
        tokens = tokens[i+j+1:]
    return shrink_whiles(res)


def readable(grammar):
    for k in grammar:
        print(k)
        alt = grammar[k]
        results = set()
        for rule in alt:
            results.add(str(summarize_repeating(rule)))
        for r in results:
            print("| \t %s" % r)


import json
def main(arg):
    with open(arg) as f:
        readable(json.load(f))

import sys
main(sys.argv[1])

