#!/usr/bin/env python3
import to_regex

REGEX_DEFS = {}

def simplify_grammar(grammar):
    new_grammar = {}
    for k in grammar:
        alts = grammar[k]
        new_alts = []
        for rule in alts:
            seen = {}
            new_rule = []
            for token in rule:
                regex = to_regex.token_to_regex(grammar, token)
                if regex in seen:
                    new_token = seen[regex]
                    new_rule.append(new_token)
                else:
                    seen[regex] = token
                    new_rule.append(token)
            new_alts.append(new_rule)
        new_grammar[k] = new_alts
    return new_grammar

import json
def main(arg):
    with open(arg) as f:
        g = json.load(f)
    new_grammar = simplify_grammar(g)
    json.dump(new_grammar, sys.stdout)

import sys
main(sys.argv[1])
