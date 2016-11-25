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
    
    # common call: cl.copy(pred.head, pred)
    def copy(self, pred=None):  
        head = Clause()
        cur = head
        cur_origin = self.next
        while cur_origin:
#             cur_origin.print()
            temp = cur
            cur = cur_origin.copy()
            if cur_origin is pred: # new copy of the specified predicate
                pred = cur
            cur.prev, cur.head = temp, head
            temp.next = cur  
            cur_origin = cur_origin.next
        if pred:
            return head, pred
        else:
            return head
    
    def merge_with(self, rhs):
        assert isinstance(rhs, Clause)
        
        cur, tail = self, None
        while cur:
            tail, cur = cur, cur.next
        tail.next = rhs.next
        if rhs.next:
            rhs.next.prev = tail 
    
    def print(self):
        print('CLAUSE ' + str(self.num) , end='')
        if DEBUG:
            print('<' + str(id(self) % 1000) + '>', end='')
        print(": ", end='')
    

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
            print('unify: different contants, unification failed')
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
#                 print('std var: new pair added ', map)
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
    if a.name not in kb:
        return False
    for pred in kb[a.name]:
#         print_clause(pred.head)
        if unify(a.args, pred.args, {}) is None:
            continue                
        to_resolve, to_unify = pred.head.copy(pred) # clause and the term
        var_name_gen = var_name_generator()
        resolve_clause_and_term(to_resolve, to_unify, a, var_name_gen)
        if to_resolve.next == None:
            return True
        elif resolution(kb, to_resolve, set()):
            return True
    return False

##
#  precondition: to_unify and ~alpha are resolvable
#  unify the list of to_unify and alpha, remove to_unify from to_resolve 
#  substitute the clause to_resolve
##
def resolve_clause_and_term(to_resolve, to_unify, alpha, name_gen):    
    std_var_in_clause(to_resolve, name_gen, {})
    print ('---unifying: term ', end='')
    alpha.print()
    print (' and clause ', end='')
    print_clause(to_resolve) #
    print ('---')
    sub = unify(to_unify.args, alpha.args, {}) # first two args order matters?
    print_subst(sub) #
    to_unify.remove_self()
    subst(sub, to_resolve)
    print_clause(to_resolve) #
    print()
    return sub

rec_count = itertools.count()
# walk the clause through the kb
def resolution(kb, clause, met):
    cnt = next(rec_count)
    if cnt == 200:
        print('@@@@@@@@@@@@ RECURSION END @@@@@@@@@@@@')
        quit()
        
    term = clause.next    
    if not term: # no term left, implying empty clause
        return True
        
        # prevent loop from predicate perspective
#     pred_id = predicate_to_tuple(term) # a representation to identify a predicate
#     if pred_id:
#         if pred_id in met:
#             print('*** Predicate Met again ***')
#             print_pred_id(pred_id); print()
#             return False
#         else:
#             met.add(pred_id)
    
    # prevent loop from clause perspective
    clause_id = clause_to_tuple(clause)
    if clause_id in met:
        print('*** Clause Met again ***')
        return False        
    else:
        print ('%%%%%% clause put into map %%%%%%')
        met.add(clause_id) ##

    nt = negate_name(term.name)
    if nt not in kb:
        return False
    is_resolvable = False
    for pred in kb[nt]:
        if unify(term.args, pred.args, {}) is None:
            print('failed terms: ', end='')
            term.print(); print('   -   ', end=''); pred.print()
            print('\n')
            continue
            
        is_resolvable = True
        print('-- about to unify two clauses --')
        new_clause, new_term = clause.copy(term) # copy from the clause    
        to_resolve, to_unify = pred.head.copy(pred) # copy from the KB
        var_name_gen = var_name_generator()
        
        std_var_in_clause(new_clause, var_name_gen, {})
        s = resolve_clause_and_term(to_resolve, to_unify, new_term, var_name_gen)
        new_term.remove_self()
        subst(s, new_clause)
        new_clause.merge_with(to_resolve)
        print('-- after unifying two clauses --')
        print_clause(new_clause)
        print()
#         met.add(clause_id) ##
        # recursively solve it        
        if resolution(kb, new_clause, met):
            return True
#         met.remove(clause_id) ##
    if not is_resolvable:
        return False
    

def negate_name(name):
    if name[0] == '-':
        return name[1:]
    else:
        return '-' + name    
    
########################### Utilites ###########################
# change a clause to a hashable representation
# not so efficient
def clause_to_tuple(clause):
    assert isinstance(clause, Clause)
    
    cur = clause.next
    l = []
    
    while cur:
        l.append(predicate_to_tuple(cur))
        cur = cur.next
    
    return tuple(l)

# change a predicate to a hashable representation
def predicate_to_tuple(pred):
    assert isinstance(pred, Predicate)
    
    l = []
    count = 0
    
    l.append(pred.name)
    for arg in pred.args:
        if arg.type == 'var':
            l.append('v')
        else:
            count = count + 1
            l.append(arg)
    # if count:
#         print('$$$$$' + str(tuple(l)) + '$$$$$')
    return tuple(l)
    # else:
#         return None

def print_pred_id(pred_id):
    print('PREDICATE ID: ')
    for e in pred_id:
        if isinstance(e, str):
            print(e, end='')
        elif e.type == 'const':
            e.nprint()
        print(' ', end='')
    print()

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
        if DEBUG:
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
            print(var.value, end='')
            if DEBUG: print('<' + str(id(var) % 1000) + '>', end='')
            print('/', end='')
            print(val.value,end='')
            if DEBUG: print('<' + str(id(val) % 1000) + '>', end='')
            print(', ', end='')
        print('%c%c }' % (8, 8))
    else: print('{ }')

def traver_kb(kb):
    for k, v in kb.items():
        print ('PREDICATE: ' + k)
        if DEBUG: print(v)
        for pred in v:
            print_clause(pred.head)
        print()

def parse_KB(kb, lines):
    for line in lines:
        tell(kb, line)
    
########################### main ###########################

# lines = q.splitlines()
# 
# for line in lines:
#     l = line.replace(' ', '')
#     tell(KB, l)

out = open('output.txt', 'w')
if not out:
    print('failed opening output.txt')
    quit()

with open('input.txt', 'r') as f:
    lines = f.read().splitlines()
    
    num_query = int(lines[0])
    num_kb = int(lines[num_query + 1])
    kb_start = num_query + 2
    
    parse_KB(KB, lines[kb_start:kb_start+num_kb])
    
    print('--------------KB----------------')
    traver_kb(KB)
    
    print('--------------Query----------------')
    for query_line in lines[1:num_query + 1]:
        query = parse_query(query_line)
        query.print()
        print(':')
        if ask(KB,query):
            print('**************True**************')
            out.write('TRUE\n')
        else:
            print('**************False**************')
            out.write('FALSE\n')
        print()
    
out.close()
