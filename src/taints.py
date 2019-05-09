#!/usr/bin/env python3

import inspect
import enum

def my_calculator(my_input):
    result = eval(my_input, {}, {})
    print("The result of %s was %d" % (my_input, result))


class tstr_(str):
    def __new__(cls, value, *args, **kw):
        return super(tstr_, cls).__new__(cls, value)

class tstr(tstr_):
    def __init__(self, value, taint=None, parent=None, **kwargs):
        self.parent = parent
        l = len(self)
        if taint is None:
            taint = 0
        self.taint = list(range(taint, taint + l)) if isinstance(
            taint, int) else taint
        assert len(self.taint) == l

    def __repr__(self):
        return self

    def __str__(self):
        return str.__str__(self)

class tstr(tstr):
    def untaint(self):
        self.taint = [None] * len(self)
        return self

    def has_taint(self):
        return any(True for i in self.taint if i is not None)

    def taint_in(self, gsentence):
        return set(self.taint) <= set(gsentence.taint)



class tstr(tstr):
    def create(self, res, taint):
        return tstr(res, taint, self)



class tstr(tstr):
    def __getitem__(self, key):
        res = super().__getitem__(key)
        if isinstance(key, int):
            key = len(self) + key if key < 0 else key
            return self.create(res, [self.taint[key]])
        elif isinstance(key, slice):
            return self.create(res, self.taint[key])
        else:
            assert False

class tstr(tstr):
    def __iter__(self):
        return tstr_iterator(self)

class tstr_iterator():
    def __init__(self, tstr):
        self._tstr = tstr
        self._str_idx = 0

    def __next__(self):
        if self._str_idx == len(self._tstr):
            raise StopIteration
        # calls tstr getitem should be tstr
        c = self._tstr[self._str_idx]
        assert isinstance(c, tstr)
        self._str_idx += 1
        return c

class tstr(tstr):
    def __add__(self, other):
        if isinstance(other, tstr):
            return self.create(str.__add__(self, other),
                               (self.taint + other.taint))
        else:
            return self.create(str.__add__(self, other),
                               (self.taint + [-1 for i in other]))

class tstr(tstr):
    def __radd__(self, other):
        taint = other.taint if isinstance(other, tstr) else [
            None for i in other]
        return self.create(str.__add__(other, self), (taint + self.taint))

class tstr(tstr):
    class TaintException(Exception):
        pass

    def x(self, i=0):
        if not self.taint:
            raise taint.TaintException('Invalid request idx')
        if isinstance(i, int):
            return [self[p]
                    for p in [k for k, j in enumerate(self.taint) if j == i]]
        elif isinstance(i, slice):
            r = range(i.start or 0, i.stop or len(self), i.step or 1)
            return [self[p]
                    for p in [k for k, j in enumerate(self.taint) if j in r]]

class tstr(tstr):
    def replace(self, a, b, n=None):
        old_taint = self.taint
        b_taint = b.taint if isinstance(b, tstr) else [None] * len(b)
        mystr = str(self)
        i = 0
        while True:
            if n and i >= n:
                break
            idx = mystr.find(a)
            if idx == -1:
                break
            last = idx + len(a)
            mystr = mystr.replace(a, b, 1)
            partA, partB = old_taint[0:idx], old_taint[last:]
            old_taint = partA + b_taint + partB
            i += 1
        return self.create(mystr, old_taint)

class tstr(tstr):
    def _split_helper(self, sep, splitted):
        result_list = []
        last_idx = 0
        first_idx = 0
        sep_len = len(sep)

        for s in splitted:
            last_idx = first_idx + len(s)
            item = self[first_idx:last_idx]
            result_list.append(item)
            first_idx = last_idx + sep_len
        return result_list

    def _split_space(self, splitted):
        result_list = []
        last_idx = 0
        first_idx = 0
        sep_len = 0
        for s in splitted:
            last_idx = first_idx + len(s)
            item = self[first_idx:last_idx]
            result_list.append(item)
            v = str(self[last_idx:])
            sep_len = len(v) - len(v.lstrip(' '))
            first_idx = last_idx + sep_len
        return result_list

    def rsplit(self, sep=None, maxsplit=-1):
        splitted = super().rsplit(sep, maxsplit)
        if not sep:
            return self._split_space(splitted)
        return self._split_helper(sep, splitted)

    def split(self, sep=None, maxsplit=-1):
        splitted = super().split(sep, maxsplit)
        if not sep:
            return self._split_space(splitted)
        return self._split_helper(sep, splitted)

class tstr(tstr):
    def strip(self, cl=None):
        return self.lstrip(cl).rstrip(cl)

    def lstrip(self, cl=None):
        res = super().lstrip(cl)
        i = self.find(res)
        return self[i:]

    def rstrip(self, cl=None):
        res = super().rstrip(cl)
        return self[0:len(res)]


