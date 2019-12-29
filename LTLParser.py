"""
ap
p   = ap | !ap
I1  = I1 Rop I1 | p | J
I2  = I2 Rop I2 | p
J   = I2 Top1 I2| I2 Top2 I2
Rop = & | |
Top1= R | U
Top2= X
Lpa = (
Rpa = )
"""
ROP = "ROP"
TOP1 = 'TOP1'
TOP2 = "TOP2"
P = "P"
EOF = "EOF"  # 文件尾
Rop = ["&", "|"]
Top1 = ["R", "U"]
Top2 = ["X"]
LPA = '('
RPA = ')'


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_token = None
        self.current_char = self.text[self.pos]

    def ParseError(self):
        raise Exception('Error parsing!')

    def advance(self):
        """advance the pointer and set the current_char variable"""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
            # indicates the end
        else:
            self.current_char = self.text[self.pos]

    def get_next_token(self):
        while self.current_char is not None:
            # true
            if self.current_char == "t":
                self.advance()
                if self.current_char == "r":
                    self.advance()
                    if self.current_char == "u":
                        self.advance()
                        if self.current_char == "e":
                            self.advance()
                            return Token(P, "true")
                        else:
                            self.pos -= 3
                            self.current_char = self.text[self.pos]
                    else:
                        self.pos -= 2
                        self.current_char = self.text[self.pos]
                else:
                    self.pos -= 1
                    self.current_char = self.text[self.pos]
            else:
                pass
            # false
            if self.current_char == "f":
                self.advance()
                if self.current_char == "a":
                    self.advance()
                    if self.current_char == "l":
                        self.advance()
                        if self.current_char == "s":
                            self.advance()
                            if self.advance() == "e":
                                self.advance()
                                return Token(P, "false")
                            else:
                                self.pos -= 3
                                self.current_char = self.text[self.pos]
                        else:
                            self.pos -= 2
                            self.current_char = self.text[self.pos]
                    else:
                        self.pos -= 1
                        self.current_char = self.text[self.pos]
                else:
                    pass

            if self.current_char.islower():  # 判断小写字母,是叶子节点
                token = Token(P, self.current_char)
                self.advance()
                return token
            if self.current_char == "!":  # 判断是非
                self.advance()
                if self.current_char.islower():
                    token = Token(P, "!" + self.current_char)
                    self.advance()
                    return token
                else:
                    self.ParseError()
            if self.current_char in Rop:
                if self.current_char == "&":
                    token = Token("&", self.current_char)
                elif self.current_char == "|":
                    token = Token("|", self.current_char)
                self.advance()
                return token
            if self.current_char in Top1:
                if self.current_char == "R":
                    token = Token("R", self.current_char)
                elif self.current_char == "U":
                    token = Token("U", self.current_char)
                self.advance()
                return token
            if self.current_char in Top2:
                token = Token("X", self.current_char)
                self.advance()
                return token
            if self.current_char == "(":
                self.advance()
                return Token(LPA, "(")
            if self.current_char == ")":
                self.advance()
                return Token(RPA, ")")
            self.error()
        return Token(EOF, None)


class AST:
    pass


