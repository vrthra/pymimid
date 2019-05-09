#!/usr/bin/env python3

# Rewrites the Python source file given so that
# 1) All `a in b` are transformed to a.in_(b)
# 2) All while conditions are transformed to have a with scope(): at the top
# 3) All if conditions are transformed to have a with scope(): at the top

import ast
import astor

if_counter = None
while_counter = None
methods = []

class InRewriter(ast.NodeTransformer):
    def wrap(self, node):
        return ast.Call(func=ast.Name(id='taint_wrap__', ctx=ast.Load()), args=[node], keywords=[])

    def visit_Compare(self, tree_node):
        left = tree_node.left
        if not tree_node.ops or not isinstance(tree_node.ops[0], ast.In):
            return tree_node
        mod_val = ast.Call(
            func=ast.Attribute(
                value=self.wrap(left),
                attr='in_'),
            args=tree_node.comparators,
            keywords=[])
        return mod_val

class Rewriter(InRewriter):
    def wrap_in_method(self, body):
        method_name_expr = ast.Str(methods[-1])
        args = [method_name_expr]
        scope_expr = ast.Call(func=ast.Name(id='method__', ctx=ast.Load()), args=args, keywords=[])
        return [ast.With(items=[ast.withitem(scope_expr, ast.Name(id='_method__'))], body=body)]

    def wrap_in_outer(self, name, can_empty, counter, node):
        name_expr = ast.Str(name)
        can_empty_expr = ast.Str(can_empty)
        counter_expr = ast.Num(counter)
        method_id = ast.Name(id='_method__')
        args = [name_expr, counter_expr, method_id, can_empty_expr]
        scope_expr = ast.Call(func=ast.Name(id='stack__', ctx=ast.Load()),
                args=args, keywords=[])
        return ast.With(items=[ast.withitem(scope_expr, ast.Name(id='%s_%d_stack__' % (name, counter)))], body=[node])

    def wrap_in_inner(self, name, counter, val, body):
        val_expr = ast.Num(val)
        stack_iter = ast.Name(id='%s_%d_stack__' % (name, counter))
        method_id = ast.Name(id='_method__')
        args = [val_expr, stack_iter, method_id]
        scope_expr = ast.Call(func=ast.Name(id='scope__', ctx=ast.Load()),
                args=args, keywords=[])
        return [ast.With(items=[ast.withitem(scope_expr, ast.Name(id='%s_%d_%d_scope__' % (name, counter, val)))], body=body)]



    def visit_FunctionDef(self, tree_node):
        global while_counter, if_counter
        while_counter = 0
        if_counter = 0
        methods.append(tree_node.name)
        self.generic_visit(tree_node)
        while_counter = 0
        tree_node.body = self.wrap_in_method(tree_node.body)
        return tree_node

    def process_if(self, tree_node, counter, val=None):
        if val is None: val = 0
        else: val += 1
        if_body = []
        self.generic_visit(tree_node.test)
        for node in tree_node.body: self.generic_visit(node)
        tree_node.body = self.wrap_in_inner('if', counter, val, tree_node.body)

        # else part.
        if len(tree_node.orelse) == 1 and isinstance(tree_node.orelse[0], ast.If):
            self.process_if(tree_node.orelse[0], counter, val)
        else:
            if tree_node.orelse:
                val += 1
                for node in tree_node.orelse: self.generic_visit(node)
                tree_node.orelse = self.wrap_in_inner('if', counter, val, tree_node.orelse)


    def visit_If(self, tree_node):
        global if_counter
        if_counter += 1
        counter = if_counter
        #is it empty
        start = tree_node
        while start:
            if isinstance(start, ast.If):
                if not start.orelse:
                    start = None
                elif len(start.orelse) == 1:
                    start = start.orelse[0]
                else:
                    break
            else:
                break
        self.process_if(tree_node, counter=if_counter)
        can_empty = '+' if start else '*'
        return self.wrap_in_outer('if', can_empty, counter, tree_node)


    def visit_While(self, tree_node):
        self.generic_visit(tree_node)
        global while_counter
        while_counter += 1
        counter = while_counter
        test = tree_node.test
        body = tree_node.body
        assert not tree_node.orelse
        tree_node.body = self.wrap_in_inner('while', counter, 0, body)
        return self.wrap_in_outer('while', '?', counter, tree_node)

def rewrite_in(src, original):
    v = ast.fix_missing_locations(InRewriter().visit(ast.parse(src)))
    header="""
import string
    """
    print(header)
    print(astor.to_source(v))

def rewrite(src, original):
    v = ast.fix_missing_locations(Rewriter().visit(ast.parse(src)))
    header="""
import string
from mimid_context import scope__, stack__, method__
    """
    print(header)
    print(astor.to_source(v))
    footer="""
import json
import sys
import Tracer
from Tracer import taint_wrap__
WITH_TAINT = True
if __name__ == "__main__":
    js = []
    for arg in sys.argv[1:]:
        with open(arg) as f:
            mystring = f.read().strip().replace('\\n', ' ')
            print(repr(mystring), file=sys.stderr)
        restrict = {'files': [sys.argv[0]]}
        if WITH_TAINT:
            with Tracer.Tracer(mystring, restrict) as tracer:
                main(tracer())
        else:
            # DEBUG without taints:
            Tracer.trace_init()
            main(mystring)
            sys.exit(0)
        #print(arg, file=sys.stderr)
        assert tracer.inputstr.comparisons
        j = {
        'comparisons':Tracer.convert_comparisons(tracer.inputstr.comparisons, mystring),
        'method_map': Tracer.convert_method_map(tracer.method_map),
        'inputstr': str(tracer.inputstr),
        'original': %s,
        'arg': arg}
        js.append(j)
    print(json.dumps(js))
    # This generates a trace file if redirected to trace.json
    # use ./src/mine.py trace.json to get the derivation tree.
"""
    print(footer % repr(original))

ONLY_IN = False
import os.path
def main(args):
    original = open(args[1]).read()
    if ONLY_IN:
        rewrite_in(original, args[1])
    else:
        rewrite(original, args[1])

import sys
main(sys.argv)
