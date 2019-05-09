#!/usr/bin/env python3
import pudb
br = pudb.set_trace

import sequitur
def sequitur_collapse(rule):
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

def merge_list(k, v):
    return [merge(k_, v_) for k_, v_ in zip(k, v)]


def merge_set(k, v):
    if isinstance(k, list):
        return merge_list(k+v)
    elif isinstance(k, tuple):
        assert len(k[0]) == len(v[0])
        if isinstance(k[0], str):
            if k[0] != v[0]:
                assert ':if_' in k[0]
                assert k[0].split()[0] == v[0].split()[0]
                x = {'alternatives':(k[0], v[0])}
            else:
                x = k[0]
        else:
            x = [merge_set(k_, v_) for k_, v_ in zip(k[0], v[0])]
        return x, (k[1] | {v[1]})
    elif isinstance(k, str):
        br()
        assert k == v
        return k
    else:
        assert k[0] == v[0]
        return k[0], (k[1] | {v[1]})

def merge_rules(rules):
    # TODO: we need to go a bit beyond what we do here. Currently
    # it does not recognize when things repeat with a count (a, {1}) is
    # same as  ([(a, {1})], {1}). The difference in structure is a
    # result of not grouping them right in group_rules
    # (ultimately due to sequitur giving different structures for
    # [[a b] c] and [a b c]).

    v = to_set(rules[0])
    if len(rules) == 1:
        return v
    for k in rules[1:]:
        v = merge_set(v, k)
    return v

def strip_if_alts(s):
    if ':if_' not in s:
        return s
    arr = s.split('#')
    assert len(arr) == 2
    a, b, c = arr[0].split(' ')
    return '#'.join([a + ' ' + b + ' ', arr[1]])

def group_rules(flattened_rules, grammar):
    # the ifs with differing alts should also come together here <-- verify
    sx = [strip_count(s, grammar, '', False) for s in flattened_rules]
    sy = [strip_if_alts(s) for s in sx]
    simple = set([str(s) for s in sy]) # our templates.
    rule_hash = {s:[] for s in simple}
    for rule in flattened_rules:
        s = strip_if_alts(strip_count(rule,  grammar, '', False))
        rule_hash[str(s)].append(rule)
    return rule_hash

def convert_to_regex(grammar, e):
    has_star = False
    item, count = e
    if count == {1}:
        if isinstance(item, list):
            return [convert_to_regex(grammar, t) for t in item]
        else:
            return to_regex.token_to_regex(grammar, item, has_star)
    else:
        if isinstance(item, list):
            return [convert_to_regex(grammar, t) for t in item]
        else:
            return to_regex.token_to_regex(grammar, item, has_star)

import to_regex
def readable(grammar):
    # first use sequitur to collapse each rule to repetition counters.
    r_grammar = {}
    for k in grammar:
        alts = []
        for rule in grammar[k]:
            alts.append(sequitur_collapse(rule))
        r_grammar[k] = alts
    grammar = None 

    # next, group_rules the rules of each alt by their common signature.
    # i.e (a|b){10} and (a|b){2} comes together.
    # the ifs with differing alts should also come together here <-- verify
    s_grammar = {}
    for k in r_grammar:
        alts = r_grammar[k]
        new_alts = group_rules(alts, r_grammar)
        s_grammar[k] = new_alts
    r_grammar = None 

    # merge the grouped rules. Essentially
    # (a|b){10} and (a|b){2} becomes (a|b){2, 10}
    # no regex merging yet.
    m_grammar = {}
    for k in s_grammar:
        rule_hash = s_grammar[k]
        alts = []
        for v_ in rule_hash.values():
            a = merge_rules(v_)
            alts.append(a)
        m_grammar[k] = alts
    s_grammar = None 

    # now, the while_ and if_ stuff can be summarized to regex, and
    # their definitions removed. Only method defs should remain
    e_grammar = {}
    for k in m_grammar:
        alts = []
        for s_tuple in m_grammar[k]:
            # here, we should remember to merge if conditions
            # and identify nullable things.
            # Remember to use the merged regex definitions of tokens.
            a = to_regex.sequitur_tuple_to_regex(m_grammar, s_tuple)
            alts.append(a)
        e_grammar[k] = alts
    m_grammar = None 

    # finally print it all out
    for k in e_grammar:
        if ':while_' in k or ':if_' in k: continue
        print(k)
        for alt in sorted(set([str(s) for s in e_grammar[k]])):
            print(" | ", alt)
        print()

import json
def main(arg):
    with open(arg) as f:
        readable(json.load(f))

import sys
main(sys.argv[1])

