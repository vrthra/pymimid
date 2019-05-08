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

import sequitur
def find_repetition(rule):
    #rule = find_while_repetition(rule)
    #rule = ["(%s)+" % ''.join(i) if isinstance(i, list) else i[1] for i in rule]
    #rule = find_normal_repetition(rule)
    #rule = [("(%s)+" % ''.join(i) if isinstance(i, list) else i) for i in rule]
    #return '\n->  '.join(rule)
    s = [str(r) for r in rule]
    g = sequitur.Grammar()
    g.train_string(s)
    x = g.flatten()
    return x

def from_rule(grammar, rule):
    new_rule = []
    for token, count in rule:
        new_rule.append(to_regex.token_to_regex(grammar, token)) # TODO: take care of repetition
    return new_rule

def merge_with(k, count, simple_merged, merged):
    return merged

def flat_list(l):
    return [flat_count(x) if isinstance(x, list) else x for x,c in l]

def flat_count(r):
    if isinstance(r, list):
        return [flat_list(i) for i in r]
    else:
        return flat_list(r[0])

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
    #if len(flattened_rules) == 1:
    #    return from_rule(grammar, flattened_rules)
    simple = set([str(strip_count(s, grammar, '', False)) for s in flattened_rules]) # our templates.
    rule_hash = {s:[] for s in simple}
    for rule in flattened_rules:
        s = strip_count(rule,  grammar, '', False)
        rule_hash[str(s)].append(rule)
    return [str(merge(v, k)) for k,v in rule_hash.items()]

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
        new_alts = simplify(alts, grammar)
        for alt in new_alts:
            print(" | ", ''.join([str(a) for a in alt]))
import json
def main(arg):
    with open(arg) as f:
        readable(json.load(f))

import sys
main(sys.argv[1])

