class Symbol:
    def __init__(self, grammar):
        self.grammar, self.next, self.prev = grammar, None, None

    def print_terminal(self):
        return self.value()

    def print_rule(self, _):
        return self.print_terminal()

    @staticmethod
    def factory(grammar, value):
        if isinstance(value, str):
            return Terminal(grammar, value)
        elif isinstance(value, Terminal):
            return Terminal(grammar, value.terminal)
        elif isinstance(value, NonTerminal):
            return NonTerminal(grammar, value.rule)
        elif isinstance(value, Rule):
            return NonTerminal(grammar, value)
        else:
            raise "type(value) == %s" % type(value)

    @staticmethod
    def guard(grammar, value):
        return Guard(grammar, value)

    def join(self, right):
        """
        Links two symbols together, removing any old digram from the hash table.
        """
        if (self.next):
            self.delete_digram()

            """
            This is to deal with triples, where we only record the second
            pair of overlapping digrams. When we delete the second pair,
            we insert the first pair into the hash table so that we don't
            forget about it. e.g. abbbabcbb
            """

            if ((right.prev is not None) and (right.next is not None) and
                right.value() == right.prev.value() and
                right.value() == right.next.value()):
                self.grammar.add_index(right)
            if ((self.prev is not None) and (self.next is not None) and
                self.value() == self.next.value() and
                self.value() == self.prev.value()):
                self.grammar.add_index(self)
        self.next = right
        right.prev = self

    def delete_digram(self):
        """Removes the digram from the hash table"""
        if (self.is_guard() or self.next.is_guard()):
            pass
        else:
            self.grammar.clear_index(self)

    def insert_after(self, symbol):
        """Inserts a symbol after this one"""
        symbol.join(self.next)
        self.join(symbol)

    def is_guard(self): return False # Overridden by Guard class

    def expand(self):
        """
        This symbol is the last reference to its rule. It is deleted, and the
        contents of the rule substituted in its place.
        """
        left = self.prev
        right = self.next
        first = self.rule.first()
        last = self.rule.last()

        self.grammar.clear_index(self)
        left.join(first)
        last.join(right)
        self.grammar.add_index(last)

    def propagate_change(self):
        if self.is_guard() or self.next.is_guard():
            if (self.next.is_guard() or self.next.next.is_guard()):
                return
            match = self.grammar.get_index(self.next)
            if not match:
                self.grammar.add_index(self.next)
            elif match.next != self.next:
                self.next.process_match(match)
        else:
            match = self.grammar.get_index(self)
            if not match:
                self.grammar.add_index(self)
                if (self.next.is_guard() or self.next.next.is_guard()):
                    return
                match = self.grammar.get_index(self.next)
                if not match:
                    self.grammar.add_index(self.next)
                elif match.next != self.next:
                    self.next.process_match(match)
            elif match.next != self:
                self.process_match(match)

    def substitute(self, rule):
        """Replace a digram with a non-terminal"""
        prev = self.prev
        prev.next.delete()
        prev.next.delete()
        prev.insert_after(Symbol.factory(self.grammar, rule))

    def process_match(self, match):
        """Deal with a matching digram"""
        rule = None
        if (match.prev.is_guard() and match.next.next.is_guard()):
            # reuse an existing rule
            rule = match.prev.rule
            self.substitute(rule)
            self.prev.propagate_change()
        else:
            # create a new rule
            rule = Rule(self.grammar)
            rule.last().insert_after(Symbol.factory(self.grammar, self))
            rule.last().insert_after(Symbol.factory(self.grammar, self.next))
            self.grammar.add_index(rule.first())

            match.substitute(rule)
            match.prev.propagate_change()
            self.substitute(rule)
            self.prev.propagate_change()

        # Check for an under-used rule
        if (NonTerminal == type(rule.first()) and (rule.first().rule.reference_count == 1)):
            rule.first().expand()

    def value(self):
        return (self.rule.unique_number if self.rule else self.terminal)

    def string_value(self):
        if self.rule:
            return "rule: %d" % self.rule.unique_number
        else:
            return self.terminal

    def hash_value(self):
        return "%s+%s" % (self.string_value(), self.next.string_value())


class Terminal(Symbol):
    def __init__(self, grammar, terminal):
        super(Terminal, self).__init__(grammar)
        self.terminal = terminal

    def value(self):
        return self.terminal
    string_value = value

    def delete(self):
        """
        Cleans up for symbol deletion: removes hash table entry and decrements
        rule reference count.
        """
        self.prev.join(self.next)
        self.delete_digram()


