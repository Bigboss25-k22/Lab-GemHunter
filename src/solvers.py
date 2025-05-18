"""
GemHunter - Solving Algorithms
This module contains 3 solving algorithms:
1. SAT solver (using pysat library)
2. DPLL (backtracking algorithm)
3. Brute Force (try all possible cases)
"""

from typing import List, Tuple
from pysat.solvers import Solver
import threading
import time
from collections import Counter

class TimeoutError(Exception):
    """Error when algorithm runs longer than allowed time."""
    pass

def solve_by_sat(cnf: List[List[int]]) -> List[int]:
    """Solve CNF using SAT solver.
    
    Uses pysat library to find solution for CNF.
    Returns list of literals if solution found,
    or None if no solution exists.
    """
    solver = Solver(name='glucose3')
    for clause in cnf:
        solver.add_clause(clause)
    return solver.get_model() if solver.solve() else None

def solve_by_dpll(cnf: List[List[int]]) -> List[int]:
    """Solve CNF using DPLL algorithm.
    
    DPLL is a backtracking algorithm for solving SAT problems, using:
    1. Unit propagation
    2. Pure literal elimination
    3. Branching on variables
    """
    all_vars = set(abs(var) for clause in cnf for var in clause)
    max_var = max(all_vars) if all_vars else 0
    assignment = dpll(cnf, [])
    
    if assignment is None:
        return []
    
    assigned_vars = set(abs(var) for var in assignment)
    for var in range(1, max_var + 1):
        if var not in assigned_vars:
            assignment.append(-var)
    
    return assignment

def solve_by_brute_force(cnf: List[List[int]]) -> List[int]:
    """Solve CNF using brute force method.
    
    Try all possible combinations of literals until
    finding a solution that satisfies all clauses.
    """
    all_vars = set()
    for clause in cnf:
        for var in clause:
            all_vars.add(abs(var))
    
    sorted_vars = sorted(all_vars)
    num_vars = len(sorted_vars)
    
    total_assignments = 1 << num_vars
    for assignment in range(total_assignments):
        model = []
        for i in range(num_vars):
            if (assignment >> i) & 1: 
                model.append(sorted_vars[i])  
            else:  
                model.append(-sorted_vars[i])  
        
        if checking_cnf(cnf, model):
            return model  
    
    return None

def solve_by_brute_force_with_timeout(cnf: List[List[int]], timeout_seconds: int = 30) -> List[int]:
    """Solve CNF using brute force with timeout.
    
    Run brute force algorithm in separate thread with timeout.
    If not completed within allowed time, raise TimeoutError.
    """
    result = [None]
    error = [None]
    stop_event = threading.Event()
    
    def run_solver():
        """Run brute force algorithm and store result."""
        try:
            if not stop_event.is_set():
                result[0] = solve_by_brute_force(cnf)
        except Exception as e:
            error[0] = e
        finally:
            stop_event.set()
    
    solver_thread = threading.Thread(target=run_solver)
    solver_thread.daemon = True
    solver_thread.start()
    
    try:
        solver_thread.join(timeout_seconds)
        if solver_thread.is_alive():
            stop_event.set()
            solver_thread.join(1)  # Give thread time to cleanup
            return None
    except KeyboardInterrupt:
        stop_event.set()
        solver_thread.join(1)  # Give thread time to cleanup
        raise
    
    if error[0] is not None:
        raise error[0]
    
    return result[0]

def unit_propagation(cnf: List[List[int]], model: List[int]) -> Tuple[List[List[int]], List[int]]:
    """Perform unit propagation on CNF.
    
    Unit propagation process:
    1. Find unit clauses (clauses with only 1 literal)
    2. Add literal to model
    3. Remove clauses containing literal
    4. Remove negation of literal from remaining clauses
    """
    changed = True
    while changed:
        changed = False
        unit_clauses = [clause[0] for clause in cnf if len(clause) == 1]

        for unit in unit_clauses:
            if unit in model or -unit in model:
                continue  
            
            model.append(unit)  
            cnf = [clause for clause in cnf if unit not in clause]

            for clause in cnf:
                if -unit in clause:
                    clause.remove(-unit)

            changed = True  

    return cnf, model

def pure_literal_elimination(cnf: List[List[int]], model: List[int]) -> Tuple[List[List[int]], List[int]]:
    """Perform pure literal elimination on CNF.
    
    Pure literal elimination process:
    1. Find pure literals (literals appearing with only one sign)
    2. Add pure literal to model
    3. Remove clauses containing pure literal
    """
    all_vars = set(abs(var) for clause in cnf for var in clause)
    pure_literals = set()
    all_literals = {lit for clause in cnf for lit in clause}

    for var in all_vars:
        if var in all_literals and -var not in all_literals:
            pure_literals.add(var)
        elif -var in all_literals and var not in all_literals:
            pure_literals.add(-var)

    for pure in pure_literals:
        model.append(pure) 
        cnf = [clause for clause in cnf if pure not in clause]

    return cnf, model

def choose_variable(cnf: List[List[int]]) -> int:
    """Choose variable for branching in DPLL algorithm.
    
    Uses Most Occurring Variable (MOV) heuristic:
    - Count occurrences of each literal
    - Choose most frequently occurring literal
    """
    flat = [abs(var) for clause in cnf for var in clause]
    counter = Counter(flat)
    return counter.most_common(1)[0][0]

def dpll(cnf: List[List[int]], model: List[int]) -> List[int]:
    """DPLL algorithm.
    
    DPLL is a backtracking algorithm for solving SAT problems, using:
    1. Unit propagation
    2. Pure literal elimination
    3. Branching on variables
    """
    cnf, model = unit_propagation(cnf, model) 
    cnf, model = pure_literal_elimination(cnf, model) 

    if not cnf:
        return model

    if any(len(clause) == 0 for clause in cnf):
        return []

    var = choose_variable(cnf)
    
    # Try positive assignment
    new_model = model + [var]
    new_cnf = [clause for clause in cnf if var not in clause]
    new_cnf = [[x for x in clause if x != -var] for clause in new_cnf]
    result = dpll(new_cnf, new_model)
    if result:
        return result

    # Try negative assignment
    new_model = model + [-var]
    new_cnf = [clause for clause in cnf if -var not in clause]
    new_cnf = [[x for x in clause if x != var] for clause in new_cnf]
    return dpll(new_cnf, new_model)

def checking_clause(clause: List[int], model: List[int]) -> bool:
    """Check if a clause is satisfied by model.
    
    A clause is satisfied if at least one literal in clause
    is true in model. A literal is true if it appears in model
    with same sign.
    """
    for var in clause:
        if var > 0 and var in model:
            return True
        if var < 0 and -var not in model:
            return True
    return False

def checking_cnf(cnf: List[List[int]], model: List[int]) -> bool:
    """Check if all clauses in CNF are satisfied.
    
    CNF is satisfied if all clauses in it are satisfied.
    """
    return all(checking_clause(clause, model) for clause in cnf) 