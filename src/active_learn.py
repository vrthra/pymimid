#!/usr/bin/env python
import json
import random
import sys
import itertools

import mingen
import to_grammar
import check
from to_regex import Regex, Alt, Rep, Seq, One


def gen_alt(arr):
    length = len(arr)
    # alpha_1 != e and alpha_2 != e
    for i in range(1,length): # shorter alpha_1 prioritized
        alpha_1, alpha_2 = arr[:i], arr[i:]
        assert alpha_1
        assert alpha_2
        for a1 in gen_rep(alpha_1):
            for a2 in gen_alt(alpha_2):
                yield Alt(a1, a2)
    if length: # this is the final choice.
        yield One(arr)
    return


def gen_rep(arr):
    length = len(arr)
    for i in range(length): # shorter alpha1 prioritized
        alpha_1 = arr[:i]
        # alpha_2 != e
        for j in range(i+1, length+1): # longer alpha2 prioritized
            alpha_2, alpha_3 = arr[i:j], arr[j:]
            assert alpha_2
            for a2 in gen_alt(alpha_2):
                for a3 in gen_rep(alpha_3):
                    yield Seq([One(alpha_1), Rep(a2), a3])
                if not alpha_3:
                    yield Seq([One(alpha_1), Rep(a2)])
    if length: # the final choice
        yield One(arr)
    return

def generate_expansion_db(tree, map_str, grammar):
    """
    Generate a database of possible expansions for each non terminal from
    the given derivation tree, and store it in map_str
    """
    node, children, *_ = tree
    if node in grammar:
        if node not in map_str:
            map_str[node] = {mingen.all_terminals(tree)}
        else:
            map_str[node].add(mingen.all_terminals(tree))

    for c in children:
        generate_expansion_db(c, map_str, grammar)
    return map_str

def tree_to_str(node, nt, expansion):
    """Reconstruct the tree replacing nt with expansion"""
    node, children, *_ = node
    if node == nt: return expansion
    else:
        if not children: return node
        else: return ''.join(tree_to_str(c, nt, expansion) for c in children)

def to_strings(nt, regex, tree):
    """
    We are given the toekn, and the regex that is being checked to see if it
    is the correct abstraction. Hence, we first generate all possible rules
    that can result from this regex.
    The complication is that str_db contains multiple alternative strings for
    each token. Hence, we have to generate a combination of all these strings
    and try to check.
   """
    for rule in regex.to_rules():
        exp_lst_of_lsts = [list(str_db.get(token, [token])) for token in rule]
        for lst in exp_lst_of_lsts: assert lst
        for lst in itertools.product(*exp_lst_of_lsts):
            """
            We first obtain the expansion string by replacing all tokens with
            candidates, then reconstruct the string from the derivation tree by
            recursively traversing and replacing any node that corresponds to nt
            with the expanded string.
            """
            expansion = ''.join(lst)
            #print("Expansion %s:\tregex:%s" % (repr(expansion), str(regex)))
            yield tree_to_str(tree, nt, expansion)

str_db = {}
regex_map = {}


def process_alt(nt, my_alt, tree):
    # active learning of regular righthandside from bastani et al.
    # the idea is as follows: We choose a single nt to refine, and a single
    # alternative at a time.
    # Then, consider that single alternative as a sting, with each token a
    # character. Then apply regular expression synthesis to determine the
    # abstraction candiates. Place each abstraction candidate as the replacement
    # for that nt, and generate the minimum string. Evaluate and verify that
    # the string is accepted (adv: verify that the derivation tree is
    # as expected). Do this for each alternative, and we have the list of actual
    # alternatives.
    for regex in gen_rep(my_alt):
        all_true = False
        for expr in to_strings(nt, regex, tree):
            if regex_map.get(regex, False):
                v = check.check(expr, regex)
                regex_map[regex] = v
                if not v: # this regex failed
                    all_true = False
                    break # one sample of regex failed. Exit
            elif regex not in regex_map:
                v = check.check(expr, regex)
                regex_map[regex] = v
                if not v: # this regex failed.
                    all_true = False
                    break # one sample of regex failed. Exit
            all_true = True
        if all_true: # get the first regex that covers all samples.
            #print("nt:", nt, 'rule:', str(regex))
            return regex
    #raise Exception() # this should never happen. At least one -- the original --  should succeed
    return None

    for k in regex_map:
        if regex_map[k]:
            print('->        ', str(k), file=sys.stderr)
    print('', file=sys.stderr)
    regex_map.clear()
    sys.stdout.flush()

def process_rule(nt, my_rule, tree, new_rule):
    for alt in my_rule:
        regex = process_alt(nt, alt, tree)
        print("->    ", str(regex), file=sys.stderr)
        new_rule.append(str(regex))
    print('-'*10, file=sys.stderr)
    sys.stdout.flush()

def process_grammar(grammar, tree, new_grammar):
    for nt in grammar:
        print("->", nt, file=sys.stderr)
        my_rule = grammar[nt]
        new_rule = []
        new_grammar[nt] = new_rule
        process_rule(nt, my_rule, tree, new_rule)
    sys.stdout.flush()

def main(tree_file, nt, alt):
    my_tree = json.load(open(tree_file))
    tree = my_tree['tree']
    src = my_tree['original']
    check.init_module(src)
    grammar = my_tree['grammar']
    generate_expansion_db(tree, str_db, grammar)
    sys.stdout.flush()
    #for i in str_db: print(i, str_db[i])
    new_grammar = {}
    process_grammar(grammar, tree, new_grammar)
    print(json.dumps(new_grammar))

if __name__ == '__main__':
    main(sys.argv[1], nt=(sys.argv[2] if len(sys.argv) > 2 else None), alt=(int(sys.argv[3]) if len(sys.argv) > 3 else -1))
