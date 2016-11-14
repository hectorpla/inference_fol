import logicparser as lp

d = '''Dog(D)
       Owns(Jack,D)
       Dog(y) & Owns(x,y) => AnimalLover(x)
       ~(AnimalLover(x) & Animal(y) & Kills(x,y))
       Kills(Jack,Tuna) | Kills(Curiosity,Tuna)
       Cat(Tuna)
       Cat(x)   => Animal(x)
       ~Kills(Curiosity, Tuna) '''

lines = d.splitlines()

for line in lines:
    t = lp.parse_sentence(line)
    # print(type(t))
#     elim_implication(t)
    lp.push_negation_inward(t)
    lp.printTree(t)
    print()
