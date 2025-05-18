# GemHunter

GemHunter is a project that implements and compares different algorithms for solving SAT (Boolean Satisfiability) problems. The project includes three different solving approaches: SAT solver (using pysat library), DPLL algorithm, and Brute Force method.

## Features

- Multiple solving algorithms:
  - SAT solver using pysat library
  - DPLL (Davis-Putnam-Logemann-Loveland) algorithm
  - Brute Force method with timeout
- Comprehensive test case processing
- Performance comparison between algorithms
- Detailed output generation
- Grid validation and CNF generation

## Project Structure

```
GemHunter/
├── main.py              # Main program entry point
├── solvers.py           # Implementation of solving algorithms
├── grid_processor.py    # Grid processing and CNF generation
├── utils.py            # Utility functions
└── TestCase/
    ├── input/          # Input test cases
    └── output/         # Generated output files
```

## Requirements

- Python 3.6 or higher
- Required packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd GemHunter
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your test cases in the `TestCase/input` directory
2. Run the main program:
```bash
python main.py
```

The program will:
- Process all test cases in the input directory
- Run each test case through all three solvers
- Generate detailed output files in `TestCase/output`
- Create a comparison summary in `TestCase/output/algorithm_comparison.txt`

## Output Format

For each test case, the program generates:
- Individual output files with detailed results for each solver
- A comparison summary showing:
  - Solving time for each algorithm
  - Solution validity
  - Timeout information (for Brute Force)

## Algorithms

1. **SAT Solver**
   - Uses pysat library with glucose3 solver
   - Efficient for complex SAT problems

2. **DPLL Algorithm**
   - Implements backtracking with:
     - Unit propagation
     - Pure literal elimination
     - Variable branching
   - Uses Most Occurring Variable (MOV) heuristic

3. **Brute Force**
   - Tries all possible combinations
   - Includes 30-second timeout
   - Useful for small problems

## License

[Your License Here] 