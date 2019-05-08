#!/usr/bin/env python3
import pudb
br = pudb.set_trace

import sequitur
def find_repetition(rule):
    s = [str(r) for r in rule]
    g = sequitur.Grammar()
    g.train_string(s)
    x = g.flatten()
    return x

def strip_count(r, grammar, tcount, to_regex=True):
    if isinstance(r, list):
        return [strip_count(i, grammar, tcount, to_regex) for i in r]
    elif isinstance(r, tuple):
        return strip_count(r[0], grammar, tcount, to_regex)
        if tcount == '':
            return strip_count(r[0], grammar, tcount, to_regex)
        else:
            if r[1] == 1:
                return (strip_count(r[0], grammar, tcount, to_regex), 1)
            else:
                return (strip_count(r[0], grammar, tcount, to_regex), '+') # r[1])
    else:
        if to_regex:
            return to_regex.token_to_regex(grammar, r)
        else:
            return str(r)

def to_set(k):
    if isinstance(k, list):
        return [to_set(i) for i in k]
    elif isinstance(k, tuple):
        return to_set(k[0]), {k[1]}
    else:
        return k

def merge_set(k, v):
    if isinstance(k, list):
        assert len(k) == len(v)
        return [merge_set(k_, v_) for k_, v_ in zip(k, v)]
    elif isinstance(k, tuple):
        return merge_set(k[0], v[0]), k[1] | {v[1]}
    elif isinstance(k, str):
        assert k == v
        return k
    else:
        assert k[0] == v[0]
        return k[0], k[1] | {v[1]}

def merge(rules, k):
    v = to_set(rules[0])
    if len(rules) == 1:
        return v
    for k in rules[1:]:
        v = merge_set(v, k)
    return v

def simplify(flattened_rules, grammar):
    simple = set([str(strip_count(s, grammar, '', False)) for s in flattened_rules]) # our templates.
    rule_hash = {s:[] for s in simple}
    for rule in flattened_rules:
        s = strip_count(rule,  grammar, '', False)
        rule_hash[str(s)].append(rule)
    return [merge(v, k) for k,v in rule_hash.items()]

def convert_to_regex(grammar, e):
    has_star = False
    item, count = e
    if count == {1}:
        if isinstance(item, list):
            return ' '.join([convert_to_regex(grammar, t) for t in item])
        else:
            return str(to_regex.token_to_regexz(grammar, item, has_star))
    else:
        if isinstance(item, list):
            return "(%s)+" % ''.join([convert_to_regex(grammar, t) for t in item])
        else:
            return "(%s)+" % str(to_regex.token_to_regexz(grammar, item, has_star))

import to_regex
def readable(grammar):
    for k in grammar:
        if ':while_' in k or ':if_' in k:
            continue
        print(k, " ::=")
        alts = []
        for rule in grammar[k]:
            #for token in rule:
                #new_rule.append((token, to_regex.token_to_regex(grammar, token)))
            #    new_rule.append(token, to_regex.token_to_regex(grammar, token)))
            #r = [t for i, t in new_rule]
            #alts.add(' '.join([i for i,t in new_rule]))
            #alts.add(' '.join([t for i,t in new_rule]))
            alts.append(find_repetition(rule))
            #alts.append(rule)
        new_alts = simplify(alts, grammar)
        my_new_alts = [convert_to_regex(grammar, a) for a in new_alts]
        #my_new_alts = [str(a) for a in alts]
        for alt in sorted(set(my_new_alts)):
        #for alt in my_new_alts:
            print(" | ", alt)
import json
def main(arg):
    with open(arg) as f:
        readable(json.load(f))

import sys
main(sys.argv[1])

