#!/usr/bin/env python3
import json
import sys

# reconstruct the actual method trace from a trace with the following
# format
# key   : [ mid, method_name, children_ids ]
# "6704": [ 6704, "unify_key", [6714, 6715] ]  <-- e.g
# "6714": [ 6714, "unify_val", [] ]
# "6715": [ 6715, "unify_val", [] ]
# to:
# {
# "6704": [ id: 6704, name: "unify_key", children: [
#                               "6714": [ id: 6714, name: "unify_val", children: [], indexes:[] ],
#                               "6715": [ id: 6715, name: "unify_val", children:[], indexes:[] ]
#                              ],
#                              indexes: [] ]
# "6714": [ 6714, "unify_val", [] ]
# "6715": [ 6715, "unify_val", [] ]
# }
def reconstruct_method_tree(method_map):
    first = None
    tree_map = {}
    for key in method_map:
        m_id, m_name, m_children = method_map[key]

        children = []
        if m_id in tree_map:
            # just update the name and children
            assert not tree_map[m_id]
            tree_map[m_id]['id'] = m_id
            tree_map[m_id]['name'] = m_name
            tree_map[m_id]['children'] = children
            tree_map[m_id]['indexes'] = []
        else:
            assert first is None
            tree_map[m_id] =  {'id':m_id, 'name': m_name, 'children':children, 'indexes':[]}
            first = m_id

        for c in m_children:
            assert c not in tree_map
            val = {}
            tree_map[c] = val
            children.append(val)
    return (first, tree_map)

# Add the comparison indexes to the method tree that we constructed
def attach_comparisons(method_tree, comparisons):
    for idx in comparisons:
        mid = comparisons[idx]
        method_tree[mid]['indexes'].append(idx)

from operator import itemgetter
import itertools as it

# convert a list of indexes to a corresponding terminal tree node
def to_node(idxes, my_str):
    return (my_str[idxes[0]:idxes[-1]+1], [], idxes[0], idxes[-1])

# convert our list of indexes to lists of contiguous indexes first, then
# convert them to terminal tree nodes.
def indexes_to_children(indexes, my_str):
    # return a set of one level child nodes with contiguous chars from indexes
    lst = [list(map(itemgetter(1), g)) for k, g
            in it.groupby(enumerate(indexes), lambda x:x[0]-x[1])]
    return [to_node(n, my_str) for n in lst]

import re
RE_NONTERMINAL = re.compile(r'(<[^<> ]*>)')
# convert the derivation tree to string
def tree_to_string(tree):
    def is_nonterminal(s): return re.match(RE_NONTERMINAL, s)
    symbol, children, *_ = tree
    if children: return ''.join(tree_to_string(c) for c in children)
    else: return '' if is_nonterminal(symbol) else symbol

# convert a mapped tree to the fuzzingbook derivation tree.
def to_tree(node, my_str):
    method_name = ("<%s>" % node['name']) if node['name'] is not None else '<START>'
    indexes = node['indexes']
    node_children = [to_tree(c, my_str) for c in node.get('children', [])]
    idx_children = indexes_to_children(indexes, my_str)
    children = sorted([c for c in node_children if c is not None] + idx_children, key=lambda x: x[2]) # assert no overlap, and order by starting index
    if not children:
        return None
    start_idx = children[0][2]
    end_idx = children[-1][3]
    return (method_name, children, start_idx, end_idx)

# We need only the last comparisons made on any index
# This means that we care for only the last parse in an
# ambiguous parse.
def last_comparisons(comparisons):
    last_cmp_only = {}
    for idx, mid in comparisons:
        last_cmp_only[idx] = mid
    return last_cmp_only

if __name__ == "__main__":
    call_trace_f = 'call_trace.json' if len(sys.argv) < 2 else sys.argv[1]
    with open(call_trace_f) as f:
        call_trace = json.load(f)
    method_map = call_trace['method_map']

    first, method_tree = reconstruct_method_tree(method_map)
    comparisons = call_trace['comparisons']
    attach_comparisons(method_tree, last_comparisons(comparisons))

    my_str = call_trace['inputstr']

    print("INPUT:", my_str)
    tree = to_tree(method_tree[first], my_str)
    print("RECONSTRUCTED INPUT:", tree_to_string(tree))
    print(tree)
    assert tree_to_string(tree) == my_str
    with open('derivation_tree.json', 'w+') as f:
        json.dump(tree, f)