class NonTerminal(Symbol):
    def __init__(self, grammar, rule):
        super(NonTerminal, self).__init__(grammar)
        self.rule = rule
        self.rule.increment_reference_count()

    def value(self):
        return self.rule.unique_number

    def string_value(self):
        return "rule: %d" % self.rule.unique_number

    def print_rule(self, rule_set):
        if (self.rule in rule_set):
            rule_index = rule_set.index(self.rule)
        else:
            rule_index = len(rule_set)
            rule_set.append(self.rule)
        return "<%d>" % rule_index

    def delete(self):
        """
        Cleans up for symbol deletion: removes hash table entry and decrements
        rule reference count.
        """
        self.prev.join(self.next)
        self.delete_digram()
        self.rule.decrement_reference_count()

class Guard(Symbol):
    """
    The guard symbol in the linked list of symbols that make up the rule.
    It points forward to the first symbol in the rule, and backwards to the last
    symbol in the rule. Its own value points to the rule data structure, so that
    symbols can find out which rule they're in.
    """

    def __init__(self, grammar, rule):
        super(Guard, self).__init__(grammar)
        self.rule = rule

    def is_guard(self): return True

    def value(self):
        return self.rule.unique_number

    def string_value(self):
        return "rule: %d" % self.rule.unique_number

    def delete(self):
        """
        Cleans up for symbol deletion: removes hash table entry and decrements
        rule reference count.
        """
        self.prev.join(self.next)

class Rule:

    unique_rule_number = 1

    def __init__(self, grammar):
        self.guard = Symbol.guard(grammar, self)
        self.guard.join(self.guard)
        self.reference_count = 0
        self.unique_number = Rule.unique_rule_number
        Rule.unique_rule_number += 1

    def first(self): return self.guard.next

    def last(self): return self.guard.prev

    def increment_reference_count(self): self.reference_count += 1

    def decrement_reference_count(self): self.reference_count -= 1

    def print_rule(self, rule_set):
        buf = []
        symbol = self.first()
        while not symbol.is_guard():
            buf.append(symbol.print_rule(rule_set))
            symbol = symbol.next
        return buf

class Grammar:
    def __init__(self):
        self.digram_index = {}
        self.root_production = Rule(self)

    def train_string(self, input_sequence):
        if (0 < len(input_sequence)):
            self.root_production.last().insert_after(Symbol.factory(self, input_sequence.pop(0)))
        while (0 < len(input_sequence)):
            self.root_production.last().insert_after(Symbol.factory(self, input_sequence.pop(0)))
            match = self.get_index(self.root_production.last().prev)
            if not match:
                self.add_index(self.root_production.last().prev)
            elif match.next != self.root_production.last().prev:
                self.root_production.last().prev.process_match(match)

    def add_index(self, digram):
        self.digram_index[digram.hash_value()] = digram

    def get_index(self, digram):
        return self.digram_index.get(digram.hash_value())

    def clear_index(self, digram):
        if self.digram_index.get(digram.hash_value()) == digram:
            self.digram_index[digram.hash_value()] = None

    def get_grammar(self):
        rule_set = [self.root_production]
        g = {}
        for i,rule in enumerate(rule_set):
            g["<%d>" % i] = rule.print_rule(rule_set)
        return g

    def count_tokens(self, rule):
        res = []
        for t in rule:
            if not res:
                res.append([t, 1])
            else:
                if res[-1][0] == t:
                    res[-1][1] += 1
                else:
                    res.append([t, 1])
        return res


    def counter(self, g):
        g_ = {}
        for k in g:
            alts = []
            a = self.count_tokens(g[k])
            g_[k] = a
        return g_

    def seq_to_flat(self, seq, g):
        my_seq = []
        for s in seq:
            token, count = s
            seq_, count_ = self.token_to_flat(token, g)
            my_seq.append((seq_, count * count_))
        return (my_seq, 1)

    def token_to_flat(self, token, g):
        if (token[0], token[-1]) != ('<', '>'):
            return (token, 1)
        rule = g[token]
        if len(rule) == 1:
            t, count = rule[0]
            t_, count_ = self.token_to_flat(t, g)
            return (t_, count*count_)
        else:
            return self.seq_to_flat(rule, g)

    def g_to_flat(self, g):
        return self.token_to_flat('<0>', g)

    def flatten(self):
        g = self.get_grammar()
        c = self.counter(g) 
        r = self.g_to_flat(c)
        return r

