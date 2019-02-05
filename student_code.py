import read, copy
from util import *
from logical_classes import *

verbose = 0

class KnowledgeBase(object):
    def __init__(self, facts=[], rules=[]):
        self.facts = facts
        self.rules = rules
        self.ie = InferenceEngine()

    def __repr__(self):
        return 'KnowledgeBase({!r}, {!r})'.format(self.facts, self.rules)

    def __str__(self):
        string = "Knowledge Base: \n"
        string += "\n".join((str(fact) for fact in self.facts)) + "\n"
        string += "\n".join((str(rule) for rule in self.rules))
        return string

    def _get_fact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument

        Args:
            fact (Fact): Fact we're searching for

        Returns:
            Fact: matching fact
        """
        for kbfact in self.facts:
            if fact == kbfact:
                return kbfact

    def _get_rule(self, rule):
        """INTERNAL USE ONLY
        Get the rule in the KB that is the same as the rule argument

        Args:
            rule (Rule): Rule we're searching for

        Returns:
            Rule: matching rule
        """
        for kbrule in self.rules:
            if rule == kbrule:
                return kbrule

    def kb_add(self, fact_rule):
        """Add a fact or rule to the KB
        Args:
            fact_rule (Fact|Rule) - the fact or rule to be added
        Returns:
            None
        """
        printv("Adding {!r}", 1, verbose, [fact_rule])
        if isinstance(fact_rule, Fact):
            if fact_rule not in self.facts:
                self.facts.append(fact_rule)
                for rule in self.rules:
                    self.ie.fc_infer(fact_rule, rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.facts.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.facts[ind].supported_by.append(f)
                else:
                    ind = self.facts.index(fact_rule)
                    self.facts[ind].asserted = True
        elif isinstance(fact_rule, Rule):
            if fact_rule not in self.rules:
                self.rules.append(fact_rule)
                for fact in self.facts:
                    self.ie.fc_infer(fact, fact_rule, self)
            else:
                if fact_rule.supported_by:
                    ind = self.rules.index(fact_rule)
                    for f in fact_rule.supported_by:
                        self.rules[ind].supported_by.append(f)
                else:
                    ind = self.rules.index(fact_rule)
                    self.rules[ind].asserted = True

    def kb_assert(self, fact_rule):
        """Assert a fact or rule into the KB

        Args:
            fact_rule (Fact or Rule): Fact or Rule we're asserting
        """
        printv("Asserting {!r}", 0, verbose, [fact_rule])
        self.kb_add(fact_rule)

    def kb_ask(self, fact):
        """Ask if a fact is in the KB

        Args:
            fact (Fact) - Statement to be asked (will be converted into a Fact)

        Returns:
            listof Bindings|False - list of Bindings if result found, False otherwise
        """
        print("Asking {!r}".format(fact))
        if factq(fact):
            f = Fact(fact.statement)
            bindings_lst = ListOfBindings()
            # ask matched facts
            for fact in self.facts:
                binding = match(f.statement, fact.statement)
                if binding:
                    bindings_lst.add_bindings(binding, [fact])

            return bindings_lst if bindings_lst.list_of_bindings else []

        else:
            print("Invalid ask:", fact.statement)
            return []

    def kb_retract(self, fact_or_rule):
        """Retract a fact from the KB

        Args:
            fact (Fact) - Fact to be retracted

        Returns:
            None
        """
        printv("Retracting {!r}", 0, verbose, [fact_or_rule])
        ####################################################
        # Student code goes here
        
        if not isinstance(fact_or_rule, Fact) and not isinstance(fact_or_rule, Rule):
            return
        
        if isinstance(fact_or_rule, Fact):
            fact = self._get_fact(fact_or_rule)
            if fact.supported_by:
                print("Fact is supported.")
                return
            else:
                for supported_fact in fact.supports_facts:
                    for pair in supported_fact.supported_by:
                        if fact in pair:
                            kb_rule = self._get_rule(pair[1])
                            kb_rule.supports_facts.remove(supported_fact)
                            kb_sf = self._get_fact(supported_fact)
                            kb_sf.supported_by.remove(pair)
                            if not kb_sf.supported_by:
                                self.kb_retract(kb_sf)
                
                for supported_rule in fact.supports_rules:
                    for pair in supported_rule.supported_by:
                        if fact in pair:
                            kb_rule = self._get_rule(pair[1])
                            kb_rule.supports_rules.remove(supported_rule)
                            
                            kb_sr = self._get_rule(supported_rule)
                            kb_sr.supported_by.remove(pair)
                            if not kb_sr.asserted:
                                self.kb_retract(kb_sr)

                self.facts.remove(fact)
        elif isinstance(fact_or_rule, Rule):
            rule = self._get_rule(fact_or_rule)
            if rule.asserted:
                print("Can't retract rule.")
                return
            elif not rule.supported_by:
                for supported_fact in rule.supports_facts:
                    for pair in supported_fact.supported_by:
                        if rule in pair:
                            kb_fact = self._get_fact(pair[0])
                            kb_fact.supports_facts.remove(supported_fact)
                            kb_sf = self._get_fact(supported_fact)
                            kb_sf.supported_by.remove(pair)
                            if not kb_sf.supported_by:
                                self.kb_retract(kb_sf)
                for supported_rule in rule.supports_rules:
                    for pair in supported_rule.supported_by:
                        if rule in pair:
                            kb_fact = self._get_fact(pair[0])
                            kb_fact.supports_facts.remove(supported_rule)
                            kb_sr = self._get_rule(supported_rule)
                            kb_sr.supported_by.remove(pair)
                            if not kb_sr.asserted:
                                self.kb_retract(kb_sr)
                self.rules.remove(rule)                
                
        return
        
#    
#        if isinstance(fact_or_rule, Fact):
#            fact = self._get_fact(fact_or_rule)
#            if not fact.supported_by:
#                for pair in fact.supported_by:
#                    for fr in pair[0]:
#                        fr = self._get_fact(fr)
#                        fr.supports_facts.remove(fact)
#                for f in fact.supports_facts:
#                    f = self._get_fact(f)
#                    f.supported_by = [e for e in f.supported_by if fact not in e]
#                    self.kb_retract(f)
#                for r in fact.supports_rules:
#                    r = self._get_rule(r)
#                    r.supported_by = [e for e in r.supported_by if fact not in e]
#                    self.kb_retract(r)
#                self.facts.remove(fact)
#
#        elif isinstance(fact_or_rule, Rule):
#            rule = self._get_rule(fact_or_rule)
#            if not rule.asserted:
#                for pair in rule.supported_by:
#                    for fr in pair[1]:
#                        fr = self._get_rule(fr)
#                        fr.supports_rules.remove(rule)
#                for f in rule.supports_facts:
#                    f = self._get_fact(f)
#                    f.supported_by = [e for e in f.supported_by if rule not in e]
#                    self.kb_retract(f)
#                for r in rule.supports_rules:
#                    r = self._get_rule(r)
#                    r.supported_by = [e for e in r.supported_by if rule not in e]
#                    self.kb_retract(r)
#                self.rules.remove(rule)

class InferenceEngine(object):
    def fc_infer(self, fact, rule, kb):
        """Forward-chaining to infer new facts and rules

        Args:
            fact (Fact) - A fact from the KnowledgeBase
            rule (Rule) - A rule from the KnowledgeBase
            kb (KnowledgeBase) - A KnowledgeBase

        Returns:
            Nothing            
        """
        printv('Attempting to infer from {!r} and {!r} => {!r}', 1, verbose,
            [fact.statement, rule.lhs, rule.rhs])
        ####################################################
        # Student code goes here
        
        if (not isinstance(fact, Fact)) | (not isinstance(rule, Rule)) | (not isinstance(kb, KnowledgeBase)):
            return
        
        bindings = match(rule.lhs[0], fact.statement)
        
        if bindings:
            if len(rule.lhs) == 1:
                new_fact = Fact(instantiate(rule.rhs, bindings), supported_by=[[fact,rule]])
                kb.kb_add(new_fact)
                fact.supports_facts.append(new_fact)
                rule.supports_facts.append(new_fact)
            else:
                new_lhs = []
                for other in rule.lhs[1:]:
                    new_lhs.append(instantiate(other, bindings)) 
                new_rhs = instantiate(rule.rhs, bindings) 
                new_rule = Rule([new_lhs, new_rhs], supported_by=[[fact, rule]])
                kb.kb_add(new_rule, )
                fact.supports_rules.append(new_rule)
                rule.supports_rules.append(new_rule)
        else:
            return
            
            
                
            
        
