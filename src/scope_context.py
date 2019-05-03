import Tracer
class scope:
    def __init__(self, name, num, method, scope_iter, alt):
        self.name, self.num, self.method, self.scope_iter, self.alt = name, num, method, scope_iter, alt
        self.key = '%s:%s_%s %s' % (self.method, self.name, self.num, self.alt)
        if self.key not in self.scope_iter: self.scope_iter[self.key] = 0

    def __enter__(self):
        # increment method and set current method
        prefix = '+'.join([str(i) for i in self.scope_iter.values()])
        Tracer.trace_call('%s:%s_%s %s+%s' % (self.method, self.name, self.num, self.alt, prefix))

    def __exit__(self, *args):
        #pop and set current method
        if self.name in {'while'}: self.scope_iter[self.key] += 1
        Tracer.trace_return()

