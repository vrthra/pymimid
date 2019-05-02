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

import sys, imp
#import parse_ # does not have the .in_ construction for taints.
parse_ = imp.new_module('parse_')

exec_map = {}
def check(s, label):
    if s in exec_map: return exec_map[s]
    v =  _check(s)
    #print("\t\t", repr(s), v, ' from: %s' % str(label))
    exec_map[s] = v
    return v

def _check(s):
    try:
        parse_.main(s)
        return True
    except:
        return False

# What samples to use for a{n} to conirm that a* is a valid regex.
SAMPLES_FOR_REP = [0, 1, 2]

class Regex:
    def to_rules(self):
        if isinstance(self, Alt):
            for a1 in self.a1.to_rules():
                yield a1
            for a2 in self.a2.to_rules():
                yield a2
        elif  isinstance(self, Rep):
            for a3 in self.a.to_rules():
                for n in SAMPLES_FOR_REP:
                    yield a3 * n
        elif  isinstance(self, Seq):
            for a4 in self.arr[0].to_rules():
                if self.arr[1:]:
                    for a5 in Seq(self.arr[1:]).to_rules():
                        yield a4 + a5
                else:
                    yield a4

        elif  isinstance(self, One):
            assert not isinstance(One, Regex)
            yield self.o
        else:
            assert False

    def __str__(self):
        if isinstance(self, Alt):
            return "(%s|%s)" % (str(self.a1), str(self.a2))
        elif  isinstance(self, Rep):
            return "(%s)*" % self.a
        elif  isinstance(self, Seq):
            if len(self.arr) == 1:
                return "(%s)" % ''.join(str(a) for a in self.arr)
            else:
                return "(%s)" % ''.join(str(a) for a in self.arr)
        elif  isinstance(self, One):
            return ''.join(str(o).replace('*', '[*]').replace('(', '[(]').replace(')', '[)]') for o in self.o)
        else:
            assert False

class Alt(Regex):
    def __init__(self, a1, a2): self.a1, self.a2 = a1, a2
class Rep(Regex):
    def __init__(self, a): self.a = a
class Seq(Regex):
    def __init__(self, arr): self.arr = arr
class One(Regex):
    def __init__(self, o): self.o = o

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

str_db = {}
regex_map = {}
final_regex_map = {}


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
                v = check(expr, regex)
                regex_map[regex] = v
                if not v: # this regex failed
                    all_true = False
                    break # one sample of regex failed. Exit
            elif regex not in regex_map:
                v = check(expr, regex)
                regex_map[regex] = v
                if not v: # this regex failed.
                    all_true = False
                    break # one sample of regex failed. Exit
            all_true = True
        if all_true: # get the first regex that covers all samples.
            #print("nt:", nt, 'rule:', str(regex))
            return regex
    return None

    for k in regex_map:
        if regex_map[k]:
            print('->        ', str(k))
    print('')
    regex_map.clear()
    sys.stdout.flush()

def process_rule(nt, my_rule, tree, new_rule):
    for alt in my_rule:
        regex = process_alt(nt, alt, tree)
        print("->    ", str(regex))
        new_rule.append(str(regex))
    print('-'*10)
    sys.stdout.flush()

def process_grammar(grammar, tree, new_grammar):
    for nt in grammar:
        print("->", nt)
        my_rule = grammar[nt]
        new_rule = []
        new_grammar[nt] = new_rule
        process_rule(nt, my_rule, tree, new_rule)
    sys.stdout.flush()

def main(tree_file, nt, alt):
    my_tree = json.load(open(tree_file))
    tree = my_tree['tree']
    src = my_tree['original']
    exec(open(src).read(), parse_.__dict__)
    grammar = get_grammar(tree)
    if nt is '':
        for i, k in enumerate(grammar):
            for j,a in enumerate(grammar[k]):
                print(i,j,k, ' '.join(["%d:%s" % (i,t) for i,t in enumerate(a)]))
            print()
        return
    generate_expansion_db(tree, str_db, grammar)
    sys.stdout.flush()
    #for i in str_db: print(i, str_db[i])
    new_grammar = {}
    process_grammar(grammar, tree, new_grammar)
    print(new_grammar)

if __name__ == '__main__':
    main(sys.argv[1], nt=(sys.argv[2] if len(sys.argv) > 2 else None), alt=(int(sys.argv[3]) if len(sys.argv) > 3 else -1))
