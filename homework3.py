########################### KB's data structure ###########################
import itertools
counter = itertools.count()
# head of a clause in the KB
class Clause:
    def __init__(self):
        self.num = next(counter)
        self.next = None
    
    def print(self):
        print('CLAUSE' + str(self.num) + ": ", end='')
    

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

# convert a clause to a linkedlist that will be stored in the KB
def convert_clause(clause_root):
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
        print("tell clause : ")
        clause_t.nprint()
        print()
        
        clause_l = convert_clause(clause_t)        
        print_clause(clause_l)
        print()
        # store in KB
        # cur = clause_l
#         while cur:
#             if cur.name not in kb:
#                 kb[cur.name] = []
#             kb[cur.name].append(cur)
            
        
    
########################### Utilites ###########################
def print_clause(head):
    assert isinstance(head, Clause)
    while head:
        head.print(), print ( '(' + str(id(head) % 1000) + ') -> ', end='' )
        head = head.next
    print('null')

########################### main ###########################

w = ''' (A(x) => B(x)) & (B(x) => C(x)) '''

m = '''Mother(Liz,Charley)
Father(Charley,Billy)
~Mother(x,y) | Parent(x,y)
~Father(x,y) | Parent(x,y)
~Parent(x,y) | Ancestor(x,y)
~(Parent(x,y) & Ancestor(y,z)) | Ancestor(x,z)'''

lines = w.splitlines()

for line in lines:
    tell(KB, line)


# with open('input.txt', 'r') as f:
#     lines = f.read().splitlines()
# 
#     for line in lines:
#         t = lp.parse_sentence(line)
#         lp.printTree(t)
#         print()

