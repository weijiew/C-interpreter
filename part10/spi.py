
INTEGER       = 'INTEGER'
REAL          = 'REAL'
INTEGER_CONST = 'INTEGER_CONST'
REAL_CONST    = 'REAL_CONST'
PLUS          = 'PLUS'
MINUS         = 'MINUS'
MUL           = 'MUL'
INTEGER_DIV   = 'INTEGER_DIV'
FLOAT_DIV     = 'FLOAT_DIV'
LPAREN        = 'LPAREN'
RPAREN        = 'RPAREN'
ID            = 'ID'
ASSIGN        = 'ASSIGN'
BEGIN         = 'BEGIN'
END           = 'END'
SEMI          = 'SEMI'
DOT           = 'DOT'
PROGRAM       = 'PROGRAM'
VAR           = 'VAR'
COLON         = 'COLON'
COMMA         = 'COMMA'
EOF           = 'EOF'


class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return "Token({type},{value})".format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()


# 标识符分为语言自带的和另外声明的。
# 前者称为保留字，例如 BEGIN 和 END 。
# 后者就是变量。都要将其转换位 Token 。
RESERVED_KEYWORDS = {
    'PROGRAM': Token('PROGRAM', 'PROGRAM'),
    'VAR': Token('VAR', 'VAR'),
    'DIV': Token('INTEGER_DIV', 'DIV'),
    'INTEGER': Token('INTEGER', 'INTEGER'),
    'REAL': Token('REAL', 'REAL'),
    'BEGIN': Token('BEGIN', 'BEGIN'),
    'END': Token('END', 'END'),
}


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        return Exception("Error parsing input")

    def advance(self):
        """指向当前字符指针自增，
        获取下一个字符内容。
        """
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        """返回当前指针所指的下一个字符

        例如扫描到了 : 为了识别是否是 :=
        需要预判，所以该函数的目的是为了
        识别当前字符的下一个字符。
        """
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_comment(self):
        """处理注释，直到遇到 } 结束"""
        while self.current_char != '}':
            self.advance()
        self.advance()

    def skip_whitespace(self):
        """跳过或空格，利用 advance 来推进。
        同时进行边界判断，防止越界！
        """
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        """处理实数，也就是整数和浮点数。

        多位整数处理，一旦遇到数字就将其转换为多位整数。
        指针递进依旧调用 advance 函数实现。
        """
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        # 处理小数的逻辑
        if self.current_char == '.':
            result += self.current_char
            self.advance()

            while (
                    self.current_char is not None and
                    self.current_char.isdigit()
            ):
                result += self.current_char
                self.advance()

            token = Token('REAL_CONST', float(result))
        else:
            token = Token('INTEGER_CONST', int(result))

        return token

    def _id(self):
        """处理保留字

        如果是保留字就返回该保留字的 token ，
        反之就将当前识别到的字符作为标识符 id 的 token
        """
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()

        token = RESERVED_KEYWORDS.get(result, Token(ID, result))
        return token

    def get_next_token(self):
        """获取 token """

        while self.current_char is not None:

            # 处理空格
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # 处理注释
            if self.current_char == '{':
                self.advance()
                self.skip_comment()
                continue

            # 处理保留字
            if self.current_char.isalpha():
                return self._id()

            # 处理多位整数
            if self.current_char.isdigit():
                return self.number()

            # 处理赋值符号 :=
            if self.current_char == ':' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(ASSIGN, ':=')

            # 处理分号，代码块的结束
            if self.current_char == ';':
                self.advance()
                return Token(SEMI, ';')

            # 处理 : 用于声明变量
            # 例如 number : INTEGER;
            if self.current_char == ':':
                self.advance()
                return Token(COLON, ':')

            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(FLOAT_DIV, '/')

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            if self.current_char == '.':
                self.advance()
                return Token(DOT, '.')

            self.error()

        return Token(EOF, None)


###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################

class AST(object):
    pass

# 定义 node 类型，均继承自 AST
class BinOp(AST):
    """用来表示一个两层的二叉树
     左右节点是操作数，而根节点是操作符
     操作符有四种类型，加减乘除。
    """
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr


class Compound(AST):
    """Represents a 'BEGIN ... END' block"""
    def __init__(self):
        self.children = []


class Assign(AST):
    """用来表示赋值语句，例如： a := 1 """
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Var(AST):
    """Var 节点是由 ID token 构造出来的。"""
    def __init__(self, token):
        self.token = token
        self.value = token.value


class NoOp(AST):
    """表示 empty statement. """
    pass


class Program(AST):
    """可以理解为 AST 的 root 节点 """
    def __init__(self, name, block):
        self.name = name
        self.block = block


class Block(AST):
    """声明 compound statement """
    def __init__(self, declarations, compound_statement):
        self.declarations = declarations
        self.compound_statement = compound_statement


class VarDecl(AST):
    """声明变量的节点表示
    例如： a : INTEGER
    分别表示左，根，右三个节点。
    """
    def __init__(self, var_node, type_node):
        self.var_node = var_node
        self.type_node = type_node