# 所有的token都建立一个node
class Node(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = op
        self.right = right


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        """proposition | Lpa expr Rpa | X Lpa expr Rpa"""
        token = self.current_token
        if token.type == P:
            self.eat(P)
            return Node(None, token, None)
        elif token.type == "X":
            self.eat("X")
            self.eat(LPA)
            node = Node(left=None, op=Token("X", "X"), right=self.expr())
            self.eat(RPA)
            return node
        elif token.type == LPA:
            self.eat(LPA)
            node = self.expr()
            self.eat(RPA)
            return node

    def term(self):
        """term : factor ((& | |) factor)*"""
        node = self.factor()
        while self.current_token.type in Rop:
            token = self.current_token
            if token.type == "&":
                self.eat("&")
            elif token.type == "|":
                self.eat("|")
            node = Node(node, token, self.factor())
        return node

    def expr(self):
        """
        expr   : term ((R | U) term)*
        """
        node = self.term()
        while self.current_token.type in Top1:
            token = self.current_token
            if token.type == "R":
                self.eat("R")
            elif token.type == "U":
                self.eat("U")
            node = Node(node, token, self.term())
        return node

    def parse(self):
        return self.expr()


class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser

    def visit_Node(self, node):
        if node.token.type == P:
            self.visit_P(node)
        elif node.token.type in Rop:
            self.visit_ROP(node)
        elif node.token.type in Top1:
            self.visit_TOP1()

    def visit_P(self, node):
        return node.token.value

    def visit_ROP(self, node):
        if node.token.type == "&":
            return self.visit(node.left) + "&" + self.visit(node.right)
        elif node.token.type == "|":
            return self.visit(node.left) + "|" + self.visit(node.right)

    def visit_TOP1(self, node):
        if node.token.type == "R":
            return self.visit(node.left) + "R" + self.visit(node.right)
        elif node.token.type == "U":
            return self.visit(node.left) + "U" + self.visit(node.right)

    def interpret(self):
        tree = self.parser.parse()
        return tree


def print_tree(tree: Node):
    if tree is not None:
        print_tree(tree.left)
        print("type:" + tree.token.type + "     value:" + tree.token.value)
        print_tree(tree.right)
    return


def get_tree(tree: Node):
    if tree is not None:
        left = get_tree(tree.left)
        op = tree.token.value
        right = get_tree(tree.right)
        return left + op + right
    else:
        return ""


##############################################
###############     DNF    ###################
##############################################
class Transition(object):
    def __init__(self, start, eat, end):
        # start ---eat---> end
        self.start = start
        self.eat = eat
        self.end = end


class Analysis(object):
    def __init__(self):
        self.states = []  # 状态集合
        self.dnf_list = []  # dnf公式集合
        self.small_dnf_set = []  # 子公式 dnf集合

    def is_dnf(self, tree: Node):
        if tree.token.value == "&" and tree.right.token.value == "X":
            return True
        else:
            return False

    def to_Standard_DNF(self, tree: Node):
        # 转树的结构
        root = tree.token  # 根节点
        if root.value == "X":
            return self.dnf_x(tree)
        elif root.value == "U":
            return self.dnf_u(tree)
        elif root.value == "R":
            return self.dnf_r(tree)
        elif root.value == "|":
            return self.dnf_v(tree)
        elif root.value == "&":
            return self.dnf_and(tree)
        else:  # 解析原子命题
            return self.dnf_p(tree)

    def dnf_x(self, tree: Node):
        self.small_dnf_set = []
        x_child = tree.right
        f = "X(" + get_tree(x_child) + ")"
        sub_f = get_tree(x_child)
        # 添加dnf
        self.small_dnf_set.append("true&" + f)
        self.dnf_list.append(tuple((f, self.small_dnf_set)))
        # 添加状态
        if f not in self.states:
            self.states.append(f)
        if sub_f not in self.states:
            self.states.append(sub_f)
        appending = []
        appending.append(x_child.token.value)
        return appending

    def dnf_u(self, tree: Node):
        self.small_dnf_set = []
        left_child = tree.left
        right_child = tree.right
        f = get_tree(tree)
        left_f = get_tree(left_child)
        right_f = get_tree(right_child)
        # 新增dnf
        self.small_dnf_set.append(left_f + "&X(" + f + ")")
        self.small_dnf_set.append(self.to_Standard_DNF(right_child))
        self.dnf_list.append(tuple((f, self.small_dnf_set)))
        appending = []
        appending.append(right_f)
        if not self.is_dnf(right_child) and f not in self.states:  # phy2 如果不是dnf的话就返回要继续解析的字符
            return appending

    def dnf_r(self, tree: Node):
        return None
        pass

    def dnf_v(self, tree: Node):
        self.small_dnf_set = []
        left_child = tree.left
        right_child = tree.right
        left_f = get_tree(left_child)
        right_f = get_tree(right_child)
        appending = []
        self.small_dnf_set.append(self.to_Standard_DNF(left_child))
        self.small_dnf_set.append(self.to_Standard_DNF(right_child))
        self.dnf_list.append(tuple((get_tree(tree), self.small_dnf_set)))
        pass

    def dnf_and(self, tree: Node):
        self.small_dnf_set = []
        left_child = tree.left
        right_child = tree.right
        left_f = get_tree(left_child)
        right_f = get_tree(right_child)
        appending = []

        return None
        pass

    def dnf_p(self, tree: Node, flag=0):
        if tree.token.value != "true":
            dnf = tree.token.value + "&X(true)"
            if "true" not in self.states:
                self.states.append("true")
        return dnf
        pass

    def print_dnf(self):
        print("DNF公式集")
        for formula in self.dnf_list:
            print(formula)

        print("\n状态集合")
        for state in self.states:
            print(state)


if __name__ == "__main__":
    # test parser and lexer
    # parser = Lexer("a&!b")
    # token = parser.get_next_token()
    # while token is not None:
    #     print(token.type)
    #     token = parser.get_next_token()
    while True:
        try:
            try:
                text = input('f> ')
            except NameError:  # Python3
                text = input('f> ')
        except EOFError:
            break
        if not text:
            continue

        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        tree = interpreter.interpret()
        # 得到LTL的语法解析树
        print("字符:")
        print_tree(tree)
        print("\n")
        analysis = Analysis()
        # 初始公式先加入到状态集合中
        if tree.token.value not in analysis.states and tree.token.value != "X":
            analysis.states.append(get_tree(tree))
        remaining = analysis.to_Standard_DNF(tree)
        if remaining is not None:
            for r in remaining:
                lexer = Lexer(r)
                parser = Parser(lexer)
                interpreter = Interpreter(parser)
                tree = interpreter.interpret()
                analysis.to_Standard_DNF(tree)
        analysis.print_dnf()
        pass