class tstr(tstr):
    def expandtabs(self, n=8):
        parts = self.split('\t')
        res = super().expandtabs(n)
        all_parts = []
        for i, p in enumerate(parts):
            all_parts.extend(p.taint)
            if i < len(parts) - 1:
                l = len(all_parts) % n
                all_parts.extend([p.taint[-1]] * l)
        return self.create(res, all_parts)

class tstr(tstr):
    def join(self, iterable):
        mystr = ''
        mytaint = []
        sep_taint = self.taint
        lst = list(iterable)
        for i, s in enumerate(lst):
            staint = s.taint if isinstance(s, tstr) else [None] * len(s)
            mytaint.extend(staint)
            mystr += str(s)
            if i < len(lst) - 1:
                mytaint.extend(sep_taint)
                mystr += str(self)
        res = super().join(iterable)
        assert len(res) == len(mystr)
        return self.create(res, mytaint)

class tstr(tstr):
    def partition(self, sep):
        partA, sep, partB = super().partition(sep)
        return (self.create(partA, self.taint[0:len(partA)]),
                self.create(sep, self.taint[len(partA):len(partA) + len(sep)]),
                self.create(partB, self.taint[len(partA) + len(sep):]))

    def rpartition(self, sep):
        partA, sep, partB = super().rpartition(sep)
        return (self.create(partA, self.taint[0:len(partA)]),
                self.create(sep, self.taint[len(partA):len(partA) + len(sep)]),
                self.create(partB, self.taint[len(partA) + len(sep):]))

class tstr(tstr):
    def ljust(self, width, fillchar=' '):
        res = super().ljust(width, fillchar)
        initial = len(res) - len(self)
        if isinstance(fillchar, tstr):
            t = fillchar.x()
        else:
            t = -1
        return self.create(res, [t] * initial + self.taint)

    def rjust(self, width, fillchar=' '):
        res = super().rjust(width, fillchar)
        final = len(res) - len(self)
        if isinstance(fillchar, tstr):
            t = fillchar.x()
        else:
            t = -1
        return self.create(res, self.taint + [t] * final)

class tstr(tstr):
    def swapcase(self):
        return self.create(str(self).swapcase(), self.taint)

    def upper(self):
        return self.create(str(self).upper(), self.taint)

    def lower(self):
        return self.create(str(self).lower(), self.taint)

    def capitalize(self):
        return self.create(str(self).capitalize(), self.taint)

    def title(self):
        return self.create(str(self).title(), self.taint)

def taint_include(gword, gsentence):
    return set(gword.taint) <= set(gsentence.taint)


def make_str_wrapper(fun):
    def proxy(*args, **kwargs):
        res = fun(*args, **kwargs)
        return res
    return proxy

import types
tstr_members = [name for name, fn in inspect.getmembers(tstr, callable)
                if isinstance(fn, types.FunctionType) and fn.__qualname__.startswith('tstr')]

for name, fn in inspect.getmembers(str, callable):
    if name not in set(['__class__', '__new__', '__str__', '__init__',
                        '__repr__', '__getattribute__']) | set(tstr_members):
        setattr(tstr, name, make_str_wrapper(fn))


def make_str_abort_wrapper(fun):
    def proxy(*args, **kwargs):
        raise tstr.TaintException('%s Not implemented in TSTR' % fun.__name__)
    return proxy



class eoftstr(tstr):
    def create(self, res, taint):
        return eoftstr(res, taint, self)

    def __getitem__(self, key):
        def get_interval(key):
            return ((0 if key.start is None else key.start),
                    (len(res) if key.stop is None else key.stop))

        res = super().__getitem__(key)
        if isinstance(key, int):
            key = len(self) + key if key < 0 else key
            return self.create(res, [self.taint[key]])
        elif isinstance(key, slice):
            if res:
                return self.create(res, self.taint[key])
            # Result is an empty string
            t = self.create(res, self.taint[key])
            key_start, key_stop = get_interval(key)
            cursor = 0
            if key_start < len(self):
                assert key_stop < len(self)
                cursor = self.taint[key_stop]
            else:
                if len(self) == 0:
                    # if the original string was empty, we assume that any
                    # empty string produced from it should carry the same
                    # taint.
                    cursor = self.x()
                else:
                    # Key start was not in the string. We can reply only
                    # if the key start was just outside the string, in
                    # which case, we guess.
                    if key_start != len(self):
                        raise tstr.TaintException('Can\'t guess the taint')
                    cursor = self.taint[len(self) - 1] + 1
            # _tcursor gets created only for empty strings.
            t._tcursor = cursor
            return t

        else:
            assert False

class eoftstr(eoftstr):
    def t(self, i=0):
        if self.taint:
            return self.taint[i]
        else:
            if i != 0:
                raise tstr.TaintException('Invalid request idx')
            # self._tcursor gets created only for empty strings.
            # use the exception to determine which ones need it.
            return self._tcursor

