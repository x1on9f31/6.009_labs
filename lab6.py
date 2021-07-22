#!/usr/bin/env python3
"""6.009 Lab 6 -- Boolean satisfiability solving"""

import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS    

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    #print(formula)
    #generate set of all conditions
    conditions = set()
    for clause in formula:
        for literal in clause:
            conditions.add(literal[0])
    
    N = len(conditions)

    order = list(conditions)
    order.sort()
    # print(order)
    assignment = {variable:None for variable in conditions}

    #iter1 = 0
    for clause in formula:
        if len(clause) == 1:
            #iter1 += 1
            var,value = clause[0]
            assignment[var] = value
    
    #print(iter1)

    def evaluateCNF(current_formula):
        # takes in a CNF, returns simplified CNF after substituting in current_settings
        rV = []
        for clause in current_formula:
            current_clause = []
            isTrue = False
            for literal in clause:
                if assignment[literal[0]] != None: # check if there is an assigned value for this literal
                    if assignment[literal[0]] == literal[1]: # if the assignment in our dictionary matches the literal, then the entire clause is True
                        isTrue = True
                else: # if not assigned value, then it is yet to be processed
                    current_clause.append(literal)
            if not isTrue: # if the assignment is not True, then the clause has yet to be evaluated
                rV.append(current_clause)
            if not isTrue and not current_clause:
                return False
        if rV:
            return rV
        else:
            return True
    
    def isValid(index):
        # print("====")
        # print(assignment)
        # print(index)
        if index == N:
            return True
        key = order[index]
        # print(var)
        #try current condition to be True
        assignment[key] = True
        formula1 = evaluateCNF(formula)
        # print(True,formula1)
        # if new_formula == True, then we have solved it
        # if new_formula == False, then this means that the current assignments cannot be part of a solution, so we should backtrack
        # if new_formula is a CNF, then we can keep going
        if formula1 == True: # our current assignment solves the problem, so we are done
            return True
        if formula1 != False: # our current assignment does not fail, so we check the next index
            #num = 0
            for clause in formula1: #check for length 1 clauses
                if len(clause) == 1:
                    #num +=1
                    var,value = clause[0]
                    assignment[var] = value
            #print(num)
            if isValid(index+1):
                return True
            for clause in formula1:#if we did not return True then we undo all the assignments from the length 1 clauses
                if len(clause) == 1:
                    var,value = clause[0]
                    assignment[var] = None
        #try current condition to be False
        assignment[key] = False
        formula2 = evaluateCNF(formula)
        # print(False,formula2)
        if formula2 == True: # our current assignment solves the problem, so we are done
            return True
        if formula2 != False: # our current assignment does not fail, so we check the next index
            #num = 0
            for clause in formula2:
                if len(clause)==1: #check for length 1 clauses
                    #num +=1
                    var,value = clause[0]
                    assignment[var] = value
            #print(num)
            if isValid(index+1):
                return True
            for clause in formula2: #if we did not return True then we undo all the assignments from the length 1 clauses
                if len(clause) ==1:
                    var,value = clause[0]
                    assignment[var]= None
        #if nothing has been returned so far, then the previous variables must be changed
        assignment[key] = None #undo what we have done here
        return False
        
        
    
    if isValid(0):
        #print(assignment)
        return assignment
    else:
        return None

        
        

        

def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """

    #print(student_preferences)
    #print(room_capacities)

    names = set()
    for elem in student_preferences.keys():
        names.add(elem)
    rooms = set()
    for elem in room_capacities.keys():
        rooms.add(elem)
    #print('names',names)
    #print('rooms',rooms)

    memo_table = {}

    def preference_to_CNF():
        rV = []
        for k,v in student_preferences.items():
            to_add = []
            for room in v:
                to_add.append((k+"_"+room,True))
            rV.append(to_add)
        return rV

    def one_room_CNF():
        all_combs = gen_comb(rooms, 2)
        rV = []
        for name in names:
            for comb in all_combs:
                to_add = []
                for room in comb:
                    to_add.append((name + "_" + room, False))
                rV.append(to_add)
        return rV
    

    def gen_comb(values,length):
        if (frozenset(values),length) in memo_table:
            return memo_table[(frozenset(values),length)]
        if length > len(values):
            memo_table[(frozenset(values),length)] = set()
            return set()
        if length == len(values):
            rV = set()
            rV.add(frozenset(values))
            memo_table[(frozenset(values),length)] = rV
            return rV
        rV = set()
        
        if length == 1:
            for elem in values:
                rV.add(frozenset([elem]))
            memo_table[(frozenset(values),length)] = rV
            return rV
        
        for elem in values:
            next_input = values.copy()
            next_input.remove(elem)
            sub_comb = gen_comb(next_input,length-1)
            for comb in sub_comb:
                to_add = set(comb)
                to_add.add(elem)
                rV.add(frozenset(to_add))
        memo_table[(frozenset(values),length)] = rV
        return rV

    def capacity_to_CNF():
        rV = []
        for k,v in room_capacities.items():
            #print(k,v)
            all_combs = gen_comb(names,v+1)
            #print(all_combs)
            for comb in all_combs:
                to_add = []
                #print(comb)
                for name in comb:
                    var = name + '_' + k
                    #print(var)
                    to_add.append((var,False))
                    #print(to_add)
                if to_add:
                    rV.append(to_add)
        return rV

    
    #print(preference_to_CNF())
    #print(one_room_CNF())
    #print(capacity_to_CNF())
    

    return preference_to_CNF() + one_room_CNF() + capacity_to_CNF()
        
    


if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)

