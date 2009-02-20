import datetime
import time

class Delta:

    def __init__(self, timedelta):
        assert(isinstance(timedelta, datetime.timedelta))
        self.timedelta = timedelta

    def __str__(self):
        return str(self.timedelta)

    def __getYears(self):
        return self.timedelta.days / 365

    def __getDays(self):
        return self.timedelta.days % 365

    def __getHours(self):
        return self.timedelta.seconds / 60 / 24

    def __getMinutes(self):
        return self.timedelta.seconds / 60 - self.hours * 60

    def __getSeconds(self):
        return self.timedelta.seconds % 60

    def __getMicroSeconds(self):
        return self.timedelta.milliseconds

    def asString(self):
        s = str(self.seconds) + "s"
        for value, unit in [(self.minutes, "m"),
                            (self.hours, "h"),
                            (self.days, "d"),
                            (self.years, "y")]:
            if value > 0:
                s = str(value) + unit + " " + s
        return s

    years = property(__getYears)
    days = property(__getDays)
    hours = property(__getHours)
    minutes = property(__getMinutes)
    seconds = property(__getSeconds)
    microseconds = property(__getMicroSeconds)
