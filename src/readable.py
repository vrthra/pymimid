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

def find_while_repetition(rule):
    new_rule = []
    res = []
    rep = []
    my_dict = dict(rule)
    for token, regex in rule:
        if 'while' in token:
            if not rep:
                rep.append(regex)
            else:
                if regex != rep[0]:
                    rep.append(regex)
                else:
                    if not res:
                        res.append(rep)
                    else:
                        if rep != res[-1]:
                            res.append(rep)
                        else:
                            pass
                    rep = [regex]
        else:
            res.append(regex)
    if not res or rep != res[-1]:
        res.extend(rep)
    return res
import pudb
br = pudb.set_trace
def find_normal_repetition(rule):
    rep = []
    res = []
    for token in rule:
        if not rep:
            rep.append(token)
        else:
            for i, r in enumerate(rep):
                if r == token:
                    break
            res.extend(rep[:i])
            rep = rep[i:]
            if not res:
                res.append(rep)
            else:
                if rep != res[-1]:
                    res.append(rep)
                else:
                    pass
            rep = [token]
    if not res or rep != res[-1]:
        res.extend(rep)
    return res

def find_repetition(rule):
    #rule = find_while_repetition(rule)
    #rule = ["(%s)+" % ''.join(i) if isinstance(i, list) else i[1] for i in rule]
    rule = find_normal_repetition(rule)
    rule = [("(%s)+" % ''.join(i) if isinstance(i, list) else i) for i in rule]
    return '\n->  '.join(rule)

import to_regex
def readable(grammar):
    for k in grammar:
        if ':while_' in k or ':if_' in k:
            continue
        print(k, " ::=")
        alts = set()
        for rule in grammar[k]:
            new_rule = []
            for token in rule:
                new_rule.append((token, to_regex.token_to_regex(grammar, token)))
            #alts.add(' '.join([i for i,t in new_rule]))
            #alts.add(' '.join([t for i,t in new_rule]))
            alts.add(find_repetition([t for i, t in new_rule]))
        for r in sorted(alts):
            print(" | ", r)
            print()
        print()
import json
def main(arg):
    with open(arg) as f:
        readable(json.load(f))

import sys
main(sys.argv[1])

