from model import Model

test = Model("test")
#print(test)
test.add_actions('a1')
cons = ('c2','c3')
test.add_consequences(*cons)
#print(test)
test.add_mechanisms('c2','a1','c3')
#print(test)
#test.remove_mechanisms("a2","a2","a3","a5") 
test.set_utility('c2',4)
test.export()