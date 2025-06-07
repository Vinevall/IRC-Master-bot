import holidays
from datetime import date, datetime, timedelta
import json
import os
from collections import defaultdict
from .printlog import Log

log = Log()

class CalendarManager:
    def __init__(self, year=2025, country="SE"):
        self.year = year
        self.country = country
        self.filename = f"kalender_{self.year}.json"

        if os.path.exists(self.filename):
            log.info(f"Opening file: {self.filename}")
            self._read_json(self.filename)
        else:
            log.info(f"Creating a new file: {self.filename}...")
            log.info("Polulating the file with data...")
            self.data = {
                "Holidays": self._get_holidays(),
                "Weekends": self._get_weekends(),
                "Vacations": {}
            }
            self._save_json(self.filename)

    def _format_date(self, date: date) -> str:
        return date.strftime("%y%m%d")

    def _validate_date(self, datum_str: str) -> bool:
        try:
            datetime.strptime(datum_str, "%y%m%d")
            return True
        except ValueError:
            return False

    def _get_weekends(self):
        start = date(self.year, 1, 1)
        end = date(self.year, 12, 31)
        delta = timedelta(days=1)

        saturdays = []
        sundays = []

        current = start
        while current <= end:
            if current.weekday() == 5:
                saturdays.append(self._format_date(current))
            elif current.weekday() == 6:
                sundays.append(self._format_date(current))
            current += delta

        # Needs fixing
        return {
            "Lördag": saturdays,
            "Söndag": sundays
        }

    def _get_holidays(self):
        all_holidays = holidays.country_holidays(self.country, years=[self.year])
        result = {}

        for day, name in all_holidays.items():
            pretty_name = name.title()
            datum = self._format_date(day)
            if pretty_name != "Söndag": # Needs fixing
                if pretty_name not in result:
                    result[pretty_name] = []
                if datum not in result[pretty_name]:
                    result[pretty_name].append(datum)

        return result

    def _save_json(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
            log.info(f"{filename} is now saved...")

    def _read_json(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def _date_to_week(self, datum_lista: list[str]) -> dict[int, list[str]]:
        weeks = defaultdict(list)
        for datum_str in datum_lista:
            try:
                datum = datetime.strptime(datum_str, "%y%m%d").date()
                week = datum.isocalendar()[1]
                weeks[week].append(datum_str)
            except ValueError:
                continue
        return dict(weeks)

    def print_json(self):
        print(json.dumps(self.data, indent=2, ensure_ascii=False))

    def check_date(self, datum):
        # Search in holidays
        for name, datelist in self.data["Holidays"].items():
            if datum in datelist:
                try:
                    key, value = name.split(";")
                except ValueError:
                    return name
                else:
                    return key
        
        # Search in holidays
        for name, datelist in self.data["Weekends"].items():
            if datum in datelist:
                return name

        return None

    def add_vacation(self, name: str, items: list[str]) -> str:
        name = name.strip().capitalize()
        message = ""

        if "Vacations" not in self.data:
            self.data["Vacations"] = {}
        if name not in self.data["Vacations"]:
            self.data["Vacations"][name] = []

        for item in items:
            item = item.strip().lower()
            
            # Handeling weeknumbers
            if item.startswith("v") and item[1:].isdigit():  
                week = int(item[1:])
                try:
                    for day in range(1, 8):  # måndag (1) till söndag (7)
                        datum = date.fromisocalendar(self.year, week, day)
                        datum_str = datum.strftime("%y%m%d")
                        if datum_str not in self.data["Vacations"][name]:
                            self.data["Vacations"][name].append(datum_str)
                            message = f"Vecka: {item} är nu registrerad som semester"
                        else:
                            message = f"Vecka: {item} finns redan registrerad som semester"
                except ValueError:
                    message = f"Ogiltig vecka: {item}"

            # Hantera datum i format YYMMDD
            elif item.isdigit() and len(item) == 6:
                if self._validate_date(item):
                    if item not in self.data["Vacations"][name]:
                        self.data["Vacations"][name].append(item)
                        message = f"Datum: {item} är nu registrerad som semester"
                    else:
                        message = f"Datum: {item} finns redan registrerad som semester"
                else:
                    message = f"Ogiltigt datum: {item}"

            else:
                message = f"Ogiltigt format ignorerat: {item}"

        self._save_json(self.filename)

        return message

    def del_vacation(self, name: str, items: list[str]):
        name = name.strip().capitalize()

        if "Vacations" not in self.data or name not in self.data["Vacations"]:
            print(f"Användaren '{name}' har inga registrerade semestrar.")
            return

        for item in items:
            item = item.strip().lower()

            if item.startswith("v") and item[1:].isdigit() and len(item[1:]) == 2:
                week = int(item[1:])
                try:
                    for day in range(1, 8):
                        datum = date.fromisocalendar(self.year, week, day)
                        datum_str = datum.strftime("%y%m%d")
                        if datum_str in self.data["Vacations"][name]:
                            self.data["Vacations"][name].remove(datum_str)
                except ValueError:
                    print(f"Veckan({item}) du vill raddera för {name} är inte registrerad")

            elif item.isdigit() and len(item) == 6:
                if self._validate_date(item):
                    if item in self.data["Vacations"][name]:
                        self.data["Vacations"][name].remove(item)
                else:
                    print(f"Ogiltigt datum: {item}")

            else:
                print(f"Ogiltigt format ignorerat: {item}")


    def todays_work_force(self, datum: str, team: list[str]) -> list[str]:
        if not self._validate_date(datum):
            log.error(f"Ogiltigt datumformat: {datum}")
            return []

        workers = []

        for person in team:
            on_vacation = self.data.get("Vacations", {}).get(person, [])
            if datum not in on_vacation:
                workers.append(person)

        return workers

    def list_all_vacations(self):
        if "Vacations" not in self.data:
            print("📭 Inga semestrar registrerade.")
            return

        for person, datum_lista in self.data["Vacations"].items():
            print(f"\n🧑 {person}:")
            weeks = self._date_to_week(datum_lista)
            hole_weeks = []
            other_dates = []

            for week, datum in sorted(weeks.items()):
                if len(datum) == 7:
                    hole_weeks.append(f"v{str(week).zfill(2)}")
                else:
                    other_dates.extend(sorted(datum))

            if hole_weeks:
                print(f"  📆 Veckor: {', '.join(hole_weeks)}")
            if other_dates:
                print(f"  📅 Datum:  {', '.join(other_dates)}")


