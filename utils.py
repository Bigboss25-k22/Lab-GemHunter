"""
GemHunter - Utility Functions
This module contains functions for:
1. File reading/writing
2. Grid processing
3. Position conversion
4. Validation checks
"""

from typing import List, Tuple
from copy import deepcopy
import os
import glob
import re

def read_input(file_path: str) -> List[List[str]]:
    """Read input file and return grid.
    
    Input file must have format:
    - Each line is a row of the grid
    - Characters separated by comma and space
    - Only contains '_' or numbers from 0-8
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            array_2d = [line.strip().split(", ") for line in file]
        return array_2d
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        import sys
        sys.exit(1)

def get_neigh(pos: Tuple[int, int], grid: List[List[str]]) -> List[Tuple[int, int]]:
    """Get list of surrounding cells for a position.
    
    Surrounding includes 8 cells:
    - 4 adjacent cells (top, bottom, left, right)
    - 4 diagonal cells (top-left, top-right, bottom-left, bottom-right)
    Only returns empty cells ('_')
    """
    adjacent = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    neigh = []
    for di, dj in adjacent:
        x, y = pos
        x += di
        y += dj
        if 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] == '_':
            neigh.append((x, y))
    return neigh

def convert_pos_to_int(pos: Tuple[int, int], grid: List[List[str]]) -> int:
    """Convert position (i,j) to integer.
    
    Formula: i * n + j + 1
    Where n is grid size.
    """
    x, y = pos
    return x * len(grid[0]) + y + 1

def convert_int_to_pos(num: int, grid: List[List[str]]) -> Tuple[int, int]: 
    """Convert integer to position (i,j).
    
    Formula:
    i = (num - 1) // n
    j = (num - 1) % n
    Where n is grid size.
    """
    num = abs(num) - 1
    x = num // len(grid[0])
    y = num % len(grid[0])
    return (x, y)

def get_grid_result(grid: List[List[str]], result: List[int]) -> List[List[str]]:
    """Convert solver result to grid.
    
    If a cell has a trap, mark as 'T'.
    If no trap, mark as 'G'.
    Keep numbered cells unchanged.
    """
    new_grid = deepcopy(grid)
    for num in result:
        temp = 'T' if num > 0 else 'G'
        x, y = convert_int_to_pos(num, grid)
        if new_grid[x][y] == '_':
            new_grid[x][y] = temp
    return new_grid

def is_valid_filled_grid(grid: List[List[str]]) -> bool:
    """Check if filled grid is valid.
    
    A valid grid must:
    1. Numbered cells must have correct number of surrounding traps
    2. Empty cells must be filled with 'T' or 'G'
    3. No invalid characters
    """
    n_rows, n_cols = len(grid), len(grid[0])

    def count_traps_around(i: int, j: int) -> int:
        """Count number of traps around a cell."""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), 
                     (1, 1), (-1, -1), (1, -1), (-1, 1)]
        trap_count = 0
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < n_rows and 0 <= nj < n_cols:
                if grid[ni][nj] == 'T':
                    trap_count += 1
        return trap_count

    for i in range(n_rows):
        for j in range(n_cols):
            if grid[i][j].isdigit():
                expected_traps = int(grid[i][j])
                actual_traps = count_traps_around(i, j)
                
                if actual_traps != expected_traps:
                    print(f"errors at cell ({i}, {j}): "
                          f"Need {expected_traps} trap but found {actual_traps}")
                    return False
            elif grid[i][j] not in ['_', 'T', 'G']:
                print(f"unvalid value in cell ({i}, {j}): {grid[i][j]}")
                return False

    print("All cells are filled correctly!")
    return True

def get_test_files(test_dir: str) -> List[str]:
    """Get list of test case files.
    
    Only get files with name format 'input_X.txt'
    where X is test case number.
    """
    test_files = glob.glob(os.path.join(test_dir, "input_*.txt"))
    return sorted(test_files)

def get_test_case_number(filename: str) -> str:
    """Get test case number from filename.
    
    Example:
    'input_1.txt' -> '1'
    'input_42.txt' -> '42'
    """
    match = re.search(r'input_(\d+)\.txt$', filename)
    if match:
        return match.group(1)
    return "0"  # Default number if pattern not found 