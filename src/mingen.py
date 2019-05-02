#!/usr/bin/env python3
def all_terminals(tree):
    (symbol, children, *_) = tree
    if children is None: return symbol
    if len(children) == 0: return symbol
    return ''.join([all_terminals(c) for c in children])

class MinGen:
    def __init__(self, grammar, start_symbol='<START>', log=False):
        self.grammar, self.start_symbol = grammar, start_symbol

    def expansion_to_children(self, expansion):
        if expansion == []: return [("", [])]
        return [(s, None) if s in  self.grammar else (s, []) for s in expansion if len(s) > 0]

    def possible_expansions(self, node):
        (symbol, children) = node
        if children is None: return 1
        return sum(self.possible_expansions(c) for c in children)

    def any_possible_expansions(self, node):
        (symbol, children) = node
        if children is None: return True
        return any(self.any_possible_expansions(c) for c in children)

    def expand_tree_once(self, tree):
        (symbol, children) = tree
        if children is None: return self.expand_node(tree)
        expandable_children = [c for c in children if self.any_possible_expansions(c)]
        index_map = [i for (i, c) in enumerate(children) if c in expandable_children]
        child_to_be_expanded = random.randrange(0, len(expandable_children))
        children[index_map[child_to_be_expanded]] = self.expand_tree_once(expandable_children[child_to_be_expanded])
        return tree

    def symbol_cost(self, symbol, seen=set()):
        return min(self.expansion_cost(e, seen | {symbol}) for e in self.grammar[symbol])

    def expansion_cost(self, expansion, seen=set()):
        symbols = [s for s in expansion if s in self.grammar]
        if len(symbols) == 0: return 1 
        if any(s in seen for s in symbols): return float('inf')
        return sum(self.symbol_cost(s, seen) for s in symbols) + 1

    def expand_node(self, node):
        (symbol, children) = node
        assert children is None
        possible_children_with_cost = [(self.expansion_to_children(expansion),
                                        self.expansion_cost(expansion, {symbol}), expansion)
                                       for expansion in self.grammar[symbol]]
        costs = [cost for (child, cost, expansion) in possible_children_with_cost]
        chosen_cost = min(costs)
        children_with_chosen_cost = [child for (child, child_cost, _) in possible_children_with_cost if child_cost == chosen_cost]
        chosen_children = random.choice(children_with_chosen_cost)
        return (symbol, chosen_children)

    def expand_tree(self, tree):
        while self.any_possible_expansions(tree):
            tree = self.expand_tree_once(tree)
        return tree

    def gen_tree(self): return self.expand_tree((self.start_symbol, None))
    def gen(self): return all_terminals(self.gen_tree())

import json, sys, random

def mingen(gf, start):
    gf = MinGen(json.load(open(gf)), start_symbol=start)
    return gf.gen()

if __name__ == '__main__':
    print(mingen(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '<START>'))
