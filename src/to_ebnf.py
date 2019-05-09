import re
import copy
RE_EXTENDED_NONTERMINAL = re.compile(r'(<[^<>]*>[?+*])')
RE_PARENTHESIZED_EXPR = re.compile(r'\([^()]*\)[?+*]?')

def convert_spaces(grammar):
    keys = {key: key.replace(' ', '_') for key in grammar}
    new_grammar = {}
    for key in grammar:
        new_alt = []
        for rule in grammar[key]:
            for k in keys:
                rule = rule.replace(k, keys[k])
            new_alt.append(rule)
        new_grammar[keys[key]] = new_alt
    return new_grammar

def convert_alternates(token):
    return token.split('|')

def convert_ebnf_parentheses(ebnf_grammar):
    """Convert a grammar in extended BNF to BNF"""
    grammar = extend_grammar(ebnf_grammar)
    for nonterminal in ebnf_grammar:
        expansions = ebnf_grammar[nonterminal]
        openP, closeP = None, None
        for i,e in enumerate(expansions):
            if '[(]' in e:
                openP = new_symbol(grammar)
                grammar[openP] = ['(']
                grammar[nonterminal][i] = grammar[nonterminal][i].replace('[(]', openP)
            if '[)]' in e:
                closeP = new_symbol(grammar)
                grammar[nonterminal][i] = grammar[nonterminal][i].replace('[)]', closeP)
                grammar[closeP] = [')']

        expansions = grammar[nonterminal]
        for i in range(len(expansions)):
            expansion = expansions[i]

            while True:
                parenthesized_exprs = parenthesized_expressions(expansion)
                if len(parenthesized_exprs) == 0:
                    break

                for expr in parenthesized_exprs:
                    operator = expr[-1:]
                    if operator not in '?+*':
                        operator = ''
                        contents = expr[1:-1]
                    else:
                        contents = expr[1:-2]

                    new_sym = new_symbol(grammar)
                    expansion = grammar[nonterminal][i].replace(
                        expr, new_sym + operator, 1)
                    grammar[nonterminal][i] = expansion
                    grammar[new_sym] = convert_alternates(contents)

    return grammar

def parenthesized_expressions(expansion):
    # In later chapters, we allow expansions to be tuples,
    # with the expansion being the first element
    if isinstance(expansion, tuple):
        expansion = expansion[0]

    return re.findall(RE_PARENTHESIZED_EXPR, expansion)

def new_symbol(grammar, symbol_name="<symbol>"):
    """Return a new symbol for `grammar` based on `symbol_name`"""
    if symbol_name not in grammar:
        return symbol_name

    count = 1
    while True:
        tentative_symbol_name = symbol_name[:-1] + "-" + repr(count) + ">"
        if tentative_symbol_name not in grammar:
            return tentative_symbol_name
        count += 1

def extend_grammar(grammar, extension={}):
    new_grammar = copy.deepcopy(grammar)
    new_grammar.update(extension)
    return new_grammar

def extended_nonterminals(expansion):
    # In later chapters, we allow expansions to be tuples,
    # with the expansion being the first element
    if isinstance(expansion, tuple):
        expansion = expansion[0]

    return re.findall(RE_EXTENDED_NONTERMINAL, expansion)

def convert_ebnf_operators(ebnf_grammar):
    """Convert a grammar in extended BNF to BNF"""
    grammar = extend_grammar(ebnf_grammar)
    for nonterminal in ebnf_grammar:
        expansions = ebnf_grammar[nonterminal]

        for i in range(len(expansions)):
            expansion = expansions[i]
            extended_symbols = extended_nonterminals(expansion)

            for extended_symbol in extended_symbols:
                operator = extended_symbol[-1:]
                original_symbol = extended_symbol[:-1]

                new_sym = new_symbol(grammar, original_symbol)
                grammar[nonterminal][i] = grammar[nonterminal][i].replace(
                    extended_symbol, new_sym, 1)

                if operator == '?':
                    grammar[new_sym] = ["", original_symbol]
                elif operator == '*':
                    grammar[new_sym] = ["", original_symbol + new_sym]
                elif operator == '+':
                    grammar[new_sym] = [
                        original_symbol, original_symbol + new_sym]

    return grammar

def convert_ebnf_grammar(ebnf_grammar):
    return convert_spaces(convert_ebnf_operators(convert_ebnf_parentheses(ebnf_grammar)))

if __name__ == '__main__':
    print(convert_spaces(convert_ebnf_parentheses({"<number>": ["<integer>(.<integer>)?"]})))
