import sys, imp
#import parse_ # does not have the .in_ construction for taints.
parse_ = imp.new_module('parse_')

def init_module(src):
    with open(src) as sf:
        exec(sf.read(), parse_.__dict__)

exec_map = {}
def check(s, label=None):
    if s in exec_map: return exec_map[s]
    v =  _check(s)
    #print("\t\t", repr(s), v, ' from: %s' % str(label))
    exec_map[s] = v
    return v

def _check(s):
    try:
        parse_.main(s)
        return True
    except:
        return False
