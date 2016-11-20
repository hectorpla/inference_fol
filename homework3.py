import argparse
DEBUG = False
cmdparser = argparse.ArgumentParser(description='Command Parser')
cmdparser.add_argument('-d', action='store_true', default=False)
args = cmdparser.parse_args()
DEBUG = args.d
########################### KB's data structure ###########################
import copy
import itertools
counter = itertools.count()
# head of a clause in the KB
class Clause:
    def __init__(self):
        self.num = next(counter)
        self.next = None
    
    def copy(self):
        head = copy.copy(self)
        cur = head
        cur_origin = self.next
        while cur_origin:
            cur_origin.print()
            temp = cur
            cur = cur_origin.copy()
            cur.prev, cur.head = temp, head
            temp.next = cur
            cur_origin = cur_origin.next
        return head
    
    def merge_clause(self, rhs):
        assert isinstance(rhs, Clause)
        
        cur, tail = self, None
        while cur:
            tail, cur = cur, cur.next
        tail.next = rhs.next   
        rhs.next.prev = tail 
    
    def print(self):
        print('CLAUSE ' + str(self.num) + ": ", end='')
    

# a link in a clause (different from that in the parser)
class Predicate:
    def __init__(self, name, args, prev):
        self.name = name
        self.args = args
        self.prev = prev
        self.head = None
        self.next = None
    
    def copy(self):
        new_args = []
        for arg in self.args:
            if arg.type == 'var': # variables are new copies
                new_args.append(copy.copy(arg))
            else: # constants are always the same object
                new_args.append(arg)
        return Predicate(self.name, new_args, None)
    
    # remove itself from the clause
    def remove_self(self):
        self.prev.next = self.next
        if self.next:
            self.next.prev = self.prev
    
    def print(self):
        print('[' + self.name + ': ', end='')
        for child in self.args:
            child.nprint(DEBUG), print(' ', end='')
        print('%c]' % 8, end='')

##
# a dictionary to store clauses in different bucket with respect to
#  the name of component predicates
##
KB = {}
########################### Extract info from CNFs ###########################
import logicparser as lp
def seperate_clauses(root):
    clauses = []
    nodeq = []
    
    nodeq.append(root)
    while nodeq:
        node = nodeq.pop()
        if node.op == '&':
            nodeq.append(node.left)
            nodeq.append(node.right)
        else:
            clauses.append(node)
    return clauses            

# convert a predicate/negation node to a Predicate object
def convert_to_pred(node, prev):
    if node.type == 'negop':
        pred_node = node.left
        ret = Predicate('-' + pred_node.name, pred_node.children, prev)
    else:
        ret = Predicate(node.name, node.children, prev)
    return ret

# convert a clause (in tree structure) to a linked list 
# that will be stored in the KB
def convert_to_clause_list(clause_root):
    head = Clause()
    cur = head
    nodeq = []
    
    nodeq.append(clause_root)
    while nodeq:
        node = nodeq.pop()
        if node.op == '|':
            nodeq.append(node.left)
            nodeq.append(node.right)
        else:
            temp = cur
            cur = convert_to_pred(node, temp)
            cur.head = head
            temp.next = cur
    return head
                    
# tell a KB a sentence of FOL
def tell(kb, line):
    line = line.replace(' ', '')
    start = lp.parse_sentence(line)
    clauses = seperate_clauses(start.left)
    for clause_t in clauses:
        # print("tell clause : ")
#         clause_t.nprint()
#         print()
        
        clause_l = convert_to_clause_list(clause_t)        
        # print_clause(clause_l)
#         print()
        # store in KB
        cur = clause_l.next
        while cur:
            if cur.name not in kb:
                kb[cur.name] = []
            kb[cur.name].append(cur)
            cur = cur.next

            
    return clause_l # an interface to test

# due to specified form of the queries
# directly return the Predicate
def parse_query(line):
    line = line.replace(' ', '')
    start = lp.parse_sentence(line)
    return convert_to_pred(start.left, None)
            
########################### Uinification ###########################
def unify(x, y, s):
    if s is None:
        return None
    elif x is y: # point to the same object (a wrapper around a string)
        return s
    elif isinstance(x, list):
        assert isinstance(y, list)
        assert len(x) == len(y)
        if len(x) == 1:
            return unify(x[0], y[0], s)
        else:
            return unify(x[1:], y[1:], unify(x[0], y[0], s))
    elif x.type == 'var':
        return unify_var(x, y, s)
    elif y.type == 'var':
        return unify_var(y, x, s)
    # constant unify with constant
    elif x.type == 'const':
        if x.value == y.value:
            return s
        else:
            print('different contants: unification failed')
            return None
    else:
        return None