class Type(AST):
    """用来表示数据类型
    目前只有两种类型 INTEGER or REAL
    """
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()


    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def block(self):
        """block : declarations compound_statement"""
        declaration_nodes = self.declarations()
        compound_statement_node = self.compound_statement()
        node = Block(declaration_nodes, compound_statement_node)
        return node

    def declarations(self):
        """declarations : VAR (variable_declaration SEMI)+
                        | empty
        """
        declarations = []
        if self.current_token.type == VAR:
            self.eat(VAR)
            while self.current_token.type == ID:
                var_decl = self.variable_declaration()
                declarations.extend(var_decl)
                self.eat(SEMI)

        return declarations

    def variable_declaration(self):
        """variable_declaration : ID (COMMA ID)* COLON type_spec"""
        var_nodes = [Var(self.current_token)]  # first ID
        self.eat(ID)

        while self.current_token.type == COMMA:
            self.eat(COMMA)
            var_nodes.append(Var(self.current_token))
            self.eat(ID)

        self.eat(COLON)

        type_node = self.type_spec()
        var_declarations = [
            VarDecl(var_node, type_node)
            for var_node in var_nodes
        ]
        return var_declarations

    def type_spec(self):
        """type_spec : INTEGER
                     | REAL
        """
        token = self.current_token
        if self.current_token.type == INTEGER:
            self.eat(INTEGER)
        else:
            self.eat(REAL)
        node = Type(token)
        return node

    def program(self):
        """program : PROGRAM variable SEMI block DOT"""
        self.eat(PROGRAM)
        var_node = self.variable()
        prog_name = var_node.value
        self.eat(SEMI)
        block_node = self.block()
        program_node = Program(prog_name, block_node)
        self.eat(DOT)
        return program_node

    def compound_statement(self):
        """
        compound_statement: BEGIN statement_list END
        """
        self.eat(BEGIN)
        nodes = self.statement_list()
        self.eat(END)

        root = Compound()
        for node in nodes:
            root.children.append(node)

        return root

    def statement_list(self):
        """
        statement_list : statement
                       | statement SEMI statement_list
        """

        node = self.statement()

        results = [node]

        while self.current_token.type == SEMI:
            self.eat(SEMI)
            results.append(self.statement())

        if self.current_token.type == ID:
            self.error()

        return results

    def statement(self):
        """
        statement : compound_statement
                  | assignment_statement
                  | empty
        """
        if self.current_token.type == BEGIN:
            node = self.compound_statement()
        elif self.current_token.type == ID:
            node = self.assignment_statement()
        else:
            node = self.empty()

        return node

    def assignment_statement(self):
        """
        assignment_statement : variable ASSIGN expr
        """
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        right = self.expr()
        node = Assign(left, token, right)
        return node

    def variable(self):
        """
        variable : ID
        """
        node = Var(self.current_token)
        self.eat(ID)
        return node

    def empty(self):
        """An empty production"""
        return NoOp()

    def expr(self):
        """
        expr : term ((PLUS | MINUS) term)*
        """
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def term(self):
        """term : factor ((MUL | INTEGER_DIV | FLOAT_DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (MUL, INTEGER_DIV, FLOAT_DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == INTEGER_DIV:
                self.eat(INTEGER_DIV)
            elif token.type == FLOAT_DIV:
                self.eat(FLOAT_DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def factor(self):
        """factor : PLUS factor
                  | MINUS factor
                  | INTEGER_CONST
                  | REAL_CONST
                  | LPAREN expr RPAREN
                  | variable
        """

        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == INTEGER_CONST:
            self.eat(INTEGER_CONST)
            return Num(token)
        elif token.type == REAL_CONST:
            self.eat(REAL_CONST)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        else:
            node = self.variable()
            return node

    def parse(self):
        """
        program : PROGRAM variable SEMI block DOT
        block : declarations compound_statement
        declarations : VAR (variable_declaration SEMI)+
                     | empty
        variable_declaration : ID (COMMA ID)* COLON type_spec
        type_spec : INTEGER | REAL
        compound_statement : BEGIN statement_list END
        statement_list : statement
                       | statement SEMI statement_list
        statement : compound_statement
                  | assignment_statement
                  | empty
        assignment_statement : variable ASSIGN expr
        empty :
        expr : term ((PLUS | MINUS) term)*
        term : factor ((MUL | INTEGER_DIV | FLOAT_DIV) factor)*
        factor : PLUS factor
               | MINUS factor
               | INTEGER_CONST
               | REAL_CONST
               | LPAREN expr RPAREN
               | variable
        variable: ID
        """
        node = self.program()
        if self.current_token.type != EOF:
            self.error()

        return node


###############################################################################
#                                                                             #
#  INTERPRETER                                                                #
#                                                                             #
###############################################################################

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):

    GLOBAL_SCOPE = {}

    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == INTEGER_DIV:
            return self.visit(node.left) // self.visit(node.right)
        elif node.op.type == FLOAT_DIV:
            return float(self.visit(node.left)) / float(self.visit(node.right))

    def visit_Program(self, node):
        self.visit(node.block)

    def visit_Block(self, node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node):
        pass

    def visit_Type(self, node):
        # Do nothing
        pass

    def visit_Num(self, node):
        return node.value

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)

    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        """当给某个变量赋值时，
        需要将该变量存起来，
        因为后续可能会用到
        """
        var_name = node.left.value
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

    def visit_Var(self, node):
        var_name = node.value
        val = self.GLOBAL_SCOPE.get(var_name)
        if val is None:
            raise NameError(repr(var_name))
        else:
            return val

    def visit_NoOp(self, node):
        pass

    def interpret(self):
        tree = self.parser.parse()
        if tree is None:
            return ''
        return self.visit(tree)


def main():
    import sys
    text = open(sys.argv[1], 'r').read()

    lexer = Lexer(text)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    result = interpreter.interpret()
    print(interpreter.GLOBAL_SCOPE)


if __name__ == '__main__':
    main()