import sys

from typing import List
from datetime import date, time, timedelta, datetime

from ics import Calendar, Event

class ICal:
    """
    Generator of ICalendar .ics files
    """

    def __init__ (self, 
                 name: str, 
                 participants: List[str],
                 start_date: date,
                 start_time: time):
        """
        Class constructor
        :param name: Name of tournament
        :param participants: List of participants of the tournament
        :param start_date: Initial date of tournament
        :param start_time: Initial time of tournament for each day
        """
        self.name = name
        self.participants = participants
        self.start_date = start_date
        self.start_time = start_time
        self.cal = Calendar()

    def generate_ical(self, filename: str, matches: List) -> None:
        """
        Function to generate ICalendar .ics file
        :param filename: Path of output file
        :param matches: Tuples describing matches to schedule
        """
        for local, visit, day, block in matches:
            
            e = Event()
            
            local_name = self.participants[local]
            visit_name = self.participants[visit]

            e.name = f"{local_name} vs {visit_name}"
            
            days_delta = timedelta(days=day)
            start_date = self.start_date + days_delta
            
            begin = datetime(
                year=start_date.year,
                month=start_date.month,
                day=start_date.day,
                hour=self.start_time.hour + 2*block
            )

            e.begin = begin 
            e.duration = timedelta(hours=2)

            self.cal.events.add(e)

        with open(filename, "w") as f:
            f.writelines(self.cal)