# Copyright (C) 2011-2014 Arjun G. Menon
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

"""Generates Python snippets for Datalog-with-constraints hypotheses.

Hypotheses form the latter part of horn clauses (ie. after the ->).
They are the "conditions" that have to be satisfied for a horn clause to be true.

Hypotheses constitute the bulk of the translation work.
"""

from auxiliary import *
from ast_nodes import *
from . hand_translations import hand_translations

from string import Template

class StopTranslating(Exception):
    def __init__(self, rule, reason):
        self.rule, self.reason = rule, reason

class CountFunctions:
    funcs = []

def loc_trans(loc):
    if loc == '"PDS"':
        loc = 'pds'
    elif loc == '"Spine"':
        loc = 'spine'
    elif loc == '"RA-ADB"':
        loc = 'ra'
    
    return 'ehr.'+loc

class HypothesesTranslator(object):
    stop_count = 0

    def __init__(self, rule):
        self.rule = rule
        self.external_vars = None # initialized by derived class, will become dict
    
    def __repr__(self):
        return repr(self.rule)
    
    def stopTranslating(self, reason):
        HypothesesTranslator.stop_count += 1
        return StopTranslating(self.rule, "[%d] " % HypothesesTranslator.stop_count + reason)
    
    @typecheck
    def build_param_bindings(self, params: list_of(str)) -> list:
        """Returns a set of constraint code generation functions which binds role parameters to external variables"""
        constraints = []
        
        for var_name in params:
            
            def param_binding(vn):
                return lambda vd = { vn : vn } : "%s == self.%s" % (vd[vn], vn)
            
            constraints.append( ({var_name}, param_binding(var_name)) )
        
        return constraints
    
    def substitution_func_gen(self, variables, code):
        """Takes a Python string representing a fragment of code, contating unbound variables.
        Substitutes unbounds if possible, with variables from self.external_vars
        The remaining unbound variables are returned along with a lambda that takes 
        as argument a dictionaty mapping the remaining unbounds to substition code.

        Sample Input (parameters):
            variables = ['x', 'org', 'pat']
            code = "deactivate(hasActivated, {x}, Spine_emergency_clinician({org}, {pat}))  # S3.2.3"

        Sample Output (return values):
            # only 'pat' remainds unbound now, as 'x' & 'org' were found in self.external_vars
            return_1 = {'pat'}
            return_2 = "deactivate(hasActivated, subj, Spine_emergency_clinician(self.org, pat))  # S3.2.3"
        """
        
        #print(self.rule.name, self.external_vars)
        ext, rest = separate(variables, lambda v: v in self.external_vars.keys())
        
        substitution_dict = dict()
        substitution_dict.update( { e : self.external_vars[e] for e in ext } )
        substitution_dict.update( { r : p(r) for r in rest } )
        
        new_format_string = code.format(**substitution_dict)
        
        return ( set(rest), lambda vd = { r : r for r in rest }: new_format_string.format(**vd) )
    
    @typecheck
    def build_constraint_bindings(self, c: Constraint):
        """ returns a special data structure of the form ({ set of bound variable names }, lambda vd: ...)
            The lambda when called returns a string which is translation of the constraint to Python.
            * the first dict is a list of variables names that are bound (or affected) by the constraint 
            * vd is a dictionary where you can substitute these variable names with other variable names 
              of your choice (for example substitute "cli" with "self.cli"). The form of the vd is {"cli":"self.cli"}
        """
        
        if c.op == 'in':
            
            if type(c.right) == Range and type(c.right.start) == Variable and type(c.right.end) == Variable:
                # it's of the form "something in [lower, upper]"
                lower, upper = h2u(c.right.start.name), h2u(c.right.end.name)
                
                # Current-time() in [lower, upper]
                if type(c.left) == Function:
                    func_name = h2u(repr(c.left))
                    
                    if len(c.left.args):
                        raise self.stopTranslating("can't handle 'in' operator - function with arguments: %r" % c.left)
                    
                    return self.substitution_func_gen([lower, upper],"%s in vrange({%s}, {%s})" % (func_name, lower, upper))
                
                # var in [lower, upper]
                if type(c.left) == Variable:
                    vn = h2u(repr(c.left))
                    
                    return self.substitution_func_gen([vn, lower, upper], "{%s} in vrange({%s}, {%s})" % (vn, lower, upper))
            
            elif type(c.right) == Function:
                func_name = h2u(str(c.right.name))
                func_args = [repr(arg) for arg in c.right.args]
                
                if type(c.left) == Variable:
                    vn = h2u(repr(c.left))
                    return self.substitution_func_gen( [vn] + func_args, 
                        "{%s} in %s" % (vn, func_name) + '(' + ', '.join('{'+a+'}' for a in func_args) + ')')
            
            elif type(c.right) == Variable:
                if type(c.left) == Variable:
                    cl, cr = h2u(repr(c.left)), h2u(repr(c.right))
                    return self.substitution_func_gen([cl, cr], "{%s} in {%s}" % (cl, cr))
        
        elif c.op == '=' or c.op == '<' or c.op == '!=':

            op = "==" if c.op == '=' else c.op
            
            cl, cr = h2u(repr(c.left)), h2u(repr(c.right))

            if type(c.left) == Variable and type(c.right) == Constant:
                return self.substitution_func_gen([cl], p(cl) + ' ' + op + ' ' + cr)

            elif type(c.left) == Variable and type(c.right) == Variable:
                return self.substitution_func_gen([cl, cr], p(cl) + ' ' + op + ' ' + p(cr))
            
            elif type(c.left) == Function and type(c.right) == Variable:
                func_name, func_args = h2u(c.left.name), [str(a) for a in c.left.args]
                return self.substitution_func_gen([cr]+func_args, func_name + 
                            '(' + ", ".join(p(a) for a in func_args) + ') ' + op + ' ' + p(cr))
            
            elif type(c.left) == Variable and type(c.right) == Tuple:
                lhs = repr(c.left)
                tuple_elems = [h2u(repr(elem)) for elem in c.right.elems]
                return self.substitution_func_gen([lhs]+tuple_elems, 
                        'compare_seq(' + p(lhs) + ', ' + '(' + ', '.join(p(elem) for elem in tuple_elems) + '))' )
        
        raise self.stopTranslating("could not translate constraint: " + repr(c))
    
    
    def build_canAc_bindings(self, canAc):
        subj, role = canAc.args
        
        bound_vars = [var.name for var in [subj] + role.args]
        
        loc = ''
        if canAc.issuer:
            loc = loc_trans( repr(canAc.issuer) )+'.'
        if canAc.location:
            loc = loc_trans( repr(canAc.location) )+'.'
        
        return self.substitution_func_gen(bound_vars, "canActivate({}, {}{}({}))".format(
            p(bound_vars[0]), loc, h2u(role.name), ", ".join(p(v) for v in bound_vars[1:])
            ) )
    
    def translate_hasActivated(self, conditionals, hasAcs, wrapper):
        if len(hasAcs) == 1:
            hasAc = hasAcs[0]
            role = hasAc.args[1]
            hasAc_subj = repr(hasAc.args[0])
            role_name = role.name
            role_params = [repr(param) for param in role.args]
            
            # turn role_params into a set
            if len(role_params) != len(set(role_params)):
                raise self.stopTranslating("duplicate role params in %s" + repr(role_params))
            else:
                role_params = set(role_params)
            
            conditionals.append( 'role.name == "%s"' % role_name )
            
            # find which role params already exist in external_vars
            existing_role_params = role_params & set(self.external_vars)
            
            # create conditionals for existing role params
            conditionals.extend([ "role."+param + " == " + self.external_vars[param] for param in existing_role_params ])
            
            role_param_mapping = { rp : "role."+rp for rp in role_params }
            self.external_vars.update( role_param_mapping )
            
            if hasAc_subj in set(self.external_vars):
                conditionals.append( "subj == " + self.external_vars[hasAc_subj] )
            self.external_vars.update( { hasAc_subj : 'subj' } )
            
            loc = loc_trans( repr(hasAc.location) ) +'.' if hasAc.location else ''
            
            tr = "return " + wrapper[0] 
            tr += '[' if wrapper[0] == "len(" else '{'
            tr += "\n    $group_key for subj, role in %shasActivated if \n    " % loc
            ending = "\n"
            ending += '])' if wrapper[0] == "len(" else '}' + wrapper[1]
            
            return tr, ending
            
        elif len(hasAcs) == 2:
            h1, h2 = hasAcs
            subj1, subj2 = str(h1.args[0]), str(h2.args[0])
            role1, role2 = h1.args[1], h2.args[1]
            
            conditionals.append( 'role1.name == "%s"' % role1.name )
            conditionals.append( 'role2.name == "%s"' % role2.name )
            
            if subj1 in set(self.external_vars):
                conditionals.append( "subj1 == " + self.external_vars[subj1] )
            if subj2 in set(self.external_vars):
                conditionals.append( "subj2 == " + self.external_vars[subj2] )
            
            role1_args, role2_args = [str(a) for a in role1.args], [str(a) for a in role2.args]
            conditionals.extend([ "role1."+p + " == " + self.external_vars[p] for p in (set(role1_args) & set(self.external_vars)) ])
            conditionals.extend([ "role2."+p + " == " + self.external_vars[p] for p in (set(role2_args) & set(self.external_vars)) ])
            
            self.external_vars.update( { subj1 : 'subj1' } )
            self.external_vars.update( { subj2 : 'subj2' } )
            self.external_vars.update( { rp : "role1."+rp for rp in role1_args } )
            self.external_vars.update( { rp : "role2."+rp for rp in role2_args } )
            
            loc1 = loc_trans( repr(h1.location) )+'.' if h1.location else ''
            loc2 = loc_trans( repr(h2.location) )+'.' if h2.location else ''
            
            return "return %s{\n    $group_key for (subj1, role1) in %shasActivated for (subj2, role2) in %shasActivated if \n    " % (
                                                                                            wrapper[0], loc1, loc2), "\n}" + wrapper[1]
            #print("Rule with 2 hasActivates:", self.rule.name)
        
        elif len(hasAcs) == 0:
            return "return (\n    ", "\n)"
            #raise self.stopTranslating("a rule with no hasActivates")
        
        else:
            raise self.stopTranslating("Not implemented: %d hasAcs in a rule." % len(hasAcs))
    
    def translate_canActivated(self, conditionals, canAcs):
        for (canAc_vars, canAc_cond_func) in map(self.build_canAc_bindings, canAcs):
            if(len(canAc_vars)):
                pass#warn("check "+self.rule.name+" whether wildcards in canActivate are okay")
            vd = { canAc_var : "Wildcard()" for canAc_var in canAc_vars }
            conditionals.append( canAc_cond_func(vd) )
    
    def handle_single_count_function(self, funcs, countf_wildcard):
        for f in (f for f in funcs if f.name in CountFunctions.funcs):
            f_return = str(f.args[0])
            args = [str(a) for a in f.args[1:]]
            
            unbound_vars, code_gen = self.substitution_func_gen(args, 
                h2u(f.name) + '(' + ", ".join(p(str(a)) for a in args) + ')' )
            
            if unbound_vars:
                if countf_wildcard:
                    self.external_vars.update( { v : "Wildcard()" for v in unbound_vars } )
                else:
                    raise self.stopTranslating("unbound vars %r in %r" % (sorted(unbound_vars), f))
            
            # create a mapping from the return value of f to its code
            self.external_vars.update( { f_return : code_gen() } )
            
            if unbound_vars and countf_wildcard:
                for v in unbound_vars:
                    self.external_vars.pop(v)
            
            # remove f from funcs:
            funcs.remove(f)
    
    def handle_constraints(self, conditionals, ctrs):
        for (remaining_ctr_vars, ctr_cond_func) in map(self.build_constraint_bindings, ctrs):
            if not remaining_ctr_vars: # remaining_ctr_vars must be empty
                conditionals.append( ctr_cond_func() )
            else:
                raise self.stopTranslating("unable to bind vars %s in constraint %s" 
                                        % ( sorted(remaining_ctr_vars), ctr_cond_func() ))
    
    def handle_other_functions(self, conditionals, funcs):
        for f in funcs:
            f_args = [str(a) for a in f.args]
            
            unbound_vars, code_gen = self.substitution_func_gen(f_args, 
                h2u(f.name) + '(' + ", ".join(p(str(a)) for a in f_args) + ')' )
            
            if unbound_vars:
                raise self.stopTranslating("unbound vars in %s" % repr(f))
            
            conditionals.append( code_gen() )
    
    def translate_group_rules(self, tr, group_key):
        if group_key:
            group_key = str(group_key)
            if not group_key in set(self.external_vars):
                raise self.stopTranslating("could not find %s in %s" % (group_key, set(self.external_vars)))
            group_key = self.external_vars[group_key]
        else:
            group_key = True
        
        return Template(tr).safe_substitute(group_key = group_key)
    
    @typecheck
    def translate_hypotheses(self, wrapper:[str,str]=['',''], pre_conditional:str='', group_key=None, countf_wildcard=False) -> lambda t: t:
        rule_repr_without_name = repr(self.rule.concl)+ ' <-\n' + ', \n'.join([repr(i) for i in self.rule.hypos])
        rule_comment = "#\n" + "".join( "# %s\n" % l for l in rule_repr_without_name.split('\n') ) + "#\n"
        
        hypo_trans = "return {}" # untranslated hyptheses return this
        
        try:
            ctrs, canAcs, hasAcs, funcs = separate(self.rule.hypos, 
                                                  lambda h: type(h) == Constraint, 
                                                  lambda h: h.name == "canActivate",
                                                  lambda h: h.name == "hasActivated")
            
            conditionals = []
            
            if pre_conditional:
                conditionals.append(pre_conditional)
            
            # translate hasActivated:
            tr, ending = self.translate_hasActivated(conditionals, hasAcs, wrapper)
            
            # translate canActivated:
            self.translate_canActivated(conditionals, canAcs)
            
            # Handle the special case of (only) 1 count function invoked in a rule:
            self.handle_single_count_function(funcs, countf_wildcard)
            
            # handle constraints:
            self.handle_constraints(conditionals, ctrs)
            
            # handle functions:
            self.handle_other_functions(conditionals, funcs)
            
            # for group<x> rules:
            tr = self.translate_group_rules(tr, group_key)
            
            # add conditionals to 'tr':
            if len(conditionals):
                tr += " and \n    ".join( sorted(conditionals) )
            
            hypo_trans = tr + ending
        
        except StopTranslating as st:
            if self.rule.name in hand_translations:
                rule_comment += "# Using a hand translation, because this rule could not be translated automatically.\n# Reason: %s\n#\n" % st.reason
                hypo_trans = hand_translations[self.rule.name]
            else:
                rule_comment += "# Unable to translate this rule automatically.\n# Reason: %s\n#\n" % st.reason
                rule_comment += "# Please provide a hand translation! (TODO/FIXME)\n#\n"
                print("Please provide a hand translation for: %s\n" % self.rule.name)
                print("Reason:", st.reason, "\n\n", self.rule, "\n")
        
        return rule_comment + hypo_trans
