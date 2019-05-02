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

def main(tree_file, nt, alt):
    my_tree = json.load(open(tree_file))
    tree = my_tree['tree']
    src = my_tree['original']
    grammar = get_grammar(tree)
    if nt is '':
        for i, k in enumerate(grammar):
            for j,a in enumerate(grammar[k]):
                print(i,j,k, ' '.join(["%d:%s" % (i,t) for i,t in enumerate(a)]))
            print()
        return

    new_tree = {}
    new_tree['grammar'] = grammar
    new_tree['tree'] = tree
    new_tree['original'] = src
    print(json.dumps(new_tree))

if __name__ == '__main__':
    main(sys.argv[1], nt=(sys.argv[2] if len(sys.argv) > 2 else None), alt=(int(sys.argv[3]) if len(sys.argv) > 3 else -1))
