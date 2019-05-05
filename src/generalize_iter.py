#!/usr/bin/env python3

from helpers import tree_to_string
import copy

TO_REPLACE = []
def replace_it(i, j):
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
    for i in keys:
        j_keys = [j for j in idx_map.keys() if j < i]
        for j in j_keys:
            a = can_it_be_replaced(idx_map[i], idx_map[j])
            b = can_it_be_replaced(idx_map[j], idx_map[i])
            if a and b:
                replace_it(idx_map[j], idx_map[i])
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

    idxs = {}
    for i,child in enumerate(children):
        if ':while_' in child[0]: idxs[i] = child
    if idxs:
        generalize_loop(idxs)

import json
import check

TREE = None

def all_to_list(v):
    name, children, *rest = v
    return [name, [all_to_list(c) for c in children], *rest]

def replace_all():
    for i, j in TO_REPLACE:
        j[0] = i[0]

def main():
    global TREE
    j = json.load(sys.stdin)
    check.init_module(j['original'])
    TREE = j['tree']
    generalize(TREE)
    replace_all()
    j['tree'] = TREE
    json.dump(j, sys.stdout)

import sys
main()
