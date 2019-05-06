import Tracer

def to_key(method, name, num):
    return '%s:%s_%s' % (method, name, num)

class method__:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.stack = []
        return self

    def __exit__(self, *args):
        pass

class stack__:
    def __init__(self, name, num, method_i):
        self.method_stack = method_i.stack
        self.name, self.num, self.method = name, num, method_i.name
        self.prefix = to_key(self.method, self.name, self.num)

    def __enter__(self):
        if self.name in {'while'}:
            self.method_stack.append(0)
        elif self.name in {'if'}:
            self.method_stack.append('_')
        else:
            assert False
        return self

    def __exit__(self, *args):
        self.method_stack.pop()
import json
class scope__:
    def __init__(self, alt, stack_i, method_i):
        self.name, self.num, self.method, self.alt = stack_i.name, stack_i.num, stack_i.method, alt
        self.method_stack = method_i.stack

    def __enter__(self):
        if self.name in {'while'}:
            self.method_stack[-1] += 1
        elif self.name in {'if'}:
            pass
        else:
            assert False, self.name
        uid = json.dumps(self.method_stack)
        if self.name in {'while'}:
            Tracer.trace_call('%s:%s_%s %s' % (self.method, self.name, self.num, uid))
        else:
            Tracer.trace_call('%s:%s_%s %s+%s' % (self.method, self.name, self.num, self.alt, uid))
        return self

    def __exit__(self, *args):
        Tracer.trace_return()

