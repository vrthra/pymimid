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

def no_overlap(arr):
    def is_included(ranges, s_, e_):
        return {(s, e) for (s, e) in ranges if (s_ >= s and e_ <= e)}

    def has_overlap(ranges, s_, e_):
        return {(s, e) for (s, e) in ranges if \
                    (s_ >= s and s_ <= e) or \
                    (e_ >= s and e_ <= e) or \
                    (s_ <= s and e_ >= e)}

    my_ranges = {}
    for a in arr:
        _, _, s, e = a
        included = is_included(my_ranges, s, e)
        if included:
            continue # we will fill up the blanks later.
            #for i in included:
                #insert_into_node(my_ranges[i], i)
                #r = my_ranges[i][1]+ a[1]
                #my_ranges[i][1].clear()
                #sr = sorted(r, key=lambda x: x[2])
                #my_ranges[i][1].extend(sr)
        else:
            overlaps = has_overlap(my_ranges, s, e)
            if overlaps:
                # unlike include which can happen only once in a set of
                # non-overlapping ranges, overlaps can happen on multiple
                # parts. One option is to simply remove the overlapping indexes
                # alone from the parent method if parent method can be
                # identified.
                assert False
            else:
                my_ranges[(s, e)] = a
    res = my_ranges.values()
    s = sorted(res, key=lambda x: x[2]) # assert no overlap, and order by starting index
    return s



from helpers import tree_to_string

# convert a mapped tree to the fuzzingbook derivation tree.
def to_tree(node, my_str):
    method_name = ("<%s>" % node['name']) if node['name'] is not None else '<START>'
    indexes = node['indexes']
    node_children = [to_tree(c, my_str) for c in node.get('children', [])]
    idx_children = indexes_to_children(indexes, my_str)
    children = no_overlap([c for c in node_children if c is not None] + idx_children)
    if not children:
        return None
    start_idx = children[0][2]
    end_idx = children[-1][3]
    si = start_idx
    my_children = []
    # FILL IN chars that we did not compare. This is likely due to an i + n
    # instruction.
    for c in children:
        if c[2] != si:
            sbs = my_str[si: c[2]]
            my_children.append((sbs, [], si, c[2]-1))
        my_children.append(c)
        si = c[3] + 1

    m = (method_name, my_children, start_idx, end_idx)
    return m

# We need only the last comparisons made on any index
# This means that we care for only the last parse in an
# ambiguous parse.

# What we actually need is that we can not replace last comparisons
# if it came from a child.
HEURISTIC=True
def last_comparisons(comparisons):
    last_cmp_only = {}
    last_idx = {}

    # get the last indexes compared in methods.
    for idx, char, mid in comparisons:
        if mid in last_idx:
            if idx > last_idx[mid]:
                last_idx[mid] = idx
        else:
            last_idx[mid] = idx

    for idx, char, mid in comparisons:
        if HEURISTIC:
            if idx in last_cmp_only:
                if last_cmp_only[idx] > mid:
                    # do not clobber children unless it was the last character
                    # for that child.
                    if last_idx[mid] > idx:
                        # if it was the last index, may be the child used it
                        # as a boundary check.
                        continue
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

    print("INPUT:", my_str, file=sys.stderr)
    tree = to_tree(method_tree[first], my_str)
    print("RECONSTRUCTED INPUT:", tree_to_string(tree), file=sys.stderr)
    my_tree = {'tree': tree, 'original': call_trace['original']}
    json.dump(my_tree, sys.stdout)
    assert tree_to_string(tree) == my_str
    #with open('derivation_tree.json', 'w+') as f: json.dump(tree, f)
