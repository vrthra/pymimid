MATCH_COMPLETE = True

class Regex:
    def __str__(self):
        if isinstance(self, Alt):
            #if self.star:
            #    return "(%s|)" % '|'.join(sorted(set([str(a) for a in self.arr])))
            #else:
                if len(self.arr) == 1:
                    return "%s" % '|'.join(sorted(set([str(a) for a in self.arr])))
                else:
                    return "(%s)" % '|'.join(sorted(set([str(a) for a in self.arr])))
        elif  isinstance(self, Rep):
            return "%s+" % self.a

        elif  isinstance(self, Seq):
            if len(self.arr) == 1:
                return "%s" % ''.join(str(a) for a in self.arr)
            else:
                return "(%s)" % ''.join(str(a) for a in self.arr)
        elif  isinstance(self, One):
            if len(self.o) == 1:
                return repr(self.o)
            return ''.join(str(o).replace('*', '[*]').replace('(', '[(]').replace(')', '[)]') for o in self.o)
        else:
            assert False

    def sub_match_regex(self, another_regex):
        if MATCH_COMPLETE:
            return str(self) == str(another_regex)
        # for submatch, not all alts need to match. But every thing else should
        # match.
        return self._sub_match_regex(another_regex)

class Rep(Regex):
    def __init__(self, a, count): self.a, self.count = a, count
    def __repr__(self): return "rep:(%s)*" % self.a

class Seq(Regex):
    def __init__(self, arr): self.arr = arr
    def __repr__(self): return "seq:(%s)" % ''.join([str(a) for a in self.arr if a])

    def _sub_match_regex(self, another):
        if isinstance(another, Alt):
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
        elif isinstance(another, Alt):
            if len(another.arr) != 1: return False
            for a in another.arr:
                if self.sub_match_regex(a):
                    return True
            return False
        else:
            return self.o == another.o

class Alt(Regex):
    def __init__(self, arr, star=0): self.arr, self.star = arr, star
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

#def token_to_regex(grammar, token):
#    if token not in grammar:
#        if token[0] + token[-1] == '<>':
#            return token
#        return repr(token)
#    definition = grammar[token]
#    if ':while_' in token:
#        return "%s" % alts_to_regex(grammar, definition)
#    elif ':if_' in token:
#        return alts_to_regex(grammar, definition)
#    elif is_method(token):
#        return token

#def rule_to_regex(grammar, rule):
#    return " ".join([token_to_regex(grammar, r) for r in rule])

#import string
#MIN_PATTERN_LEN = 4
#MIN_PATTERN_FRAC = 0.50
#def alts_to_regex(grammar, alts):
#    if len(alts) == 1:
#        return "%s" % "|".join(sorted(set([rule_to_regex(grammar, a) for a in alts])))
#    else:
#        r = set(len(a) for a in alts)
#        if r == {1}:
#            r = set(a[0] for a in alts)
#            t = {type(a) if a[0] != '<' and a[-1] != '>' else None for a in r}
#            if t == {str}:
#                no_esc_punct = set(list(string.punctuation)) - set("[]^-")
#                punct = "".join(no_esc_punct)
#                p_ = "-_\". +#()=/*:?,@!"
#                p = string.ascii_letters + string.digits + "-_\". +#()=/*:?,@!"
#                ops = "+-*/"
#                quotes = "\"'"
#                boxes = "[]{}()<>"
#                patterns = {
#                        "[0-9]": string.digits,
#                        "[a-z]": string.ascii_lowercase,
#                        "[A-Z]": string.ascii_uppercase,
#                        "[a-zA-Z]": string.ascii_letters,
#                        "[a-zA-Z0-9]": string.ascii_letters + string.digits,
#                        "[%s]" % ops : ops,
#                        "[%s]" % quotes : quotes,
#                        "[%s]" % boxes : boxes,
#                        "[%s]" % punct: punct,
#                        '[a-zA-Z0-9%s]' % p_: p
#                        }
#                for k in patterns:
#                    p  = set(list(patterns[k]))
#                    # do we hit at least 10%?
#                    if len(p) * MIN_PATTERN_FRAC < len(r):
#                        if p >= r and len(r) > MIN_PATTERN_LEN:
#                            return k
#                return "[%s]" % "".join(sorted(r))
#        return "(%s)" % "|".join(sorted(set([rule_to_regex(grammar, a) for a in alts])))

# def rule_to_regex(grammar, rule):
#     expr = []
#     for token in rule:
#         expr.append(token_to_regex(grammar, token))
#     return Seq(expr)

def alts_to_regex(grammar, alts, ctl_flow):
    expr = []
    for stuple in alts:
        expr.append(sequitur_tuple_to_regex(grammar, stuple, ctl_flow))
    return Alt(expr)

import pudb
br = pudb.set_trace

def if_to_regex(grammar, definition, token, ctl_flow):
    return alts_to_regex(grammar, definition, ctl_flow)

def while_to_regex(grammar, definition, token, ctl_flow):
    return alts_to_regex(grammar, definition, ctl_flow)


def sequitur_tuple_to_regex(grammar, s_token, ctl_flow=True):
    item, count = s_token
    if count == {1}:
        if isinstance(item, list):
            #br()
            arr = [sequitur_tuple_to_regex(grammar, t, ctl_flow) for t in item]
            return Seq(arr)
        else:
            assert isinstance(item, (str, dict))
            if ctl_flow:
                return token_to_regex(grammar, item, ctl_flow)
            else:
                return repr(item)
    else:
        if isinstance(item, list):
            #br()
            arr = [sequitur_tuple_to_regex(grammar, t, ctl_flow) for t in item]
            return Rep(Seq(arr), count=count)
        else:
            assert isinstance(item, (str, dict))
            return Rep(token_to_regex(grammar, item, ctl_flow), count=count)

def token_to_regex(grammar, token, ctl_flow=True):
    if isinstance(token, dict):
        #br()
        tokens = token['alternatives']
        arr = [token_to_regex(grammar, a, ctl_flow) for a in tokens]
        return Alt(arr, ctl_flow)
    else:
        definition = grammar.get(token, None)
        if definition is None:
            return One(token)
        elif ':while_' in token:
            #br()
            return while_to_regex(grammar, definition, token, ctl_flow)
        elif ':if_' in token:
            #br()
            return if_to_regex(grammar, definition, token, ctl_flow)
        else:
            return One(token)
