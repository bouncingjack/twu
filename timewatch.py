import datetime as dt

import twweb
import twargs
import twkml
from random import randint


class Report:
    """
    Represnets the time watch report.
    This will call updating actions.
    """
    
    end_date = None
    start_date = None
    chrome_driver = None
    force_times = None

    
    def __init__(self, start_date, end_date, chrome_driver, force_times=None):
        self.start_date = start_date
        self.end_date = end_date
        self.chrome_driver = chrome_driver
        if force_times:
            self.force_times = [x.split(':') for x in force_times]
        
    def __call__(self):
        with twweb.TimeWatch(chrome_driver=self.chrome_driver, params=params) as tw:
            if self.force_times:
                for d in self.generate_work_dates():
                    start_time = dt.datetime(
                        year=d.year, month=d.month, day=d.day,
                        hour=int(self.force_times[0][0]), 
                        minute=int(self.force_times[0][1]))
                    end_time = dt.datetime(
                        year=d.year, month=d.month, day=d.day,
                        hour=int(self.force_times[1][0]), 
                        minute=int(self.force_times[1][1]))
                    start_time += dt.timedelta(minutes=randint(-43,43))
                    end_time += dt.timedelta(minutes=randint(-43,43))
                    tw.edit_single_date(
                        start_time=twkml.format_time(start_time),
                        end_time=twkml.format_time(end_time),
                        download_date=d)
            else:
                for k in self._gen_kml():
                    tw.edit_single_date(
                        start_time=k.start, 
                        end_time=k.end, 
                        download_date=k.download_date)
    
    def generate_work_dates(self):
        """
        generator of dates in sequence between two given dates.\n
        yields dates in the sequence for iteration only if they are work days.

        :yields: date for upadte
        """
        delta = self.end_date - self.start_date
        for d in range(delta.days + 1):
            tmp_date = self.start_date + dt.timedelta(days=d)
            if self.is_work_day(tmp_date): 
                yield tmp_date 

    def is_work_day(self, date_in_question):

        """
        checks if the date in question is a workday: Sunday - Thursday

        :param datetime: datetime object of the date to check
        :return bool: True for Sunday..Thursday and False otherwise
        """
        return not date_in_question.weekday() in [4, 5]

    def _gen_kml(self):
        yield

class ChromeWebDriver:
    """
    Subclass for the chromedriver - path container
    """

    def __init__(self, executable_path):
        pass




if __name__ == '__main__':
    tw_args = twargs.TWArgs()
    args = tw_args()
    