def unify_var(var, x, s):
    if var in s:
        return unify(s[var], x, s)
    elif x in s:
        return unify(var, s[var], s)
    # can a variable be unified with another variable
    else:
        s[var] = x
        return s

def std_var_in_clause(clause, name_gen, map):
    assert isinstance(clause, Clause)
       
    cur = clause.next
    while cur:
        std_var_in_pred(cur, name_gen, map)
        cur = cur.next
    

# map: variable name(string) to variable object, 
# for example: 'a' -> Variable('x')
def std_var_in_pred(pred, name_gen, map):
    assert isinstance(pred, Predicate)
        
    l = pred.args
    for i in range(len(l)):
        if l[i].type == 'var':
            if l[i].value not in map:               
                map[l[i].value] = l[i]
                print('std var: new pair added ', map)
                l[i].value = next(name_gen)
            else: 
                l[i] = map[l[i].value]
    
def subst(s, clause):
    assert isinstance(clause, Clause)
    
    cur = clause.next
    while cur:
        args = cur.args
        for i in range(len(args)):
            if args[i] in s:
                assert args[i].type == 'var'
                args[i] = s[args[i]]
        cur = cur.next
########################### Resolution ###########################
def ask(kb, a):
    na = negate_name(a.name)
    for pred in kb[na]:
        var_name_gen = var_name_generator()
        std_var_in_clause(pred.head, var_name_gen, {})
        print_clause(pred.head)
        sub = unify(a.args, pred.args, {})
        print_subst(sub)

def negate_name(name):
    if name[0] == '-':
        return name[1:]
    else:
        return '-' + name

# walk the clause through the kb
# def resolution(kb, clause):
    
        
    

########################### Utilites ###########################
def var_name_generator():
    name_tab = ['x', 'y', 'z', 'w', 'p', 'q']
    counter = itertools.count(1)
    
    while True:
        num = next(counter)
        stack = []
        name = ''
        while num:
            num -= 1
            stack.append(name_tab[num % 6])
            num //= 6  
        while len(stack):
            name += stack.pop()     
        yield name

def print_clause(head):
    assert isinstance(head, Clause)
    head.print()
    head = head.next
    while head:
        head.print()
        print('<c' + str(head.head.num) + '>', end='')
        if DEBUG:
            print ( '(' + str(id(head) % 1000) + ')', end='' )
        print (' -> ',end='')
        head = head.next
    print('null')

def print_subst(s):
    # assert isinstance(s, dict)
    if s is None:
        print('Not such substitution')
        return
    if s:
        print('{ ', end='')
        for var, val in s.items():
            # assert var.type == 'var'
#             assert val.type == 'const'
            print(var.value + '/' + val.value + ', ', end='')
        print('%c%c }' % (8, 8))
    else: print('{ }')

def traver_kb(kb):
    for k, v in kb.items():
        print ('PREDICATE: ' + k)
        for pred in v:
            print_clause(pred.head)
        print()

def parse_KB(kb, lines):
    for line in lines:
        tell(kb, line)
    
########################### main ###########################

w = ''' (A(x) => B(x)) & (B(x) => C(x)) '''

m = '''Mother(Liz,Charley)
Father(Charley,Billy)
~Mother(x,y) | Parent(x,y)
~Father(x,y) | Parent(x,y)
~Parent(x,y) | Ancestor(x,y)
~(Parent(x,y) & Ancestor(y,z)) | Ancestor(x,z)'''

q = '''A      (Bo      b)
       (A(x, y)    =     > B    (   z))
       Mo      t   her(x,y)'''

# lines = q.splitlines()
# 
# for line in lines:
#     l = line.replace(' ', '')
#     tell(KB, l)

# with open('input.txt', 'r') as f:
#     lines = f.read().splitlines()
#     
#     num_query = int(lines[0])
#     num_kb = int(lines[num_query + 1])
#     kb_start = num_query + 2
#     
#     parse_KB(KB, lines[kb_start:kb_start+num_kb])
#     
# #     traver_kb(KB)
#     
#     for query_line in lines[1:num_query + 1]:
#         query = parse_query(query_line)
#         query.print()
#         print(':')
#         ask(KB,query)
#         print()
    





