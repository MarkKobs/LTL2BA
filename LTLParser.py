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


def get_tree(tree:Node):
    if tree is not None:
        left = get_tree(tree.left)
        op = tree.token.value
        right = get_tree(tree.right)
        return left+op+right
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
        self.literals = []  # 字母表
        self.states = []  # 状态集合
        self.dnf_list = []  # dnf公式集合
        self.transitions = []  # 一个transition的列表
        self.accept_states = []  # 可接受状态

    def to_Standard_DNF(self,tree: Node):
        # 更改树的结构
        root = tree.token  # 根节点
        if root.value == "X":
            self.dnf_x(tree)
        elif root.value == "U":
            self.dnf_u(tree)
        elif root.value == "R":
            self.dnf_r(tree)
        elif root.value == "|":
            self.dnf_v(tree)
        elif root.value == "&":
            self.dnf_and(tree)
        else:  # 解析原子命题
            self.dnf_p(tree)

    def dnf_x(self, tree: Node):
        x_child = tree.right
        f = "X("+get_tree(x_child)+")"
        sub_f = get_tree(x_child)
        # 添加dnf
        self.dnf_list.append("true&"+f)
        # 添加状态
        if f not in self.states:
            self.states.append(f)
        if sub_f not in self.states:
            self.states.append(sub_f)
        # 添加迁移
        self.transitions.append(Transition(f, "true", sub_f))
        self.to_Standard_DNF(x_child)
        pass

    def dnf_u(self, tree: Node):
        left_child = tree.left
        right_child = tree.right
        f = get_tree(tree)
        left_f = get_tree(left_child)
        right_f = get_tree(right_child)
        # 新增dnf
        self.dnf_list.append(left_f+"&X("+f+")")
        # 添加迁移
        self.transitions.append(Transition(f, left_f, f))  # 转移到自身
        self.transitions.append(Transition(f, right_f, "true"))
        self.to_Standard_DNF(right_child)
        pass

    def dnf_r(self, tree: Node):
        pass

    def dnf_v(self, tree: Node):
        pass

    def dnf_and(self, tree: Node):
        pass

    def dnf_p(self, tree: Node):
        if tree.token.value != "true":
            self.dnf_list.append(tree.token.value + "&X(true)")
            self.literals.append(tree.token.value)
            if "true" not in self.states:
                self.states.append("true")
                transition = Transition(start="true", eat="true", end="true")
                self.transitions.append(transition)
                self.literals.append("true")
            pass
        pass

    def print_dnf(self):
        aps = ""
        for ap in self.literals:
            aps += (ap+" ")
        print('原子命题集合: '+aps+"\n")

        print("DNF公式集")
        for formula in self.dnf_list:
            print(formula)

        print("\n状态集合")
        for state in self.states:
            print(state)
        print("\n迁移")
        for transition in self.transitions:
            print("迁移:"+transition.start+"--->"+transition.eat+"--->"+transition.end)


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
        if tree.token.value not in analysis.states:
            analysis.states.append(get_tree(tree))
        if tree.token.type == P:
            analysis.transitions.append(Transition(tree.token.value, tree.token.value, "true"))
        analysis.to_Standard_DNF(tree)
        analysis.print_dnf()
        pass
