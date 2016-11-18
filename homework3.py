########################### KB's data structure ###########################
import itertools
counter = itertools.count()
# head of a clause in the KB
class Clause:
    def __init__(self):
        self.num = next(counter)
        self.next = None
    
    def print(self):
        print('CLAUSE ' + str(self.num) + ": ", end='')
    

# a link in a clause (different from that in the parser)
class Predicate:
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.head = None
        self.next = None
    
    def print(self):
        print('[' + self.name + ': ', end='')
        for child in self.args:
            child.nprint(), print(' ', end='')
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
def convert_to_pred(node):
    if node.type == 'negop':
        pred_node = node.left
        ret = Predicate('-' + pred_node.name, pred_node.children)
    else:
        # print('hey')
        ret = Predicate(node.name, node.children)
    return ret

# convert a clause (in tree structure) to a linked list 
# that will be stored in the KB
def convert_to_clause(clause_root):
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
            cur = convert_to_pred(node)
            cur.head = head
            temp.next = cur
    return head
                    
# tell a KB a sentence of FOL
def tell(kb, line):
    start = lp.parse_sentence(line)
    clauses = seperate_clauses(start.left)
    for clause_t in clauses:
        # print("tell clause : ")
#         clause_t.nprint()
#         print()
        
        clause_l = convert_to_clause(clause_t)        
        # print_clause(clause_l)
#         print()
        # store in KB
        # cur = clause_l
#         while cur:
#             if cur.name not in kb:
#                 kb[cur.name] = []
#             kb[cur.name].append(cur)
    return clause_l # an interface to test
            
########################### Uinification ###########################
def unify(x, y, s):
    if s is None:
        # test out put
        print('unification failed')
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
    else:
        return None

def unify_var(var, x, s):
    if var in s:
        return unify(s[var], x, s)
    elif x in s:
        return unify(var, s[var], s)
    else:
        s[var] = x
        return s

# def std_var_in_clause(clause, name_gen, map):
#     assert isinstance(clause, Clause)
#     
#     cur = clause.next
#     while cur:
#         std_var_in_pred(cur, name_gen, map)
#     
# 
# def std_var_in_pred(pred, name_gen, map):
#     assert isinstance(pred, Predicate)
#     
#     l = pred.args
#     for i in range(len(l)):
#         if l[i].type == 'var':
#             if l[i] not in map:
#                 map[l[i].value] = next(name_gen)
#             l[i].value = map[l[i].value]
    
    
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
        print ( '(' + str(id(head) % 1000) + ') -> ', end='' )
        head = head.next
    print('null')

def print_subst(s):
    print('{ ', end='')
    for var, val in s.items():
        # assert var.type == 'var'
#         assert val.type == 'const'
        print(var.value + '/' + val.value + ', ', end='')
    print('%c%c }' % (8, 8))
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
#     print(l)
#     tell(KB, l)


# with open('input.txt', 'r') as f:
#     lines = f.read().splitlines()
# 
#     for line in lines:
#         t = lp.parse_sentence(line)
#         lp.printTree(t)
#         print()

