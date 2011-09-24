import pickle, ehrparse

with open("data/parse_tree.pickle", "rb") as f:
    rules = pickle.load(f)


def num_constraints(r):
    return len([h for h in r.hypos if type(h) == ehrparse.Constraint])

#print([num_constraints(r) for r in rules])

s = [r for r in rules if num_constraints(r) > 1]

print(len(s))


from translator import *

def func_hypos():
    """This test shows only 3 special predicates appear in hypos, 
    and all the ones without them are function calls."""
    
    hs = []
    for r in rules:
        for h in r.hypos:
            if type(h) != Constraint:
                if type(h) == RemoteAtom:
                    h = h.atom
                hs.append(h)
    
    print(len(hs))
    
    hy = [h for h in hs if h.name!="hasActivated" and h.name !="isDeactivated" and h.name!="canActivate"]
    print(len(hy))
    
    for i in hy:
        print(i)

func_hypos()