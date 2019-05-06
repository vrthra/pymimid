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

def node_include(i, j):
    name_i, children_i, s_i, e_i = i
    name_j, children_j, s_j, e_j = j
    if s_i <= s_j and e_i >= e_j:
        return True
    return False


def can_it_be_replaced(i, j):
    if node_include(i, j): return False
    my_tree = TREE
    original_string = tree_to_string(my_tree)
    a = tree_to_string(i)
    b = tree_to_string(j)
    if a == b:
        return True
    my_string = replace_nodes(i, j, my_tree)
    v = check.check(my_string)
    return v

while_counter = {}
import pudb
br = pudb.set_trace
def generalize_loop(idx_map, while_register):
    global while_counter
    to_replace = []
    idx_keys = sorted(idx_map.keys())
    for while_key in while_register[0]:
        # try sampling here.
        values = while_register[0][while_key][0:1]
        for k in idx_keys:
            for v in values:
                k_m = idx_map[k]
                a = can_it_be_replaced(k_m, v)
                if not a: continue
                b = can_it_be_replaced(v, k_m)
                if not b: continue
                to_replace.append((k_m, v)) # <- replace k_m by v
                break
    replace_all(to_replace)

    rkeys = sorted(idx_map.keys(), reverse=True)
    for i in rkeys: # <- nodes to check for replacement -- started from the back
        i_m = idx_map[i]
        if '*' in i_m: continue
        j_keys = sorted([j for j in idx_map.keys() if j < i])
        for j in j_keys: # <- nodes that we can replace i_m with -- starting from front.
            j_m = idx_map[j]
            if i_m[0] == j_m[0]: break
            # previous whiles worked.
            a = can_it_be_replaced(i_m, j_m)
            if not a: continue
            b = can_it_be_replaced(j_m, i_m)
            if not b: continue
            to_replace.append((i_m, j_m)) # <- replace i_m by j_m
            break
    replace_all(to_replace)

    # now, update all while names.
    seen = {}
    for k in idx_keys:
        k_m = idx_map[k]
        if "*" not in k_m[0]:
            if k_m[0] in seen:
                k_m[0] = seen[k_m[0]]
                continue
            # new! get a brand new name!
            km_1, rest = k_m[0].split(' ')
            while_register[1] += 1
            name = "%s *%d>" % (km_1, while_register[1])
            seen[k_m[0]] = name
            k_m[0] = name
            while_register[0][name] = [k_m]
        else:
            name = k_m[0]
            assert name in while_register[0]
            while_register[0][name].append(k_m)

    return idx_map

NODE_REGISTER = {}

def generalize(tree):
    # The idea is to look through the tree, looking for while loops
    # when one sees a while loop, start at one end, and see if the
    # while iteration index can be replaced by the first one, and vice
    # versa. If not, try with the second one and so on until the first one
    # succeeds. When one succeeds, replace the definition of the matching
    # one with an alternate with the last's definition, and replace the
    # name of last with the first, and delete last.
    node, children, *_rest = tree
    if node not in NODE_REGISTER:
        NODE_REGISTER[node] = {}
    register = NODE_REGISTER[node]

    for child in children:
        generalize(child)

    idxs = {}
    last_while = None
    for i,child in enumerate(children):
        # now we need to map the while_name here to the ones in node
        # register. Essentially, we try to replace each.
        if ':while_' not in child[0]:
            continue
        #if '_from_json_string:while_1' in child[0]: br()
        while_name = child[0].split(' ')[0]
        if last_while is None:
            last_while = while_name
            if while_name not in register:
                register[while_name] = [{}, 0]
        else:
            if last_while != while_name:
                # a new while! Generalize the last
                last_while = while_name
                generalize_loop(idxs, register[last_while])
        idxs[i] = child
    if last_while is not None:
        generalize_loop(idxs, register[last_while])

import json
import check

TREE = None

def all_to_list(v):
    name, children, *rest = v
    return [name, [all_to_list(c) for c in children], *rest]

def replace_all(to_replace):
    for i, j in to_replace:
        i[0] = j[0]
    to_replace.clear()

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
