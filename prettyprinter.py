
class exprPrettyPrintingVisitor(v):
    def __init__(self):
        self.string = ""
    def prettyPrint(self):
        print self.string

    # Ops
    def visit_BinOp(self, node):
        return self.visit(node.left) + self.visit(node.op) + self.visit(node.right)

    def visit_UnaryOp(self, node):
        return addParen(self.visit(node.op) + self.visit(node.operand))

    def visit_Compare(self, node):
        self.visit(node.left)
        if len(node.ops) != 1:
            err.error("unsupported[translateToZ3.py :: exprVisitor :: visit_Compare]: node.ops list has more than 1 element")
        if len(node.comparators) != 1:
            err.error("unsupported[translateToZ3.py :: exprVisitor :: visit_Compare]: node.comparators list has more than 1 element")
        return addParen(self.visit(node.ops[0]) + self.visit(node.left) + self.visit(node.comparators[0]))

    # Arithmetic
    def visit_Add(self, node):
        #self.string += "+"
        return "+"
    def visit_Sub(self, node):
        #self.string += "-"
        return "-"
    def visit_Mult(self, node):
        #self.string += "*"
        return "*"
    def visit_Div(self, node):
        #self.string += "/"
        return "/"
    def visit_USub(self, node):
        #self.string += "-"
        return "-"

    # Relational
    def visit_Lt(self, node):
#    self.string += "<"
        return "<"
    def visit_Gt(self, node):
#    self.string += ">"
        return ">"
    def visit_GtE(self, node):
#    self.string += ">="
        return ">="
    def visit_LtE(self, node):
#    self.string += "<="
        return "<="
    def visit_Eq(self, node):
#    self.string += "=="
        return "=="
    def visit_NotEq(self, node):
#    self.string += "!="
        return "!="

    # Logical
    def visit_And(self, node):
        return "And"
    def visit_BoolOp(self, node):
        opStr = self.visit(node.op)
        #exprList = []
        #for val in node.values:
            #exprList.append(self.visit(val))
        exprStr = " ".join([self.visit(val) for val in node.values])
        return "(" + opStr + " " + exprStr + ")"

    # Generic
    def visit_Module(self, node):
        if len(node.body) != 1:
            err.error("unsupported[translateToZ3.py :: exprVisitor :: visit_Module]:Module.body has more than 1 element")
        return self.visit(node.body[0])

    def visit_Stmt(self, node):
        print "STMT"
        print ast.dump(node)
        exit()
        return

    def visit_Expr(self,node):
        return self.visit(node.value)

    def visit_Assign(self,node):
        if len(node.targets) != 1:
            err.error("unsupported[translateToZ3.py :: exprVisitor :: visit_Assign]:node.targets list has more than 1 elements")
        lhs = self.visit(node.targets[0])
        rhs = self.visit(node.value)
        return lhs+":="+rhs
    def visit_Load(self,Node):
        pass
    def visit_Store(self,Node):
        pass
    def visit_Name(self, node):
#    self.string += node.id
        return node.id
    def visit_Num(self, node):
        return str(node.n)
