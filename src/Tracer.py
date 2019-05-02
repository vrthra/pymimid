from InformationFlow import ctstr

CURRENT_METHOD = None
METHOD_NUM_STACK = []
METHOD_MAP = {}
METHOD_NUM = 0

def get_current_method():
    return CURRENT_METHOD

def set_current_method(method, stack_depth, mid):
    global CURRENT_METHOD
    CURRENT_METHOD = (method, stack_depth, mid)
    return CURRENT_METHOD

def trace_init():
    global CURRENT_METHOD
    global METHOD_NUM_STACK
    global METHOD_MAP
    global METHOD_NUM
    CURRENT_METHOD = None
    METHOD_NUM_STACK.clear()
    METHOD_MAP.clear()
    METHOD_NUM = 0

    start = (METHOD_NUM, None, [])
    METHOD_NUM_STACK.append(start)
    METHOD_MAP[METHOD_NUM] = start

def trace_call(method):
    global CURRENT_METHOD
    global METHOD_NUM_STACK
    global METHOD_MAP
    global METHOD_NUM
    METHOD_NUM += 1

    # create our method invocation
    # method_num, method_name, children
    n = (METHOD_NUM, method, [])
    METHOD_MAP[METHOD_NUM] = n
    # add ourselves as one of the children to the previous method invocation
    METHOD_NUM_STACK[-1][2].append(n)
    # and set us as the current method.
    METHOD_NUM_STACK.append(n)

def trace_return():
    METHOD_NUM_STACK.pop()

def trace_set_method(method):
    set_current_method(method, len(METHOD_NUM_STACK), METHOD_NUM_STACK[-1][0])

class xtstr(ctstr):
    def add_instr(self, op, c_a, c_b):
        ct = None
        if len(c_a) == 1 and isinstance(c_a, xtstr):
            ct = c_a.taint[0]
        elif len(c_b) == 1 and isinstance(c_b, xtstr):
            ct = c_b.taint[0]
        m = get_current_method()
        #print(repr(m))
        self.comparisons.append((ct, m))

    def create(self, res, taint):
        o = xtstr(res, taint, self)
        o.comparisons = self.comparisons
        return o

class Context:
    def __init__(self, frame, track_caller=True):
        self.method = frame.f_code.co_name
        self.file_name = frame.f_code.co_filename
        self.parent = Context(frame.f_back, False) if track_caller and frame.f_back else None

import sys
class Tracer:
    def __enter__(self):
        self.oldtrace = sys.gettrace()
        sys.settrace(self.trace_event)
        return self

    def __exit__(self, *args):
        sys.settrace(self.oldtrace)

    def __call__(self): return self.inputstr

    def __init__(self, inputstr, restrict={}):
        global METHOD_NUM
        self.inputstr = xtstr(inputstr, parent=None).with_comparisons([])
        self.trace = []
        self.restrict = restrict

        trace_init()
        # method_num, method_name, children

    def tracing_context(self, cxt, event, arg):
        if self.restrict.get('files'):
            return any(cxt.file_name.endswith(f) for f in self.restrict['files'])
        if self.restrict.get('methods'):
            return cxt.method in self.restrict['methods']
        return True

    def trace_event(self, frame, event, arg):
        cxt = Context(frame)
        if not self.tracing_context(cxt, event, arg): return self.trace_event
        self.on_event(event, arg, cxt)
        return self.trace_event

    @property
    def method_map(self):
        return METHOD_MAP

    def on_event(self, event, arg, cxt):
        global METHOD_NUM
        # make it tree
        self.trace.append((event, cxt))
        if event == 'call':
            trace_call(cxt.method)
        elif event == 'return':
            trace_return()
        trace_set_method(cxt.method)

def convert_comparisons(comparisons):
    light_comparisons = []
    for idx, (method, stack_depth, mid) in comparisons:
        if idx is None: continue
        light_comparisons.append((idx, mid))
    return light_comparisons

def convert_method_map(method_map):
    light_map = {}
    for k in method_map:
        method_num, method_name, children = method_map[k]
        light_map[k] = (k, method_name, [c[0] for c in children])
    return light_map
