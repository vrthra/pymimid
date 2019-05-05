def is_method(token):
    return True

def token_to_regex(grammar, token):
    if token not in grammar:
        if token[0] + token[-1] == '<>':
            return token
        return repr(token)
    definition = grammar[token]
    if ':while_' in token:
        return "%s" % alts_to_regex(grammar, definition)
    elif ':if_' in token:
        return alts_to_regex(grammar, definition)
    elif is_method(token):
        return token

def rule_to_regex(grammar, rule):
    return " ".join([token_to_regex(grammar, r) for r in rule])

def alts_to_regex(grammar, alts):
    if len(alts) == 1:
        return "%s" % "|".join(sorted([rule_to_regex(grammar, a) for a in alts]))
    else:
        return "(%s)" % "|".join(sorted([rule_to_regex(grammar, a) for a in alts]))
