import Tracer
SCOPES = {}

def to_key(name, num, method):
    return '%s:%s_%s' % (method, name, num)

class method__:
    def __init__(self, method):
        self.method = method
        if method not in SCOPES: SCOPES[method] = []

    def __enter__(self):
        SCOPES[self.method].append({})
        return self

    def __exit__(self, *args):
        SCOPES[self.method].pop()

class stack__:
    def __init__(self, name, num, method):
        self.stack_iter = SCOPES[method][-1]
        self.name, self.num, self.method = name, num, method
        self.prefix = to_key(self.method, self.name, self.num)

    def __enter__(self):
        self.stack_iter[self.prefix] = {}
        return self

    def __exit__(self, *args):
        del self.stack_iter[self.prefix]

class scope__:
    def __init__(self, name, num, method, alt):
        self.name, self.num, self.method, self.alt = name, num, method, alt
        kprefix = to_key(self.method, self.name, self.num)
        stack_iter = SCOPES[method][-1]
        self.scope_iter = stack_iter[kprefix]
        if self.alt not in self.scope_iter: self.scope_iter[self.alt] = 0

    def __enter__(self):
        # increment method and set current method
        uid = '+'.join([str(v) for k,v in self.scope_iter.items()])
        Tracer.trace_call('%s:%s_%s %s+%s' % (self.method, self.name, self.num, self.alt, uid))

    def __exit__(self, *args):
        #pop and set current method
        if self.name in {'while'}: self.scope_iter[self.alt] += 1
        Tracer.trace_return()

