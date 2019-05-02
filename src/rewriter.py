#!/usr/bin/env python3

# Rewrites the Python source file given so that
# 1) All `a in b` are transformed to a.in_(b)
# 2) All while conditions are transformed to have a with scope(): at the top
# 3) All if conditions are transformed to have a with scope(): at the top

import ast
import astor

method_name = None
if_counter = None
while_counter = None
class Rewriter(ast.NodeTransformer):
    def visit_FunctionDef(self, tree_node):
        global method_name, while_counter, if_counter
        while_counter = 0
        if_counter = 0
        method_name = tree_node.name
        self.generic_visit(tree_node)
        while_counter = 0
        return tree_node

    def wrap_in_with(self, name, val, body):
        name_expr = ast.Str(name)
        val_expr = ast.Num(val)
        args = [name_expr, val_expr]
        scope_expr = ast.Call(func=ast.Name(id='scope', ctx=ast.Load()),
                args=args, keywords=[])
        return [ast.With(items=[ast.withitem(scope_expr, None)], body=body)]


    def process_if(self, tree_node, name, val=None):
        if val is None: val = 0
        else: val += 1
        self.generic_visit(tree_node.test)
        for node in tree_node.body: self.generic_visit(node)
        tree_node.body = self.wrap_in_with(name, val, tree_node.body)

        # else part.
        if len(tree_node.orelse) == 1 and isinstance(tree_node.orelse[0], ast.If):
            self.process_if(tree_node.orelse[0], name, val)
        else:
            if tree_node.orelse:
                for node in tree_node.orelse: self.generic_visit(node)
                val += 1
                tree_node.orelse = self.wrap_in_with(name, val, tree_node.orelse)


    def visit_If(self, tree_node):
        global if_counter
        if_counter += 1
        name = 'if_%d %s' % (if_counter, method_name)
        self.process_if(tree_node, name=name)
        return tree_node


    def visit_While(self, tree_node):
        global while_counter
        while_counter += 1
        test = tree_node.test
        body = tree_node.body
        assert not tree_node.orelse
        self.generic_visit(tree_node)
        name = ast.Str('while_%d %s' % (while_counter, method_name))
        val = ast.Num(0)
        scope_expr = ast.Call(func=ast.Name(id='scope', ctx=ast.Load()), args=[name, val], keywords=[])
        tree_node.body = [ast.With(items=[ast.withitem(scope_expr, None)], body=body)]
        return tree_node

    def visit_Compare(self, tree_node):
        left = tree_node.left
        if not tree_node.ops or not isinstance(tree_node.ops[0], ast.In):
            return tree_node
        mod_val = ast.Call(
            func=ast.Attribute(
                value=left,
                attr='in_',
                ctx=left.ctx),
            args=tree_node.comparators,
            keywords=[])
        return mod_val

def rewrite(src):
    return ast.fix_missing_locations(Rewriter().visit(ast.parse(src)))


def main(args):
    v = rewrite(open(args[1]).read())
    header="""
import string
from helpers import scope
    """
    print(header)
    print(astor.to_source(v))


import sys
main(sys.argv)
