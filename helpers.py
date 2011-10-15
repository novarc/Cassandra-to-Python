from typecheck import *
from functools import reduce

##################
# Helper functions
##################

def uniq(seq): # returns unique elements (like set) with order preserved
    seen = set()
    return [ x for x in seq if x not in seen and not seen.add(x) ]

def identical(seq): # check if all elements in a sequence are identical
    if len(seq) > 1:
        return reduce(lambda a, b: (b, a[0]==b), seq, (seq[0], None))[1]
    return True

def any_eq(val, seq):
    for k in seq:
        if k == val:
            return True
    return False

@typecheck
def str_substitue(s: str, char_to_sub: lambda s: len(s)==1, sub_with: str):
    if type(s) != str: raise TypeError("s must be of type str")
    return "".join(sub_with if c == char_to_sub else c for c in s)

def h2u(s): # convert hyphens to underscores
    return str_substitue(s, '-', '_')

@typecheck
def prefix_lines(s: str, prefix: str):
    return "".join( prefix + line + "\n" for line in s.splitlines() )

def tab(s, indentation_level=1):
    return prefix_lines(s, '    '*indentation_level)

def separate(l, cond):
    return [x for x in l if cond(x) == True], [x for x in l if cond(x) == False]

print(separate([1,2,3,4], lambda x: x % 2 ==0))