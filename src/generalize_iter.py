#!/usr/bin/env python3

from helpers import tree_to_string
import copy

TO_REPLACE = []
def replace_name(i, j):
    # simply rename idx_map[i] to idx_map[j]
    TO_REPLACE.append((i, j))

def replace_nodes(node1, node2, my_tree):
    str0 = tree_to_string(my_tree)
    old = copy.copy(node2)
    node2.clear()
    for n in node1:
        node2.append(n)
    str1 = tree_to_string(my_tree)
    assert str0 != str1
    node2.clear()
    for n in old:
        node2.append(n)
    str2 = tree_to_string(my_tree)
    assert str0 == str2
    return str1

def can_it_be_replaced(i, j):
    my_tree = TREE
    original_string = tree_to_string(my_tree)
    a = tree_to_string(i)
    b = tree_to_string(j)
    if a == b:
        return True
    my_string = replace_nodes(i, j, my_tree)
    v = check.check(my_string)
    return v

def generalize_loop(idx_map):
    keys = sorted(idx_map.keys(), reverse=True)
    for i in keys: # <- nodes to check for replacement -- started from the back
        i_m = idx_map[i]
        j_keys = sorted([j for j in idx_map.keys() if j < i])
        for j in j_keys: # <- nodes that we can replace i_m with -- starting from front.
            j_m = idx_map[j]
            if i_m[0] == j_m[0]: assert False
            a = can_it_be_replaced(i_m, j_m)
            b = can_it_be_replaced(j_m, i_m)
            if a and b:
                replace_name(i_m, j_m) # <- replace i_m by j_m
                break
    return idx_map

def generalize(tree):
    # The idea is to look through the tree, looking for while loops
    # when one sees a while loop, start at one end, and see if the
    # while iteration index can be replaced by the first one, and vice
    # versa. If not, try with the second one and so on until the first one
    # succeeds. When one succeeds, replace the definition of the matching
    # one with an alternate with the last's definition, and replace the
    # name of last with the first, and delete last.
    node, children, *_rest = tree
    for child in children:
        generalize(child)
        replace_all()

    idxs = {}
    for i,child in enumerate(children):
        if ':while_' in child[0]: idxs[i] = child
    gmap = generalize_loop(idxs) if idxs else {}

import json
import check

TREE = None

def all_to_list(v):
    name, children, *rest = v
    return [name, [all_to_list(c) for c in children], *rest]

def replace_all():
    for i, j in TO_REPLACE:
        i[0] = j[0]
    TO_REPLACE.clear()

def main(arg):
    global TREE
    with open(arg) as f:
        j = json.load(f)
    check.init_module(j['original'])
    TREE = j['tree']
    generalize(TREE)
    j['tree'] = TREE
    json.dump(j, sys.stdout)

import sys
main(sys.argv[1])
