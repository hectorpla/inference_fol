tokens = (
    'PREDICATE','CONSTANT', 'VARIABLE', 'IMPLIES', 'COMMA', 'LPAREN', 'RPAREN',
    'NEGATE', 'AND', 'OR'
)

literals = ['&', '|', '~', '(', ')'] # must be single character

# Tokens

# t_PREDICATE = r'[A-Z][a-z]*\('
t_CONSTANT = r'[A-Z_][a-zA-Z0-9_]*'
t_VARIABLE = r'[a-z][a-z0-9_]*'

t_IMPLIES = r'=>'
t_COMMA = r','
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_NEGATE = r'~'
t_AND = r'&'
t_OR = r'\|'


def t_PREDICATE(t):
    r'[A-Z][a-z]*\('
    return t

t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lexer = lex.lex()

# sentences = ''' D(x,y) => ~H(y)
#                 B(x,y) & C(x,y) => A(x)
#                 D(John,Bob)
#                 ~Mother(x,y) | Parent(x,y) '''
# 
# lex.input(sentences)

# for tok in lexer:
#     print(tok)

############################# yacc ###########################

# Parsing rules

precedence = (
    ('left', 'IMPLIES'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NEGATE'),
)

# definitions of grammar tree nodes (might abstract further) #
class Start: # start of a sentence
    def __init__(self, left):
        self.type = "start"
        self.left = left # only one child, must be a predicate
        self.right = None
        self.op = "start"
    
    def nprint(self):
        self.left.nprint()

class NegateOp:
    def __init__(self, left, parent=None):
        self.type = "negop"
        self.left = left # only one child, must be a predicate
        self.right = None
        self.op = "~"
        self.parent = parent
        
    def nprint(self):
        print('~(', end='')
        self.left.nprint()
        print(')', end='')

class BinOp:
    def __init__(self,left,op,right):
        self.type = "binop"
        self.left = left
        self.right = right
        self.op = op
        
    def nprint(self):
        print(self.op + '(', end='')
        self.left.nprint()
        print(', ', end='')
        self.right.nprint()
        print(')', end='')

class Predicate():
    def __init__(self, name, children=None):
         self.type = "pred"
         self.name = name
         if children: self.children = children
         else: self.children = [ ]
         self.op = "pred"
         
    def nprint(self):
        print('[' + self.name + ': ', end='')
        for child in self.children:
            child.nprint()
            print(' ', end='')
        print('%c' % 8, end='')
        print(']', end='')
        
class List():
    def __init__(self, first_child):
        self.type = "list"
        self.children = []
        self.children.append(first_child)

class Variable():
    def __init__(self, value):
        self.type = "var"
        self.value = value
    def nprint(self):
        print(self.value, end='')
        
class Constant():
    def __init__(self, value):
        self.type = "const"
        self.value = value
    def nprint(self):
        print(self.value, end='')


# grammar rules #
def p_sentence_binop(p):
    '''sentence : sentence AND sentence
                | sentence OR sentence
                | sentence IMPLIES sentence
    '''
    p[0] = BinOp(p[1], p[2], p[3])

def p_sentence_negation(p):
    "sentence : NEGATE sentence"
    p[0] = NegateOp(p[2])

def p_sentence_group(p):
    "sentence : LPAREN sentence RPAREN"
    p[0] = p[2]

def p_sentence_atomic(p):
    "sentence : atomic"
    p[0] = p[1]

def p_atomic(p):
    "atomic : PREDICATE term_list RPAREN"
    p[0] = Predicate(p[1][0:-1])
    p[0].children = p[2].children

def p_term_list(p):
    '''term_list : term
                 | term_list COMMA term'''
    if len(p) == 2:
        p[0] = List(p[1])
    elif len(p) == 4:
        p[1].children.append(p[3])
        p[0] = p[1]

def p_term_constant(p):
    "term : CONSTANT"
    p[0] = Variable(p[1])

def p_term_variable(p):
    "term : VARIABLE"
    p[0] = Constant(p[1])

def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")

# Conversion to CNF #
def elim_implication(root):
    if root.type == "pred":
        return
    if root.op == '=>':
        left, right = root.left, root.right
        root.left = NegateOp(left, root)
        root.op = '|'
        elim_implication(left)
        elim_implication(right)
    else:
        if root.left: 
            elim_implication(root.left)
        if root.right:
            elim_implication(root.right)    

#
# during parsing time, a negation node does not
# know who is its parent
#
def populate_parent(root): # for negation nodes
    if root.type == "pred":
        return
    left, right = root.left, root.right
    if left:
        if left.op == '~':
            left.parent = root
        populate_parent(left)
    if right:
        if right.op == '~':
            right.parent = root
        populate_parent(right)
        

def push_negation_inward(root):
    if root.type == "pred":
        return
    if root.op == '~':
        child = root.left
        parent = root.parent
        
        if child.op == '~':
            if parent.left == root: parent.left = child.left
            else: parent.right = child.left
            child.left.parent = parent
            push_negation_inward(child.left)
        #if child.op == '&':
    else:
        if root.left:
            push_negation_inward(root.left)
        if root.right:
            push_negation_inward(root.right)

# Utilities #
# a wrapper for yacc.parse()
def parse_sentence(s):
    ret = Start(yacc.parse(line))
    populate_parent(ret)
    return ret

def printTree(root):
    root.nprint()

import ply.yacc as yacc
yacc.yacc()

s = '''A(x) => H(x)
D(x,y) => ~H(y)
B(x,y) & C(x,y) => A(x)
B(John,Alice)
B(John,Bob)
(D(x,y) & F(y)) => C(x,y)
D(John,Alice)'''

ss = '''(A(x) & B(x))
((A(x) & B(x)) => C(x))
(~A(x))
A(x)
(~(~(~(~A(x)))))'''

lines = s.splitlines()

for line in lines:
    t = parse_sentence(line)
    # print(type(t))
    elim_implication(t)
    push_negation_inward(t)
    printTree(t)
    print()
