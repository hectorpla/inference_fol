########################### KB's data structure ###########################
# a link in a clause (different from that in the parser)
class Predicate:
    __init__(self, name, args):
        self.name = name
        self.args = args
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
def convert_pred(node):
    if node.type == 'negop':
        pred_node = node.left
        ret = Predicate('-' + pred_node.name, pred_node.children, True)
    else:
        ret = Predicate(node.name, node.children, False)
    return ret

# convert a clause to a linkedlist that will be stored in the KB
def convert_clause(clause_root):
    head = None, cur = None
    nodeq = []
    
    while nodeq:
        node = nodeq.pop()
        if node.op == '|':
            nodeq.append(node.left)
            nodeq.append(node.right)
        else:
            if head == None:
                head = convert_pred(node)
                cur = head
            else:
                temp = cur
                cur = convert_pred(node)
                temp.next = cur
    return head
                    
# tell a KB a sentence of FOL
def tell(kb, line):
    start = lp.parse_sentence(line)
    clauses = seperate_clauses(start->left)
    for clause_t in clauses:
        clause_l = convert_clause(clause_t)
        print_clause(clause_l)
        
    
########################### Utilites ###########################
def print_clause(head):
    while head:
        head.print(), print ( '(' + id(head) + ') -> ', end='' )
    print('null')

########################### main ###########################

w = ''' (A(x) => B(x)) & (B(x) => C(x)) '''

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

