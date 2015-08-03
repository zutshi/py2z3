#!/usr/bin/python

################################################################################
# Remarks:
#
#   There is no documentation for the Python AST
#   To understand Python's ast, use
#       - ast.walk(<ast_objext>)
#       - ast.dump(<ast_objext>)
#       - external documentation:
#           https://greentreesnakes.readthedocs.org/en/latest/nodes.html
#
################################################################################
from __future__ import print_function

import ast
import z3
import err

#import imp
#z3 = imp.load_source('module.name','/home/zutshi/work/z3-4.3.2.97a5e6d326cb-x64-ubuntu-13.10/bin/z3.py')

#varDictZ3[varNameStr] = varId
varDictZ3 = {}


class v(ast.NodeVisitor):
    def generic_visit(self, node):
        print("generic handling of:", type(node).__name__)
        return ast.NodeVisitor.generic_visit(self, node)


class translatePythonExprToZ3Visitor(v):
    def visit_Subscript(self, node):
        z3_var_vector = self.visit(node.value)
        idx = self.visit(node.slice)
        return z3_var_vector[idx]

    def visit_Index(self, node):
        return self.visit(node.value)

    # Ops
    def visit_BinOp(self, node):
        if type(node.op) is ast.Add:
            return (self.visit(node.left) + self.visit(node.right))
        elif type(node.op) is ast.Sub:
            return (self.visit(node.left) - self.visit(node.right))
        elif type(node.op) is ast.Mult:
            return (self.visit(node.left) * self.visit(node.right))
        elif type(node.op) is ast.Div:
            return (self.visit(node.left) / self.visit(node.right))
        else:
            err.error("translateToZ3.py::translatePythonExprToZ3Visitor::visit_BinOp unhandled operator: " + ast.dump(node.op))
        #return self.visit(node.left) + self.visit(node.op) + self.visit(node.right)

    def visit_UnaryOp(self, node):
        if type(node.op) is ast.UAdd:
            return (self.visit(node.operand))
        elif type(node.op) is ast.USub:
            return (-self.visit(node.operand))
        else:
            err.error("translateToZ3.py::translatePythonExprToZ3Visitor::visit_UnaryOp unhandled operator" + ast.dump(node.op))

    def visit_Compare(self, node):
        self.visit(node.left)
        if len(node.ops) != 1:
            err.error("unsupported[translateToZ3.py :: exprVisitor :: visit_Compare]: node.ops list has more than 1 element")
        if len(node.comparators) != 1:
            err.error("unsupported[translateToZ3.py :: exprVisitor :: visit_Compare]: node.comparators list has more than 1 element")

        op = node.ops[0]
        rightOperand = node.comparators[0]

        if type(op) is ast.Lt:
            return (self.visit(node.left) < self.visit(rightOperand))
        if type(op) is ast.Gt:
            return (self.visit(node.left) > self.visit(rightOperand))
        if type(op) is ast.GtE:
            return (self.visit(node.left) >= self.visit(rightOperand))
        if type(op) is ast.LtE:
            return (self.visit(node.left) <= self.visit(rightOperand))
        if type(op) is ast.Eq:
            return (self.visit(node.left) == self.visit(rightOperand))
        if type(op) is ast.NotEq:
            return (self.visit(node.left) != self.visit(rightOperand))
        else:
            err.error("translateToZ3.py::translatePythonExprToZ3Visitor::visit_Compare unhandled operator" + ast.dump(op))

    # Arithmetic
    def visit_Add(self, node):
        err.error("op!!")
        return z3.Sum

    def visit_Sub(self, node):
        err.error("op!!")
        return z3.Sum

    def visit_Mult(self, node):
        err.error("op!!")
        return z3.Product

    def visit_Div(self, node):
        err.error("op!!")
        return "/"

    def visit_USub(self, node):
        err.error("op!!")
        return "-"

    # Relational
    def visit_Lt(self, node):
        err.error("op!!")
        return "<"

    def visit_Gt(self, node):
        err.error("op!!")
        return ">"

    def visit_GtE(self, node):
        err.error("op!!")
        return ">="

    def visit_LtE(self, node):
        err.error("op!!")
        return "<="

    def visit_Eq(self, node):
        err.error("op!!")
        return "=="

    def visit_NotEq(self, node):
        err.error("op!!")
        return "!="

    # Logical
    def visit_Or(self, node):
        err.error("z3.Or unexpected!!")
        return z3.Or

    def visit_And(self, node):
        return z3.And

    def visit_BoolOp(self, node):
        op = self.visit(node.op)
        exprList = []
        for val in node.values:
            exprList.append(self.visit(val))
        #exprList = " ".join([self.visit(val) for val in node.values])
        return (op(*exprList))

    # Generic
    def visit_Module(self, node):
        if len(node.body) != 1:
            err.error("unsupported[translateToZ3.py :: exprVisitor :: visit_Module]:Module.body has more than 1 element")
        return self.visit(node.body[0])

    def visit_Expr(self, node):
        return (self.visit(node.value))

    def visit_Assign(self, node):
        err.error("assigns in constraints?!!")
        if len(node.targets) != 1:
            err.error("unsupported[translateToZ3.py :: exprVisitor :: visit_Assign]:node.targets list has more than 1 elements")
        lhs = self.visit(node.targets[0])
        rhs = self.visit(node.value)
        return lhs+":="+rhs

    def visit_Load(self, Node):
        pass

    def visit_Store(self, Node):
        pass

    def visit_Name(self, node):
        global varDictZ3
        return varDictZ3[node.id]

    def visit_Num(self, node):
        return node.n


