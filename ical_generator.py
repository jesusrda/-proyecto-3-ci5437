import sys

from typing import List
from datetime import date, time, timedelta, datetime

from ics import Calendar, Event

class ICal:

    def __init__ (self, 
                 name: str, 
                 participants: List[str],
                 start_date: date,
                 start_time: time):

        self.name = name
        self.participants = participants
        self.start_date = start_date
        self.start_time = start_time
        self.cal = Calendar()

    def generate_ical(self, filename: str, matches: List) -> None:

        for match in matches:
            
            e = Event()
            
            local, visit, day, block = match
            
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

            
if __name__ == "__main__":

    name = "test"
    participants = ["1", "2", "3", "4"]
    start_date = date(2021, 7, 20)
    start_time = time(12, 00)
    cal = ICal(name, participants, start_date, start_time)
    matches = [(0, 1, 0, 0), (2, 3, 0, 1), (3, 0, 1, 0), (1, 2, 1, 1)]
    cal.generate_ical("result.ics", matches)