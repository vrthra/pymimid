import Tracer
class scope:
    def __init__(self, name, alt):
        self.name, self.alt = name, alt

    def __enter__(self):
        # increment method and set current method
        Tracer.trace_call('%s %s' % (self.name, self.alt))

    def __exit__(self, *args):
        #pop and set current method
        Tracer.trace_return()

