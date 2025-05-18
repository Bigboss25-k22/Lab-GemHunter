import time
import os
from typing import Dict, Any
from solvers import solve_by_sat, solve_by_dpll, solve_by_brute_force_with_timeout, TimeoutError
from utils import read_input, get_grid_result, is_valid_filled_grid, get_test_files, get_test_case_number
from grid_processor import generate_cnf, validate_grid

def process_test_case(test_file: str, output_dir: str) -> Dict[str, Any]:
    """Process a single test case with all solvers."""
    print(f"\nProcessing {test_file}...")
    
    try:
        # Read the grid
        grid = read_input(test_file)
        
        # Validate grid
        validate_grid(grid)
        
        # Generate CNF once for all solvers
        cnf_start = time.time()
        cnf = generate_cnf(grid)
        cnf_time = time.time() - cnf_start
        
        # Define solvers to use
        solvers = {
            'SAT': solve_by_sat,
            'DPLL': solve_by_dpll,
            'Brute Force': solve_by_brute_force_with_timeout
        }
        
        # Initialize results dictionary
        results = {}
        
        # Process with each solver
        for solver_name, solver_func in solvers.items():
            print(f"\nRunning {solver_name} solver...")
            
            try:
                # Solve using current solver and measure time
                solve_start = time.time()
                
                # Special handling for Brute Force
                if solver_name == 'Brute Force':
                    try:
                        result = solver_func(cnf, timeout_seconds=30)
                        if result is None:
                            print(f"Brute Force solver timed out after 30 seconds for {test_file}")
                            results[solver_name] = {
                                'time': None,
                                'result': None,
                                'valid': False,
                                'timeout': True
                            }
                            continue
                    except TimeoutError:
                        print(f"Brute Force solver timed out after 30 seconds for {test_file}")
                        results[solver_name] = {
                            'time': None,
                            'result': None,
                            'valid': False,
                            'timeout': True
                        }
                        continue
                else:
                    result = solver_func(cnf)
                    
                solve_time = time.time() - solve_start
                
                if result is None:
                    print(f"No solution found with {solver_name}")
                    results[solver_name] = {
                        'time': None,
                        'result': None,
                        'valid': False,
                        'timeout': False
                    }
                    continue
                    
                # Get the result grid
                result_grid = get_grid_result(grid, result)
                
                # Validate the solution
                is_valid = is_valid_filled_grid(result_grid)
                
                # Store results
                results[solver_name] = {
                    'time': solve_time,
                    'result': result,
                    'result_grid': result_grid,
                    'valid': is_valid,
                    'timeout': False
                }
                
                print(f"Solution found with {solver_name}")
                print(f"Time taken: {solve_time:.4f} seconds")
                print(f"Solution valid: {'Yes' if is_valid else 'No'}")
                
            except Exception as e:
                print(f"Error occurred with {solver_name} solver: {str(e)}")
                results[solver_name] = {
                    'time': None,
                    'result': None,
                    'valid': False,
                    'timeout': False,
                    'error': str(e)
                }
        
        return {
            'grid': grid,
            'cnf_time': cnf_time,
            'results': results
        }
        
    except Exception as e:
        print(f"Error processing test case {test_file}: {str(e)}")
        return {
            'grid': None,
            'cnf_time': None,
            'results': {},
            'error': str(e)
        }

def write_output_file(test_file: str, output_dir: str, data: Dict[str, Any]):
    """Write results to output file."""
    # Get test case number from input filename
    test_case_num = get_test_case_number(test_file)
    output_file = os.path.join(output_dir, f"output_{test_case_num}.txt")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Input file: {test_file}\n")
        f.write("=" * 50 + "\n\n")
        
        if data['grid'] is None:
            f.write(f"Error processing test case: {data.get('error', 'Unknown error')}\n")
            return
            
        f.write("Original grid:\n")
        for row in data['grid']:
            f.write(", ".join(row) + "\n")
        f.write("\n")
        
        for solver_name, result in data['results'].items():
            f.write(f"\n{solver_name} Solver Results:\n")
            f.write("-" * 30 + "\n")
            
            if result['timeout']:
                f.write("Status: Timeout after 30 seconds\n")
            elif result['time'] is None:
                if 'error' in result:
                    f.write(f"Status: Error - {result['error']}\n")
                else:
                    f.write("Status: No solution found\n")
            else:
                f.write(f"Solving time: {result['time']:.4f} seconds\n")
                f.write(f"Solution valid: {'Yes' if result['valid'] else 'No'}\n")
                if result['valid']:
                    f.write("\nSolution grid:\n")
                    for row in result['result_grid']:
                        f.write(", ".join(row) + "\n")
            f.write("\n")

def write_comparison_file(output_dir: str, all_results: Dict[str, Dict[str, Any]]):
    """Write comparison summary to file."""
    comparison_file = os.path.join(output_dir, "algorithm_comparison.txt")
    
    with open(comparison_file, "w", encoding="utf-8") as f:
        f.write("Algorithm Comparison Summary\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"{'Test Case':<20} {'SAT Time':<15} {'DPLL Time':<15} {'Brute Force Time':<20} {'SAT Valid':<10} {'DPLL Valid':<10} {'Brute Force Valid':<15}\n")
        f.write("-" * 100 + "\n")
        
        for test_file, data in all_results.items():
            if data['grid'] is None:
                continue
                
            results = data['results']
            
            sat_time = f"{results['SAT']['time']:.4f}s" if results['SAT']['time'] is not None else "N/A"
            dpll_time = f"{results['DPLL']['time']:.4f}s" if results['DPLL']['time'] is not None else "N/A"
            brute_time = f"{results['Brute Force']['time']:.4f}s" if results['Brute Force']['time'] is not None else "Timeout"
            
            sat_valid = "Yes" if results['SAT']['valid'] else "No"
            dpll_valid = "Yes" if results['DPLL']['valid'] else "No"
            brute_valid = "Yes" if results['Brute Force']['valid'] else "No"
            
            test_case_num = get_test_case_number(test_file)
            f.write(f"Test Case {test_case_num:<15} {sat_time:<15} {dpll_time:<15} {brute_time:<20} {sat_valid:<10} {dpll_valid:<10} {brute_valid:<15}\n")

def main():
    try:
        # Create input and output directories if they don't exist
        base_dir = "TestCase"
        input_dir = os.path.join(base_dir, "input")
        output_dir = os.path.join(base_dir, "output")
        
        for dir_path in [base_dir, input_dir, output_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        
        # Get all test case files from input directory
        test_files = get_test_files(input_dir)
        
        if not test_files:
            print("No test files found in TestCase/input directory")
            return
            
        print("Running all solvers on test cases...")
        print("=" * 50)
        
        # Process all test cases and store results
        all_results = {}
        for test_file in test_files:
            data = process_test_case(test_file, output_dir)
            all_results[test_file] = data
            write_output_file(test_file, output_dir, data)
        
        # Write comparison summary
        write_comparison_file(base_dir, all_results)
        
        print(f"\nResults have been saved to the output directory.")
        print(f"Comparison summary has been saved to {os.path.join(output_dir, 'algorithm_comparison.txt')}")
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main()