def getZ3VarList(varList):
    global varDictZ3
    z3VarList = []
    for v in varList:
        if v.typStr == "R":
            try:
                if v.subTypStr == 'V':
                    z3Var = z3.RealVector(v.nameStr, v.dim)
                else:
                    raise err.Fatal('unhandled subtype: {}'.format(v.subTypStr))
            # if subtype is not present, default to regular 'Real'
            except AttributeError:
                z3Var = z3.Real(v.nameStr)
        elif v.typStr == "B":
            z3Var = z3.Bool(v.nameStr)
        elif v.typStr == "I":
            try:
                if v.subTypStr == 'V':
                    z3Var = z3.IntVector(v.nameStr, v.dim)
                else:
                    raise err.Fatal('unhandled subtype: {}'.format(v.subTypStr))
            except AttributeError:
                z3Var = z3.Int(v.nameStr)
        # type X: don't care..treat it as anything, lets say Real
        elif v.typStr == "X":
            z3Var = z3.Real(v.nameStr)
        else:
            err.error("translateToZ3.py :: getOutputVars: unhandled type - " + v.typStr)
        varDictZ3[v.nameStr] = z3Var
        z3VarList.append(z3Var)
    return z3VarList


def translate(pcObj):
    global varDictZ3
    pythonExprToZ3Translator = translatePythonExprToZ3Visitor()

#  rawPCFile = fops.getData(fileName)
#  pcObj = parseBasic.parse(rawPCFile)

    pcObj.outputsZ3 = getZ3VarList(pcObj.outputs)
    pcObj.inputsZ3 = getZ3VarList(pcObj.inputs)
    pcObj.statesZ3 = getZ3VarList(pcObj.states)

    pathListPython = pcObj.parsedPathList
    for path in pathListPython:
        pathConsPython = path[0]
        opConsList = path[1]

        # if a constraint expression has only constants, it will result in a
        # python bool after parsing. In such a case, silently ignore [better
        # suggestions??]. Z3 can handle python bools.
        #print('='*100)
        #print(pcObj.py_str)
        pathConsZ3 = pythonExprToZ3Translator.visit(pathConsPython)

        # clear the list
        opConsZ3List = []
        for opName, opCons in opConsList:
            opConsZ3 = pythonExprToZ3Translator.visit(opCons)
            [print(k, varDictZ3[k]) for k in varDictZ3]
            opConsZ3List.append((varDictZ3[opName], opConsZ3))
        pcObj.pathListZ3.append((pathConsZ3, opConsZ3List))

    return pcObj