class Op(enum.Enum):
    LT = 0
    LE = enum.auto()
    EQ = enum.auto()
    NE = enum.auto()
    GT = enum.auto()
    GE = enum.auto()
    IN = enum.auto()
    NOT_IN = enum.auto()
    IS = enum.auto()
    IS_NOT = enum.auto()
    FIND_STR = enum.auto()

COMPARE_OPERATORS = {
    Op.EQ: lambda x, y: x == y,
    Op.NE: lambda x, y: x != y,
    Op.IN: lambda x, y: x in y,
    Op.NOT_IN: lambda x, y: x not in y,
    Op.FIND_STR: lambda x, y: x.find(y)
}

Comparisons = []

# ### Instructions

class Instr:
    def __init__(self, o, a, b):
        self.opA = a
        self.opB = b
        self.op = o

    def o(self):
        if self.op == Op.EQ:
            return 'eq'
        elif self.op == Op.NE:
            return 'ne'
        else:
            return '?'

    def opS(self):
        if not self.opA.has_taint() and isinstance(self.opB, tstr):
            return (self.opB, self.opA)
        else:
            return (self.opA, self.opB)

    @property
    def op_A(self):
        return self.opS()[0]

    @property
    def op_B(self):
        return self.opS()[1]

    def __repr__(self):
        return "%s,%s,%s" % (self.o(), repr(self.opA), repr(self.opB))

    def __str__(self):
        if self.op == Op.EQ:
            if str(self.opA) == str(self.opB):
                return "%s = %s" % (repr(self.opA), repr(self.opB))
            else:
                return "%s != %s" % (repr(self.opA), repr(self.opB))
        elif self.op == Op.NE:
            if str(self.opA) == str(self.opB):
                return "%s = %s" % (repr(self.opA), repr(self.opB))
            else:
                return "%s != %s" % (repr(self.opA), repr(self.opB))
        elif self.op == Op.IN:
            if str(self.opA) in str(self.opB):
                return "%s in %s" % (repr(self.opA), repr(self.opB))
            else:
                return "%s not in %s" % (repr(self.opA), repr(self.opB))
        elif self.op == Op.NOT_IN:
            if str(self.opA) in str(self.opB):
                return "%s in %s" % (repr(self.opA), repr(self.opB))
            else:
                return "%s not in %s" % (repr(self.opA), repr(self.opB))
        else:
            assert False


class ctstr(eoftstr):
    def create(self, res, taint):
        o = ctstr(res, taint, self)
        o.comparisons = self.comparisons
        return o

    def add_instr(self, op, c_a, c_b):
        self.comparisons.append(Instr(op, c_a, c_b))

    def with_comparisons(self, comparisons):
        self.comparisons = comparisons
        return self

class ctstr(ctstr):
    def __eq__(self, other):
        if len(self) == 0 and len(other) == 0:
            self.add_instr(Op.EQ, self, other)
            return True
        elif len(self) == 0:
            self.add_instr(Op.EQ, self, other[0])
            return False
        elif len(other) == 0:
            self.add_instr(Op.EQ, self[0], other)
            return False
        elif len(self) == 1 and len(other) == 1:
            self.add_instr(Op.EQ, self, other)
            return super().__eq__(other)
        else:
            if not self[0] == other[0]:
                return False
            return self[1:] == other[1:]

class ctstr(ctstr):
    def __ne__(self, other):
        return not self.__eq__(other)

class ctstr(ctstr):
    def __contains__(self, other):
        self.add_instr(Op.IN, self, other)
        return super().__contains__(other)

class ctstr(ctstr):
    def find(self, sub, start=None, end=None):
        if start is None:
            start_val = 0
        else:
            start_val = start
        if end is None:
            end_val = len(self)
        else:
            end_val = end
        self.add_instr(Op.IN, self[start_val:end_val], sub)
        return super().find(sub, start, end)

class ctstr(ctstr):
    def rfind(self, sub, start=None, end=None):
        if start is None:
            start_val = 0
        else:
            start_val = start
        if end is None:
            end_val = len(self)
        else:
            end_val = end
        self.add_instr(Op.IN, self[start_val:end_val], sub)
        return super().find(sub, start, end)

class ctstr(ctstr):
    def startswith(self, s, beg =0,end=None):
        if end == None:
            end = len(self)
        self == s[beg:end]
        return super().startswith(s, beg, end)


def substrings(s, l):
    for i in range(len(s) - (l - 1)):
        yield s[i:i + l]

class ctstr(ctstr):
    def in_(self, s):
        if isinstance(s, str):
            # c in '0123456789'
            # to
            # __fn(c).in_('0123456789')
            # ensure that all characters are compared
            result = [self == c for c in substrings(s, len(self))]
            return any(result)
        else:
            for item in s:
                if self == item:
                    return True
            return False

class ctstr(ctstr):
    def split(self, sep=None, maxsplit=-1):
        self.add_instr(Op.IN, self, sep)
        return super().split(sep, maxsplit)
