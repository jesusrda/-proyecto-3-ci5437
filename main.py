import argparse
import subprocess
import os

from pathlib import Path, PurePath
from datetime import time

from preprocess import read_file, preprocess_parameters
from sat_generator import SAT
from ical_generator import ICal
from postprocess import extract_from_result

class CLIArgs:
    """
    Class used to parse and operate with command line arguments for the main execution
    """

    def generate_cal(self):
        """
        Returns true if we pretend to generate de .ics file, false otherwise
        """
        return self.ical is not None

    def generate_sat(self):
        """
        Returns true if we pretend to only generate sat model, false otherwise
        """
        return self.sat is not None

    def get_input_file_path(self):
        """
        Extracts json input file path from command line arguments
        """
        if (self.generate_cal()):
            filename = self.ical[0]
        else:
            filename = self.sat[0]

        if PurePath(filename).suffix != ".json":
            raise Exception(f"file extension for {filename} not allowed.")

        return filename
    
    def get_output_file_path(self):
        """
        Extracts output file path from command line arguments
        """
        if (self.generate_cal()):
            filename = self.ical[1]
        else:
            filename = self.sat[1]

        if self.generate_cal() and PurePath(filename).suffix != ".ics":
            raise Exception(f"file extension for {filename} not allowed.")

        if self.generate_sat() and PurePath(filename).suffix != ".cnf":
            raise Exception(f"file extension for {filename} not allowed.")

        return filename

def run(args: CLIArgs) -> None:
    """ Main flow of execution """

    input_file_path = args.get_input_file_path()
    output_file_path = args.get_output_file_path()

    if args.generate_cal():
        output_sat_file_path = str(PurePath(output_file_path).with_suffix(".cnf"))
    elif args.generate_sat():
        output_sat_file_path = output_file_path

    print(f"Scanning tournament parameters...")
    tournament_params = read_file(input_file_path)
    name, days, blocks, participants = preprocess_parameters(tournament_params)
    print(f"Tournament parameters scanned.")
    
    print(f"Generating SAT model in {output_sat_file_path}...")
    sat_generator = SAT(name, days, blocks, len(participants))
    sat_generator.generate_model(output_sat_file_path)
    print(f"SAT model generated.")

    if args.generate_cal():
        # Trying to generate iCalendar file
        print(f"Calculating SAT result using Glucose...")
        sat_result_file_path = str(PurePath(output_sat_file_path).with_suffix(".out"))
        cmd = f'./glucose -model -verb=0 {output_sat_file_path} | egrep "^s|^v" > {sat_result_file_path}'
        p = subprocess.Popen(cmd, shell=True)
        os.waitpid(p.pid, 0)
        print(f"Result calculated.")

        result = extract_from_result(sat_result_file_path)
        if result:
            matches = sat_generator.from_vars(result)
            print(f"Generating Ical file in {output_file_path}...")
            start_date = tournament_params["start_date"]
            start_time = tournament_params["start_time"]
            cal_generator = ICal(name, participants, start_date, start_time)
            cal_generator.generate_ical(output_file_path, matches)
            print(f"Ical file generated.")
        else:
            print("There is not any possible match scheduling that satisfies tournament conditions.")



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Tournament scheduling.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--sat', nargs=2, type=str, metavar=("<input-json-file>", "<output-Ical-file>"))
    group.add_argument('--ical', nargs=2, type=str, metavar=("<input-json-file>", "<output-Ical-file>"))
    
    args = CLIArgs()
    parser.parse_args(namespace=args)

    if not args.generate_cal() and not args.generate_sat():
        parser.print_usage()
    else:
        try:
            run(args)
        except Exception as ex:
            print(f"error: {ex}")

    