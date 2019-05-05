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
            assert not isinstance(self.o, Regex)
            yield self.o
        else:
            assert False

    def __str__(self):
        if isinstance(self, Alt):
            return "(%s|%s)" % (str(self.a1), str(self.a2))
        if isinstance(self, Altz):
            return "(%s)" % '|'.join(str(a) for a in self.arr)
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

    def sub_match_regex(self, another_regex):
        # for submatch, not all alts need to match. But every thing else should
        # match.
        return self._sub_match_regex(another_regex)

class Alt(Regex):
    def __init__(self, a1, a2): self.a1, self.a2 = a1, a2
    def __repr__(self): return "alt:(%s|%s)" % (self.a1, self.a2)


class Rep(Regex):
    def __init__(self, a): self.a = a
    def __repr__(self): return "rep:(%s)*" % self.a

class Seq(Regex):
    def __init__(self, arr): self.arr = arr
    def __repr__(self): return "seq:(%s)" % ''.join([str(a) for a in self.arr if a])

    def _sub_match_regex(self, another):
        if isinstance(another, Altz):
            if not len(another.arr) == 1: return False
            for a in another.arr:
                if self.sub_match_regex(a):
                    return True
            return False
        elif isinstance(another, One):
            if len(self.arr) != 1:
                return False
            else:
                return self.arr[0].sub_match_regex(another)
        else:
            if len(self.arr) != len(another.arr):
                return False
            for a1, a2 in zip(self.arr, another.arr):
                if not a1.sub_match_regex(a2):
                    return False
            return True


class One(Regex):
    def __init__(self, o): self.o = o
    def __repr__(self): return "one:(%s)" % (str(self.o) if self.o else '')

    def _sub_match_regex(self, another):
        if isinstance(another, Seq):
            if len(another.arr) != 1:
                return False
            return self.sub_match_regex(another.arr[0])
        elif isinstance(another, Altz):
            if len(another.arr) != 1: return False
            for a in another.arr:
                if self.sub_match_regex(a):
                    return True
            return False
        else:
            return self.o == another.o

class Altz(Regex):
    def __init__(self, arr): self.arr = arr
    def __repr__(self): return "altz:(%s)" % '|'.join([str(a) for a in self.arr])

    def _sub_match_regex(self, another):
        if isinstance(another, Seq):
            for a in self.arr:
                if a.sub_match_regex(another):
                    return True
            return False
        elif isinstance(another, One):
            for a in self.arr:
                if a.sub_match_regex(another):
                    return True
            return False
        else:
            for b in another.arr:
                br = True
                for a in self.arr:
                    if a.sub_match_regex(b):
                        br = False
                if br:
                    return False
            return True


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

import string
def alts_to_regex(grammar, alts):
    if len(alts) == 1:
        return "%s" % "|".join(sorted(set([rule_to_regex(grammar, a) for a in alts])))
    else:
        r = set(len(a) for a in alts)
        if r == {1}:
            r = set(a[0] for a in alts)
            t = {type(a) for a in r}
            if t == {str}:
                patterns = {
                        "[0-9]": string.digits,
                        "[a-z]": string.ascii_lowercase,
                        "[A-Z]": string.ascii_uppercase,
                        "[a-zA-Z]": string.ascii_letters,
                        "[a-zA-Z0-9]": string.ascii_letters + string.digits,
                        '[-a-zA-Z0-9_". +#()=/*:?,@!]': string.ascii_letters + string.digits + '_". +-#()=/*:?,@!',
                        }
                for k in patterns:
                    p  = set(list(patterns[k]))
                    if p > r:
                        return k
                ascii_lower =  set(list(string.ascii_lowercase))
        return "(%s)" % "|".join(sorted(set([rule_to_regex(grammar, a) for a in alts])))

def rule_to_regexz(grammar, rule):
    expr = []
    for token in rule:
        expr.append(token_to_regexz(grammar, token))
    return Seq(expr)

def alts_to_regexz(grammar, alts):
    expr = []
    for rule in alts:
        expr.append(rule_to_regexz(grammar, rule))
    return Altz(expr)

def token_to_regexz(grammar, token):
    definition = grammar.get(token, None)
    if definition is None:
        return One(token)
    elif ':while_' in token:
        return alts_to_regexz(grammar, definition)
    elif ':if_' in token:
        return alts_to_regexz(grammar, definition)
    else:
        return One(token)
