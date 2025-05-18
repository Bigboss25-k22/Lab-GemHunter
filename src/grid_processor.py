"""
GemHunter - Grid Processing and CNF Generation
This module contains functions for:
1. Validating grid
2. Generating trap combinations
3. Converting grid to CNF
"""

from typing import List, Tuple
from itertools import combinations
from utils import get_neigh, convert_pos_to_int

def validate_grid(grid: List[List[str]]) -> bool:
    """Validate the grid.
    
    A valid grid must:
    1. Not be empty
    2. Have valid dimensions (n x n)
    3. Only contain '_' or numbers from 0-8
    """
    if not grid or not grid[0]:
        raise ValueError("Grid cannot be empty")
        
    rows = len(grid)
    cols = len(grid[0])
    
    if not all(len(row) == cols for row in grid):
        raise ValueError("All rows must have the same length")
        
    valid_chars = {'_', '0', '1', '2', '3', '4', '5', '6', '7', '8'}
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] not in valid_chars:
                raise ValueError(f"Invalid character '{grid[i][j]}' at position ({i}, {j})")
                
    return True

def generate_trap_combinations(array: List[int], n: int) -> List[List[int]]:
    """Generate trap combinations from array of positions.
    
    Args:
        array: List of positions where traps can be placed
        n: Number of traps to place
        
    Returns:
        List of CNF clauses representing trap combinations
    """
    clauses = []
    leng = len(array) - n + 1
    
    # Create clause for at least n traps
    for combo in combinations(array, leng):
        clauses.append(list(combo))
        
    # Create clause for at most n traps
    k = n + 1
    if k <= len(array):
        for combo in combinations(array, k):
            clauses.append([-var for var in combo])
            
    return clauses

def generate_cnf(grid: List[List[str]]) -> List[List[int]]:
    """Convert grid to CNF.
    
    Conversion process:
    1. Validate grid
    2. For each numbered cell:
       - Find surrounding cells where traps can be placed
       - Generate trap combinations based on required number
       - Create clauses for each combination
    """
    # Validate grid
    validate_grid(grid)
    
    cnf = []
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] != '_':
                pos = (i, j)
                neigh = get_neigh(pos, grid)
                neigh_vars = [convert_pos_to_int(p, grid) for p in neigh]
                
                # Check if puzzle is solvable
                if len(neigh_vars) - int(grid[i][j]) < 0:
                    cnf.append([])  # Not solvable
                else:
                    trap_clauses = generate_trap_combinations(neigh_vars, int(grid[i][j]))
                    cnf.extend(trap_clauses)
                    
    return cnf 