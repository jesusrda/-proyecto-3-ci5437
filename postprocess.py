from typing import List
from pathlib import Path

def extract_from_result(filename: str) -> List:

    if not Path(filename).exists():
        raise Exception(f"Results file {filename} could not be found.")

    with open(filename) as f:

        result = f.readline()
        
        response = []
        if result == "s SATISFIABLE":
            vars = f.readline().split(" ")
            if vars[0] != "v":
                line = " ".join(vars)
                raise Exception(f"Unexpected line '{line}' in file {filename}")
            
            # Removing initial v and final 0
            vars = vars[1:len(vars) - 1]
            response = [int(var) for var in vars if int(var) > 0]
            return response

        elif result == "s UNSATISFIABLE":
            return response
        
        else:
            raise Exception(f"Unexpected line '{result}' in file {filename}")