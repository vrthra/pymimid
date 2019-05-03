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
class Rewriter(ast.NodeTransformer):
    def wrap_in_method(self, body):
        method_name_expr = ast.Str(methods[-1])
        args = [method_name_expr]
        scope_expr = ast.Call(func=ast.Name(id='method__', ctx=ast.Load()), args=args, keywords=[])
        return [ast.With(items=[ast.withitem(scope_expr, None)], body=body)]

    def wrap_in_outer(self, name, counter, node):
        name_expr = ast.Str(name)
        counter_expr = ast.Num(counter)
        method_name_expr = ast.Str(methods[-1])
        args = [name_expr, counter_expr, method_name_expr]
        scope_expr = ast.Call(func=ast.Name(id='stack__', ctx=ast.Load()),
                args=args, keywords=[])
        return ast.With(items=[ast.withitem(scope_expr, None)], body=[node])

    def wrap_in_inner(self, name, counter, val, body):
        name_expr = ast.Str(name)
        counter_expr = ast.Num(counter)
        method_name_expr = ast.Str(methods[-1])
        val_expr = ast.Num(val)
        args = [name_expr, counter_expr, method_name_expr, val_expr]
        scope_expr = ast.Call(func=ast.Name(id='scope__', ctx=ast.Load()),
                args=args, keywords=[])
        return [ast.With(items=[ast.withitem(scope_expr, None)], body=body)]



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
        self.generic_visit(tree_node.test)
        for node in tree_node.body: self.generic_visit(node)
        tree_node.body = self.wrap_in_inner('if', counter, val, tree_node.body)

        # else part.
        if len(tree_node.orelse) == 1 and isinstance(tree_node.orelse[0], ast.If):
            self.process_if(tree_node.orelse[0], counter, val)
        else:
            if tree_node.orelse:
                for node in tree_node.orelse: self.generic_visit(node)
                val += 1
                tree_node.orelse = self.wrap_in_inner('if', counter, val, tree_node.orelse)


    def visit_If(self, tree_node):
        global if_counter
        if_counter += 1
        self.process_if(tree_node, counter=if_counter)
        return self.wrap_in_outer('if', if_counter, tree_node)


    def visit_While(self, tree_node):
        global while_counter
        while_counter += 1
        test = tree_node.test
        body = tree_node.body
        assert not tree_node.orelse
        self.generic_visit(tree_node)
        tree_node.body = self.wrap_in_inner('while', while_counter, 0, body)
        return self.wrap_in_outer('while', while_counter, tree_node)

    def visit_Compare(self, tree_node):
        left = tree_node.left
        if not tree_node.ops or not isinstance(tree_node.ops[0], ast.In):
            return tree_node
        mod_val = ast.Call(
            func=ast.Attribute(
                value=left,
                attr='in_'),
            args=tree_node.comparators,
            keywords=[])
        return mod_val

def rewrite(src):
    return ast.fix_missing_locations(Rewriter().visit(ast.parse(src)))


def main(args):
    original = open(args[1]).read()
    v = rewrite(original)
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
if __name__ == "__main__":
    mystring = sys.argv[1]
    restrict = {'methods': %s}
    with Tracer.Tracer(mystring, restrict) as tracer:
        main(tracer())
    assert tracer.inputstr.comparisons
    print(json.dumps({
        'comparisons':Tracer.convert_comparisons(tracer.inputstr.comparisons),
        'method_map': Tracer.convert_method_map(tracer.method_map),
        'inputstr': str(tracer.inputstr),
        'original': %s}))
    # This generates a trace file if redirected to trace.json
    # use ./src/mine.py trace.json to get the derivation tree.
"""
    print(footer % (repr(methods), repr(args[1])))

import sys
main(sys.argv)
