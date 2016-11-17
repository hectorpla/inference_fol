########################### lex ###########################

tokens = (
    'PREDICATE','CONSTANT', 'VARIABLE', 'IMPLIES', 'COMMA', 'LPAREN', 'RPAREN',
    'NEGATE', 'AND', 'OR'
)

# literals = ['&', '|', '~', '(', ')'] # must be single character

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
    r'[A-Z][a-zA-Z]*\('
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
# tests
# sentences = ''' D(x,y) => ~H(y)
#                 B(x,y) & C(x,y) => A(x)
#                 D(John,Bob)
#                 ~Mother(x,y) | Parent(x,y) '''
#

# lex.input(w)
# 
# for tok in lexer:
#      print(tok)

########################### yacc ###########################

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
    def __init__(self,left,op,right, parent=None):
        self.type = "binop"
        self.left = left
        self.right = right
        self.op = op
        self.parent = parent
        
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

# both the following classes are nearly not relavent to
# to the parsing tree, and are stored directly to the KB
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
    if p[2] == '=>':
        p[0] = BinOp(NegateOp(p[1]), '|', p[3])
    else :
        p[0] = BinOp(p[1], p[2], p[3])

def p_sentence_negation(p):
    "sentence : NEGATE sentence"
    if p[2].op == '~':
        p[0] = p[2].left
    else:
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
    p[0] = Constant(p[1])

def p_term_variable(p):
    "term : VARIABLE"
    p[0] = Variable(p[1])

def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")

############################## Conversion to CNF ##############################
#
# during parsing time, a negation node does not
# know who is its parent
#
def populate_parent(root): # for negation nodes
    if root.type == "pred":
        return
    left, right = root.left, root.right
    if left:
        # if left.op == '~':
        left.parent = root
        populate_parent(left)
    if right:
        # if right.op == '~':
        right.parent = root
        populate_parent(right)
        

def push_negation_inward(root):
    if root.type == "pred":
        return
    if root.op == '~':
        child = root.left
        parent = root.parent
        
        if child.op == '~':
            if parent.left == root:
                parent.left = child.left
            else: 
                parent.right = child.left
            child.left.parent = parent
            push_negation_inward(child.left)
        if child.op == '&' or child.op == '|':
            child.left = NegateOp(child.left, child)
            child.right = NegateOp(child.right, child)          
            if child.op == '&':
                child.op = '|'
            elif child.op == '|':
                child.op = '&'
            child.parent = parent # update parent of '&' or '|'
            if parent.left == root: # cancel out the negation (middle level)
                parent.left = child
            else: 
                parent.right = child
            push_negation_inward(child.left), push_negation_inward(child.right)
    else:
        if root.left:
            push_negation_inward(root.left)
        if root.right:
            push_negation_inward(root.right)

##
# distribute 'or' into 'and'
# ~(A(x) & (B(x) | C(x))) should be converted into
# (~A(x) | ~B(x)) & (~A(x) | ~C(x))
# no longer necessary to keep track of parent of negations though inconsistent
##
import itertools
counter = itertools.count()
def distribute_or(root):
#     print('Distribute Or Called: ' + str(next(counter))) 
    
    if root.type == "pred":
        return
    
    if root.left:
        distribute_or(root.left)
    if root.right:
        distribute_or(root.right)
    
    # complexity might be very bad
    if root.op == '|' and (root.left.op == '&' or root.right.op == '&'): 
        parent = root.parent
        # left and right child of root
        left, right = root.left, root.right
        
        if left.op == '&':
            l_and, r_and = BinOp(left.left, '|', right), BinOp(left.right, '|', right)
        elif right.op == '&':
            l_and, r_and = BinOp(right.left, '|', left), BinOp(right.right, '|', left)
        new_and = BinOp(l_and, '&', r_and, parent) # parent of new node be parent of '|'
        l_and.parent = r_and.parent = new_and # set parent for two new '|'
        if parent.left == root:
            parent.left = new_and
        else: parent.right = new_and
        distribute_or(l_and), distribute_or(r_and) # check new children again
    
########################### Utilities ###########################
# a wrapper for yacc.parse()
def parse_sentence(line):
    ret = Start(yacc.parse(line))
    populate_parent(ret)
    push_negation_inward(ret)
    distribute_or(ret)
    return ret

def printTree(root):
    root.nprint()

# construct parser
import ply.yacc as yacc
yacc.yacc()

########################### Tests ###########################
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

m = '''Mother(Liz,Charley)
Father(Charley,Billy)
~Mother(x,y) | Parent(x,y)
~Father(x,y) | Parent(x,y)
~Parent(x,y) | Ancestor(x,y)
~(Parent(x,y) & Ancestor(y,z)) | Ancestor(x,z)'''

d = '''Dog(D)
       Owns(Jack,D)
       Dog(y) & Owns(x,y) => AnimalLover(x)
       ~(AnimalLover(x) & Animal(y) & Kills(x,y))
       Kills(Jack,Tuna) | Kills(Curiosity,Tuna)
       Cat(Tuna)
       Cat(x)   => Animal(x)
       ~Kills(Curiosity, Tuna) '''

w = ''' (A(x) => B(x)) & (B(x) => C(x)) '''

# test cases for or distribution
v = ''' ~(A(x) & B(x) | C(x))
        ~(A(x) & (B(x) | C(x)))
        ~((A(x) | D(x)) & (B(x) | C(x)))'''

# lines = v.splitlines()
# 
# for line in lines:
#     t = parse_sentence(line)
#     # print(type(t))
#     printTree(t)
#     print()
