from typing import List
from pathlib import Path

def extract_from_result(filename: str) -> List:
    """
    Function to extract result after running the sat solver
    :param filename: Path of file containing the SAT solver result
    :returns: List of variables with true value in the solution. Empty 
              in case there is no possible solution
    """
    if not Path(filename).exists():
        raise Exception(f"Results file {filename} could not be found.")

    with open(filename) as f:

        result = f.readline().strip()

        response = []
        if result == "s SATISFIABLE":
            vars = f.readline().split(" ")
            if vars[0] != "v":
                line = " ".join(vars)
                raise Exception(f"Unexpected line '{line}' in file {filename}")
            
            # Removing initial v and final 0
            vars = vars[1:len(vars) - 1]
            response = [int(var) for var in filter(lambda x : int(x) > 0, vars)]
            return response

        elif result == "s UNSATISFIABLE":
            return response
        
        else:
            raise Exception(f"Unexpected line '{result}' in file {filename}")