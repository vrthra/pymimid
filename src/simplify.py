#!/usr/bin/env python3
import to_regex
import pudb
br = pudb.set_trace

REGEX_DEFS = {}

def is_regex_a_subset(regex, seen):
    for R in seen:
        if R.sub_match_regex(regex):
            return R
    return False

def simplify_grammar(grammar):
    new_grammar = {}
    for k in grammar:
        alts = grammar[k]
        new_alts = []
        for rule in alts:
            seen = {}
            new_rule = []
            for token in rule:
                #if '0+12' in token: br()
                #if '0+26' in token: br()
                regex = to_regex.token_to_regexz(grammar, token)
                s =  is_regex_a_subset(regex, seen)
                if s:
                    new_token = seen[s]
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
    simplified_grammar = simplify_grammar(g)
    # HEURISTIC
    # if we find a while, find the repeat after, and replace all remaining instances of the while with
    # the order identified from the beginning.
    new_grammar = simplified_grammar #apply_recursion_heuristic(simplified_grammar)
    json.dump(new_grammar, sys.stdout)

import sys
main(sys.argv[1])
