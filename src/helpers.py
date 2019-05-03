import re
RE_NONTERMINAL = re.compile(r'(<[^<> ]*>)')
# convert the derivation tree to string
def tree_to_string(tree):
    def is_nonterminal(s): return re.match(RE_NONTERMINAL, s)
    symbol, children, *_ = tree
    if children: return ''.join(tree_to_string(c) for c in children)
    else: return '' if is_nonterminal(symbol) else symbol
