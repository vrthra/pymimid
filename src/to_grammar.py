#!/usr/bin/env python
import json
import sys

def to_grammar(tree, grammar):
    node, children, _, _ = tree
    tokens = []
    if node not in grammar:
        grammar[node] = set()
    for c in children:
        if c[1] == []:
            tokens.append(c[0])
        else:
            tokens.append(c[0])
            to_grammar(c, grammar)
    grammar[node].add(tuple(tokens))
    return grammar


def merge_grammar(g1, g2):
    all_keys = set(list(g1.keys()) + list(g2.keys()))
    merged = {}
    for k in all_keys:
        alts = g1.get(k, set()) | g2.get(k, set())
        merged[k] = alts
    return merged

def process(files):
    start = set()
    final_grammar = {}
    for fn in files:
        with open(fn) as f:
            tree = json.load(f)[1][0]
            start.add(tree[0])
        g = to_grammar(tree, {})
        final_grammar = merge_grammar(final_grammar, g)
    assert len(start) == 1
    return {k:list(v) for k,v in final_grammar.items()}

if __name__ == '__main__':
    g = process(sys.argv[1:])
    print(json.dumps(g))
