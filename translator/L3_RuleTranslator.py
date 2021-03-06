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

"""Translates Cassandra EHR rules such as 
   canActivate, canDeactivate, permits;
   as well as function predicates."""

from . L4_HypothesesTranslator import *

class SpecialPredicates:
    prmts = "permits"        # 1. permits(e,a) indicates that the entity e is permitted to perform action a.
    canAc = "canActivate"    # 2. canActivate(e, r) indicates that the entity e can activate role r.
    hasAc = "hasActivated"   # 3. hasActivated(e, r) indicates that the entity e has currently activated role r.
    canDc = "canDeactivate"  # 4. canDeactivate(e1,e2, r) indicates that e1 can deactivate e2's role r (if e2 has really currently activated r).
    isDac = "isDeactivated"  # 5. isDeactivated(e, r) indicates that e's role r shall be deactivated as a consequence of another role deactivation (if e has really currently activated r).
    canRC = "canReqCred"     # 6. canReqCred(e1,e2.p(~e)) indicates that e1 is allowed to request and receive credentials asserting p(~e) and issued by e2.
    
    @staticmethod
    def list_all():
        return [SpecialPredicates.prmts, SpecialPredicates.canAc, SpecialPredicates.hasAc,
                SpecialPredicates.canDc, SpecialPredicates.isDac, SpecialPredicates.canRC]
    
    @staticmethod
    def separate(rules, predicates):
        #e.g. prmts, canAc, hasAc, canDc, isDac, canRC, funcs = SpecialPredicates.separate(rules, ..)
        return separate(rules, *map(lambda pred: lambda rule: rule.concl.name == pred, predicates))

class canAc(HypothesesTranslator):
    def __init__(self, rule):
        super().__init__(rule)
        self.subject = repr(self.rule.concl.args[0])
    
    @typecheck
    def translate(self, role_params: list_of(Variable)):
        self.role_params = [repr(p) for p in role_params]
        
        # build self.external_vars (for HypothesesTranslator)
        self.external_vars = { p : 'self.'+p for p in self.role_params }
        self.external_vars.update( { self.subject : self.subject } )
        
        return lambda number: """
def canActivate{num}(self, {subject}): # {rule_name}
{hypotheses_translation}""".format(
             rule_name = self.rule.name
            ,num = "" if number==0 else "_" + str(number)
            ,subject = self.subject
            ,hypotheses_translation = tab(self.translate_hypotheses())
        )


class canDc(HypothesesTranslator):
    def __init__(self, rule):
        super().__init__(rule)
        
    @typecheck
    def translate(self, role_params: list_of(Variable)):
        self.role_params = [repr(p) for p in role_params]
        
        # build self.external_vars (for HypothesesTranslator)
        self.external_vars = { p : 'self.'+p for p in self.role_params }
        
        subj1 = str(self.rule.concl.args[0])
        subj2 = str(self.rule.concl.args[1])
        
        if subj1 == subj2:
            self.external_vars.update( { subj1 : subj1 } )
            subj2 = subj2 + "_"
            pre_conditional = "%s == %s" % (subj1, subj2)
        else:
            self.external_vars.update( { subj1 : subj1 , subj2 : subj2  } )
            pre_conditional = ""
        
        return lambda number: """
def canDeactivate{num}(self, {subj1}, {subj2}): # {rule_name}
{hypotheses_translation}""".format(
                     rule_name = self.rule.name
                     ,num = "" if number==0 else "_" + str(number)
                    ,subj1 = subj1
                    ,subj2 = subj2
                    ,hypotheses_translation = tab(self.translate_hypotheses(pre_conditional=pre_conditional))
                    )


