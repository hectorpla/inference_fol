import homework3 as hw3
import itertools

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

def std_var_in_clause(clause, name_gen, map):
    assert isinstance(clause, hw3.Clause)
    
    cur = clause.next
    while cur:
        std_var_in_pred(cur, name_gen, map)
        cur = cur.next

# map: variable name(string) to variable object, 
# for example: 'a' -> Variable('x')
def std_var_in_pred(pred, name_gen, map):
    assert isinstance(pred, hw3.Predicate)
    
    l = pred.args
    for i in range(len(l)):
        if l[i].type == 'var':
            if l[i].value not in map:               
                map[l[i].value] = l[i]
                print('std var: new pair added ', map)
                l[i].value = next(name_gen)
            else: 
                l[i] = map[l[i].value]

w = ''' Bird(x)
        Bird(Kak)
        Mother(x,y)
        Mother(Salsa,John) 
        Love(x, Rose)
        Love(Jack,y)
        '''
# variable standardization
q = '''Sells(Bob, x)
       Sells(x, Coke)
       Kicks(a, Football)
       Kicks(Even, a)
       Beats(Donnie, x, y, z)
       Beats(x, Kimura, Santos, Clinton)
       A(x, y, z)
       A(y, x, Bob)'''

# between constant
p = '''Tall(Bob)
       Tall(Bob)
       Fakes(Tony, Gold)
       Fakes(x, Gold)'''

# can't unify
e = ''' K(A)
        K(B)
        K(B,C)
        K(M,N)'''

# compound clause
o = ''' A(x) | B(x)
        B(David)
        D(y) | C(x,y)
        C(x, Wenger)'''

lines = o.splitlines()

cls = []

for line in lines:
    l = line.replace(' ', '')
    print(l)
    cl = hw3.tell(hw3.KB, l)    
    hw3.print_clause(cl)
    cls.append(cl)


l = [cl.next.args for cl in cls]


for i in range(0, len(cls), 2):
    print ('\nunification: ')
    var_name_gen = var_name_generator()
    std_var_in_clause(cls[i], var_name_gen, {})
    hw3.print_clause(cls[i])
    std_var_in_clause(cls[i+1], var_name_gen, {})
    hw3.print_clause(cls[i+1])
    
    sub = hw3.unify(l[i],l[i+1], {})
    hw3.print_subst(sub)