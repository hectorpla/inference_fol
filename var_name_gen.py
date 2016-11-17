# infinite variable name generator

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

varname_gen = var_name_generator()
for _ in range(20):
    print (next(varname_gen))