class FuncRule(HypothesesTranslator):
    def __init__(self, rule):
        super().__init__(rule)
        
        self.kind = None # unknown kind        
        # Determine what kind of function it is...
        if type(self.rule.concl.args[0]) == Aggregate:
            if self.rule.concl.args[0].name == 'count':
                if self.rule.hypos[0].name == SpecialPredicates.hasAc:
                    # it is of the form: count-role-name(count<x>, ...) <- hasActivated(x, ...), ...
                    self.kind = 'count'
                    CountFunctions.funcs.append(self.rule.concl.name)
            elif self.rule.concl.args[0].name == 'group':
                self.kind = 'group'
                self.group_key = self.rule.concl.args[0].args[0]
        elif self.rule.concl.name == "no-main-role-active":
            self.kind = 'nmra'
    
    def nmra_trans_hypo(self):
        conditionals = []
        ctrs, funcs = separate(self.rule.hypos, lambda h: type(h) == Constraint)
        if len(ctrs) == 1:        
            varn, foo  = self.build_constraint_bindings(ctrs[0])
            if varn == {'n'}:
                for f in funcs:
                    if f.name in CountFunctions.funcs:
                        f_name = h2u(f.name)
                        f_args = [str(a) for a in f.args[1:]]
                        n = f_name + "(" + ", ".join(f_args) + ")"
                        conditionals.append( foo( { 'n' : n } ) )
                return "return  " + " and \\\n        ".join(conditionals)
        
        return untranslated(self.rule)
    
    def translate(self):
        if self.kind == 'count' or self.kind == 'group' or self.kind == 'nmra':
            
            if self.kind == 'nmra':
                args = [h2u(repr(a)) for a in self.rule.concl.args]
            else:
                args = [h2u(repr(a)) for a in self.rule.concl.args[1:]]
            
            self.external_vars = { a:a for a in args }
            
            if self.kind == 'nmra':
                hypotheses_translation = tab(self.nmra_trans_hypo())
            elif self.kind == 'count':
                hypotheses_translation = tab(self.translate_hypotheses( ["len(" , ")"] ))
            elif self.kind == 'group':
                hypotheses_translation = tab(self.translate_hypotheses( group_key = self.group_key ))
            
            return"""
def {func_name}({func_args}): # {rule_name}
{hypotheses_translation}""".format(
                 rule_name = self.rule.name
                ,func_name = h2u(self.rule.concl.name)
                ,func_args = ", ".join(args)
                ,hypotheses_translation = hypotheses_translation
                )
        
        return untranslated(self.rule)

class PermitsRule(HypothesesTranslator):
    def __init__(self, rule):
        super().__init__(rule)
        self.subject = str(self.rule.concl.args[0])
    
    def translate(self, action_params):
        # build self.external_vars (for HypothesesTranslator)
        self.external_vars = { p : 'self.'+p for p in action_params }
        self.external_vars.update( { self.subject : self.subject } )
        
        return lambda number: """
def permits{num}(self, {subject}): # {rule_name}
{hypotheses_translation}""".format(
             rule_name = self.rule.name
            ,num = "" if number==0 else "_" + str(number)
            ,subject = self.subject
            ,hypotheses_translation = tab(self.translate_hypotheses())
        )

class canReqCred_canActivate(HypothesesTranslator):
    def __init__(self, rule, the_role_name, n):
        super().__init__(rule)
        self.subject = str(self.rule.concl.args[0])
        self.the_role_name = the_role_name
        self.n = n

    def translate(self):
        self.external_vars = { self.subject : self.subject }

        return """
def canReqCred_canActivate_{the_role_name}_{n}({subject}): # {rule_name}
{hypotheses_translation}""".format(
             the_role_name = self.the_role_name
            ,n = self.n
            ,rule_name = self.rule.name
            ,subject = self.subject
            ,hypotheses_translation = tab(self.translate_hypotheses())
        )

class canReqCred_hasActivated(HypothesesTranslator):
    def __init__(self, rule, the_role_name, n):
        super().__init__(rule)
        self.subject = str(self.rule.concl.args[0])
        self.params = [str(p) for p in self.rule.concl.args[1].args[1].args]
        self.the_role_name = the_role_name
        self.n = n

    def translate(self):
        self.external_vars = { self.subject : self.subject }
        self.external_vars.update( { p : p for p in self.params } )

        return """
def canReqCred_hasActivated_{the_role_name}_{n}({subject}{params}): # {rule_name}
{hypotheses_translation}""".format(
             the_role_name = h2u(self.the_role_name)
            ,n = self.n
            ,rule_name = self.rule.name
            ,subject = self.subject
            ,params = (', ' if len(self.params) else '') + ', '.join(self.params)
            ,hypotheses_translation = tab(self.translate_hypotheses())
        )
