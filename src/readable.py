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

def replace(grammar, key, by):
    del grammar[key]
    for k in grammar:
        rules = grammar[k]
        new_rules = []
        for rule in rules:
            new_rule = []
            for token in rule:
                if token == key:
                    new_rule.append(by)
                else:
                    new_rule.append(token)
            new_rules.append(new_rule)
        grammar[k] = new_rules
    return grammar


def simplify(my_grammar):
    to_replace = {}
    for k in my_grammar:
        rules = my_grammar[k]
        if len(rules) > 1:
            continue
        else:
            rule = rules[0]
            if len(rule) > 1:
                continue
            else:
                to_replace[k] = rule[0]
    del to_replace['<START>']
    for key in to_replace:
        replace(my_grammar, key, to_replace[key])

    # remove redundant rules.
    for key in my_grammar:
        rules = my_grammar[key]
        new_rules = {}
        for rule in rules:
            new_rules[str(rule)] = rule
        my_grammar[key] = list(new_rules.values())
    return to_replace


def remove_redundant(grammar):
    # keys with exactly same rules get removed.
    seen = {}
    to_replace = {}
    for k in grammar:
        key = str(sorted(grammar[k]))
        if key in seen:
            to_replace[k] = seen[key][0]
        else:
            seen[key] = (k, grammar[k])

    for key in to_replace:
        replace(grammar, key, to_replace[key])
    return to_replace


def readable(grammar):
    # first simplify and then do the repeating.
    # simplify involves, looping through the grammar, looking for single defs.
    # Then replacing the rule witi its definitions.
    cont = True
    while cont:
        cont = simplify(grammar)
        remove_redundant(grammar)

    for k in grammar:
        print(k)
        alt = grammar[k]
        results = set()
        for rule in alt:
            #results.add(str(summarize_repeating(rule)))
            results.add(''.join(rule))
        for r in results:
            print("   | %s" % repr(r))


import json
def main(arg):
    with open(arg) as f:
        readable(json.load(f))

import sys
main(sys.argv[1])

