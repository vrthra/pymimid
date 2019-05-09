#!/usr/bin/env python
import json
import random
import sys
import itertools

import mingen
import to_grammar

def get_grammar(tree):
    """ Make sure that the grammar we derive from the tree is deterministic"""
    g = to_grammar.to_grammar(tree, {})
    return {k:sorted(g[k]) for k in g}

def merge(grammar, g):
    for k in list(grammar.keys()) + list(g.keys()):
        grammar[k] = list(set(grammar.get(k, list()) + g.get(k, list())))

def main(tree_file):
    my_trees = json.load(open(tree_file))
    grammar = {}
    for my_tree in my_trees:
        tree = my_tree['tree']
        src = my_tree['original']
        g = get_grammar(tree)
        merge(grammar, g)

    new_tree = {}
    new_tree['grammar'] = grammar
    new_tree['original'] = src
    print(json.dumps(new_tree))

if __name__ == '__main__':
    main(sys.argv[1])
