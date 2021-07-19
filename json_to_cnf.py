import json

from datetime import date, time
from pathlib import Path
from typing import Dict, List, Tuple

MAXVAR = 0

def read_file(filename: str) -> Dict:
    """
    Function to read json file containing problem parameters
    :param filename: Path to file to read
    :return: Dictionary containing parameters
    """
    if not Path(filename).exists():
        raise Exception(f"File {filename} does not exists.")
    else:
        with open(filename, "r") as f:
            return json.load(f)

def compute_days(start: date, end: date) -> int:
    """
    Function to calculate number of available days to use
    :param start: start date
    :param end: end date
    :return: number of days
    """
    if end < start:
        raise Exception(f"End date is earlier than start date.")

    delta = end - start
    return delta.days() + 1

def compute_blocks(start: time, end: time) -> int:
    """
    Function to calculate number of blocks availables to use per day
    :param start: start time
    :param end: end time
    :return: number of blocks
    """
    if end <= start:
        raise Exception("End time is earlier or equal than start time")


    actual_start = start.hour + 1 if start.min > 0 else start.hour
    actual_end = start.hour

    blocks = (end - start) // 2
    if blocks == 0:
        raise Exception("Non available blocks to use")
    
    return blocks

def preprocess_parameters(params: Dict) -> Tuple[str, int, int, List[str]]:
    """
    Function to extract and preprocess parameters from input
    :param params: Dictionary of parameters
    :return: tuple containing name of tournament, number of days available,
             number of blocks available for each day and participants in the 
             tournament
    """
    name = params["tournament_name"]
    days = compute_days(params["start_date"], params["end_date"])
    blocks = compute_blocks(params["start_time"], params["end_time"])
    participants = params["participants"]
    return name, days, blocks, participants

def to_var(sign: int, local: int, visit: int, day: int, block: int) -> int:
    return sign * (local + visit * MAXVAR + day * MAXVAR ** 2 + block * MAXVAR ** 3)


def generate_all_vs_all_clauses(days: int, blocks: int, participants: int):

    clauses = []
    for i in range(1, participants+1):
        for j in range(1, participants+1):
            if i != j:
                clause = []
                for d in range(days):
                    for b in range(blocks):
                        clause.append(to_var(1, i, j, d, b))
                clauses.append(clause)
    
    return clauses

def generate_non_rep_clauses(days: int, blocks: int, participants: int):

    clauses = []
    for i in range(1, participants+1):
        for j in range(1, participants+1):
            if i != j:
                for d in range(days):
                    for b in range(blocks):
                        v = to_var(-1, i, j, d, b)
                        for d2 in range(days):
                            if d != d2:
                                for b2 in range(blocks):
                                    clauses.append([v, to_var(-1, i, j, d2, b2)])
    return clauses

def generate_one_per_day_clauses(days: int, blocks: int, participants: int):

    clauses = []
    for i in range(1, participants+1):
        for j in range(1, participants+1):
            if i != j:
                for d in range(days):
                    for b in range(blocks):
                        v = to_var(-1, i, j, d, b)
                        for j2 in range(1, participants + 1):
                            if j2 != i:
                                for b2 in range(blocks):
                                    clauses.append([v, to_var(-1, i, j2, d, b2)])
                                    clauses.append([v, to_var(-1, j2, i, d, b2)])
    return clauses

def generate_non_type_rep_clauses(days: int, blocks: int, participants: int):

    clauses = []
    for i in range(1, participants+1):
        for j in range(1, participants+1):
            if i != j:
                for d in range(days):
                    for b in range(blocks):
                        v = to_var(-1, i, j, d, b)
                        for j2 in range(1, participants + 1):
                            if i != j2:
                                for b2 in range(days):
                                    clauses.append([v, to_var(-1, i, j2, d+1, b2)])
                        for i2 in range(1, participants + 1):
                            if i2 != j:
                                for b2 in range(days):
                                    clauses.append([v, to_var(-1, i2, j, d+1, b2)])
    return clauses

def generate_not_same_time_clauses(days: int, blocks: int, participants: int):

    clauses = []
    for i in range(1, participants+1):
        for j in range(1, participants+1):
            if i != j:
                for d in range(days):
                    for b in range(blocks):
                        v = to_var(-1, i, j, d, b)
                        for i2 in range(1, participants + 1):
                            for j2 in range(1, participants + 1):
                                if i != i2 or j != j2:
                                    clauses.append([v, to_var(-1, i2, j2, d, b)])
    return clauses

def generate_clauses(days: int, blocks: int, participants: int):

    MAXVAR = days * blocks * participants * (participants - 1)
    clauses = []
    clauses.extend(generate_all_vs_all_clauses(days, blocks, participants))
    clauses.extend(generate_non_rep_clauses(days, blocks, participants))
    clauses.extend(generate_one_per_day_clauses(days, blocks, participants))
    clauses.extend(generate_non_type_rep_clauses(days, blocks, participants))