# Copyright (C) 2011-2013 Arjun G. Menon
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from datetime import datetime
from functools import reduce
from typecheck import typecheck, list_of

"""
Auxiliary Classes & Functions
"""

#####################
# Cassandra-specific
#####################

class  Role(object):
    def __init__(self, name, **params):
        self.name = name
        self.__dict__.update(params)
        self.prms = list(params)

#    def __eq__(self, other):
#        if self.name == other.name and self.args == other.args:
#            self_params = [self.__dict__[p] for p in self.args]
#            other_params = [other.__dict__[p] for p in other.args]
#            
#            matching_params = [a for (a, b) in zip(self_params, other_params)]
#            if len(matching_params) == len(other_params):
#                return True
#        return False

    def __repr__(self):
        r = 'Role(name = ' + repr(self.name)
        a = ', '.join( prm + ' = ' + repr(self.__dict__[prm]) for prm in self.prms )
        return ( (r + ', ' + a) if a else r ) + ')'

def canActivate(subject, role):
    return role.canActivate(subject)

def pi7_1(obj):
    pass

def Current_time():
    return datetime.utcnow()


#########################
# Generic Helper Classes
#########################

class anyset(object): # because python sets don't allow unhashable types like other sets & dicts...
    def __init__(self):
        self.list_of_objects = []
    def add(self, obj):
        if not any_eq(obj, self.list_of_objects):
            self.list_of_objects.append(obj)
#    def __iter__(self):
#        return self
#    def __next__(self):
#        for i in self.list_of_objects:
#            yield i
    def __iter__(self):
        class ListIterator:
            def __init__(self, me):
                self.me = me
                self.pos = 0
            def __iter__(self):
                return self
            def __next__(self):
                if self.pos == len(self.me):
                    raise StopIteration
                else:
                    item = self.me[self.pos]
                    self.pos += 1
                    return item
        return ListIterator(self.list_of_objects)

class vrange(object):
    def __init__(self, start, end):
        self.start, self.end = start, end
    def __contains__(self, val):
        if not (val >= self.start and val <= self.end):
            #raise CassandraException("test failed: %r is not in [%r, %r]" % (val, self.start, self.end))
            return False
        return True

class Wildcard(object):
    def __init__(self):
        pass
    def __eq__(self, other):
        return True

class Equals(object):
    def __init__(self, entity):
        self.entity = entity
    def __eq__(self, other):
        return self.entity == other


###################
# Helper Functions
###################

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
def str_substitute(s: str, char_to_sub: lambda s: len(s)==1, sub_with: str):
    if type(s) != str: raise TypeError("s must be of type str")
    return "".join(sub_with if c == char_to_sub else c for c in s)

def h2u(s): # convert hyphens to underscores
    return str_substitute(s, '-', '_')

@typecheck
def prefix_lines(s: str, prefix: str):
    return "".join( prefix + line + "\n" for line in s.splitlines() )

def tab(s, indentation_level=1):
    return prefix_lines(s, '    '*indentation_level)

def separate(alist, *conds):
    """ Examples:
     >  print(separate([1,2,3,4], lambda x: x % 2 ==0))
     >  ([2, 4], [1, 3])
     >  print( separate(range(1,16), lambda x: x % 2 ==0, lambda x: x % 3 ==0) )
     >  ([2, 4, 6, 8, 10, 12, 14], [3, 9, 15], [1, 5, 7, 11, 13]) """
    
    cats = []
    rest = alist
    for cond in conds:
        this, rest = [x for x in rest if cond(x) == True], [x for x in rest if cond(x) == False]
        cats.append(this)
    return tuple(cats+[rest])

def p(s):
    return '{' + s + '}'

def compare_seq(a, b):
    """Compare sequences containing Wilcard() objects.
    Wildcard objects, as their names suggest, are treated as wildcards.

    Note: Python supports sequence type comparison. This function simply 
    when used in conjuction with the Wildcard class, adds wildcard support.
    """

    if len(a) != len(b):
        return False
    for i, j in zip(a, b):
        if isinstance(i, Wildcard) or isinstance(j, Wildcard):
            continue
        if i != j:
            return False
    return True

def untranslated(obj):
    return "\n" + prefix_lines("untranslated:\n" + repr(obj), "#")

@typecheck
def warn(message : str):
    print(message)
