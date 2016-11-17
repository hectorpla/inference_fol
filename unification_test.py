import homework3 as hw3

w = ''' Bird(x)
        Bird(Kak)
        Mother(x,y)
        Mother(Salsa,John) 
        Love(x, Rose)
        Love(Jack,y)
        Sells(Bob, x)
        Sells(x, coke)'''
        
lines = w.splitlines()

cls = []

for line in lines:
    l = line.replace(' ', '')
    print(l)
    cl = hw3.tell(hw3.KB, l)
    hw3.print_clause(cl)
    cls.append(cl)

# l1 = cls[0].next.args
# l2 = cls[1].next.args

l = [cl.next.args for cl in cls]
# print(l)

# sub = hw3.unify(l[0],l[1], {})
# hw3.print_subst(sub)
# sub = hw3.unify(l[2],l[3], {})
# hw3.print_subst(sub)
# sub = hw3.unify(l[4],l[5], {})
# hw3.print_subst(sub)

for i in range(0, len(cls), 2):
    sub = hw3.unify(l[i],l[i+1], {})
    hw3.print_subst(sub)