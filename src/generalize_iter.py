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
    if v:
        print('[{"%s": "%s"}, {"%s":"%s"}, %s]' % (i[0], a.replace('"', "'"), j[0], b.replace('"', "'"), my_string), file=sys.stderr)
    return v

while_counter = {}
import pudb
br = pudb.set_trace

def unparse_name(method, ctrl, name, num, cstack):
    if ctrl == 'while':
        return "<%s:%s_%s %s>" % (method, ctrl, name, json.dumps(cstack))
    else:
        return "<%s:%s_%s %s+%s>" % (method, ctrl, name, num, json.dumps(cstack))

def parse_name(name):
    # '<_from_json_string:while_1 [1]>'
    assert name[0] + name[-1] == '<>'
    name = name[1:-1]
    method, rest = name.split(':')
    ctrl_name, space, stack = rest.partition(' ')
    if ':while_' in name:
        method_stack = json.loads(stack)
        ctrl, name = ctrl_name.split('_')
        return method, ctrl, int(name), 0, method_stack
    elif ':if_' in name:
        num, mstack = stack.split('+')
        method_stack = json.loads(mstack)
        ctrl, name = ctrl_name.split('_')
        return method, ctrl, int(name), num, method_stack

def update_methods(node, at, new_name):
    nname, children, *rest = node
    if not (':if_' in nname or ':while_' in nname):
        return
    method, ctrl, cname, num, cstack = parse_name(nname)
    cstack[at] = new_name
    name = unparse_name(method, ctrl, cname, num, cstack)
    node[0] = name
    for c in children:
        update_methods(c, at, new_name)

def update_name(k_m, my_id, seen):
    # fixup k_m with what is in my_id, and update seen.
    original = k_m[0]
    method, ctrl, cname, num, cstack = parse_name(original)
    cstack[-1] = float('%d.0' % my_id)
    name = unparse_name(method, ctrl, cname, num, cstack)
    seen[k_m[0]] = name
    k_m[0] = name

    # only replace it at the len(cstack) -1 the
    # until the first non-cf token
    children = []
    for c in k_m[1]:
        update_methods(c, len(cstack)-1, cstack[-1])
    return name, k_m

def generalize_loop(idx_map, while_register):
    global while_counter
    to_replace = []

    # First we check the previous while loops
    idx_keys = sorted(idx_map.keys())
    for while_key in while_register[0]:
        # try sampling here.
        values = while_register[0][while_key]#[0:1]
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

    # then we check he current while iterations
    rkeys = sorted(idx_map.keys(), reverse=True)
    for i in rkeys: # <- nodes to check for replacement -- started from the back
        i_m = idx_map[i]
        if '.0' in i_m[0]: continue
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

    # lastly, update all while names.
    seen = {}
    for k in idx_keys:
        k_m = idx_map[k]
        if ".0" not in k_m[0]:
            if k_m[0] in seen:
                k_m[0] = seen[k_m[0]]
                continue
            # new! get a brand new name!
            while_register[1] += 1
            my_id = while_register[1]

            original_name = k_m[0]
            name, new_km = update_name(k_m, my_id, seen)
            while_register[0][name] = [new_km]
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
        #if 'from_json_dict:while_1 [2' in child[0]: br()
        #if '_from_json_list:while_1 ' in child[0]: br()
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

def has_complex_children(tree):
    node, children, *rest = tree
    for c in children:
        if ':if_' in c[0] or ':while_' in c[0]: return True
    return False

def replace_all(to_replace):
    # remember, we only replace whiles.
    for i, j in to_replace:
        #if has_complex_children(i) or has_complex_children(j):
        method1, ctrl1, cname1, num1, cstack1 = parse_name(i[0])
        method2, ctrl2, cname2, num2, cstack2 = parse_name(j[0])
        assert len(cstack1) == len(cstack2)
        update_methods(i, len(cstack2)-1, cstack2[-1])
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
