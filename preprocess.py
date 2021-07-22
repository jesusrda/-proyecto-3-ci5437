import json

from datetime import date, time
from pathlib import Path
from typing import Dict, List, Tuple

def read_file(filename: str) -> Dict:
    """
    Function to read json file containing problem parameters
    :param filename: Path to file to read
    :return: Dictionary containing parameters
    """
    if not Path(filename).exists():
        raise Exception(f"file {filename} does not exists.")
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
    delta = end - start
    return delta.days + 1

def compute_blocks(start: time, end: time) -> int:
    """
    Function to calculate number of blocks availables to use per day
    :param start: start time
    :param end: end time
    :return: number of blocks
    """
    end_hour = 24 if end == time.min else end.hour
    blocks = (end_hour - start.hour) // 2
    if blocks <= 0:
        raise Exception("Non available blocks to use")
    
    return blocks

def preprocess_date_and_time(params: Dict) -> None: 
    """
    Function to pars date and time parameters from input
    :param params: Tournaments parameters
    """
    start_date = date.fromisoformat(params["start_date"])
    end_date = date.fromisoformat(params["end_date"])

    if end_date < start_date:
        raise Exception(f"End date is earlier than start date.")
            
    start_time = time.fromisoformat(params["start_time"])
    end_time = time.fromisoformat(params["end_time"])

    if end_time != time.min and end_time <= start_time:
        raise Exception("End time is earlier or equal than start time")
    
    actual_start = time(start_time.hour + 1 if start_time.minute + start_time.second + start_time.microsecond > 0 
                                            else start_time.hour)
    actual_end = time(end_time.hour)

    if actual_end == time.min and end_time != time.min:
        raise Exception("Non available blocks to use")
    
    params.update({
        "start_date": start_date,
        "end_date": end_date,
        "start_time": actual_start,
        "end_time": actual_end
        })

def preprocess_parameters(params: Dict) -> Tuple[str, int, int, List[str]]:
    """
    Function to extract and preprocess parameters from input
    :param params: Dictionary of parameters
    :return: tuple containing name of tournament, number of days available,
             number of blocks available for each day and participants in the 
             tournament
    """
    name = params["tournament_name"]
    preprocess_date_and_time(params)
    days = compute_days(params["start_date"], params["end_date"])
    blocks = compute_blocks(params["start_time"], params["end_time"])
    participants = params["participants"]
    return name, days, blocks, participants