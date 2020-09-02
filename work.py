"""
This module abstract a single work date and deals with all the aspects of extracting data
and meta data about and from this specific date: gps data, determining if work day, holiday etc.
"""

import os
import datetime as dt
import platform
from random import randint
from math import isclose
import subprocess
import time
from fastkml import kml
import calendar
import re

import twlog

logger = twlog.TimeWatchLogger()


class WorkDate:

    def __init__(self, date, download_dir, work_location):
        self._date = date
        self.mode = ''
        self.excuse = None
        self.work_day_times = {}
        self._download_dir = download_dir
        self._work_location = work_location
        logger.debug('Initialized date %s', date.strftime('%Y-%m-%d'))

    def query_work_date(self, work_day, weekend):
        """
        Checks whether current date has gps data or not.
        Downloads a kml file from google timeline.
        mode is set to 'gps' if the kml file indicated that were at work at current date.
        Otherwise `mode` will be 'non-gps'.
        In case the day a weekend, mode will be set to 'weekend'
        :param dict work_day: workday configuration from the JSON parameters file
        :param list weekend: list of the names of the days in the weekend
        :return:
        """
        if self.is_work_day(weekend):
            logger.debug('Data %s is a work day', self._date.strftime('%Y-%m-%d'))
            self.mode = 'non_gps'
            if self._work_location is not None:
            with KMLFile(file_date=self._date, download_dir=self._download_dir) as f:
                kml_data = f.read()
            k = KMLData(kml_data=kml_data)
            if k.is_at_work(work_location=self._work_location):
                self.mode = 'gps'
            if self.mode == 'gps':
                logger.debug('Date %s has valid gps data - work from office', self._date.strftime('%Y-%m-%d'))
                return k.get_work_times(work_location=self._work_location)
            elif self.mode == 'non_gps':
                logger.debug('Date %s has no valid gps data - not in office', self._date.strftime('%Y-%m-%d'))
                if work_day['randomize']:
                    return self.spoof_times(work_day=work_day)
                else:
                    return self.fixed_times(work_day=work_day)
        else:
            self.mode = 'weekend'

    def is_work_day(self, weekend):
        """
        Check is current date is a weekday based on provided data in the parameters file.
        :param list weekend: Names of the weekend days
        :return: bool. True if current date is part of :param: weekend.
        """
        return not self._date.weekday() in [ii for ii, x in enumerate(list(calendar.day_name)) if x in weekend]

    def spoof_times(self, work_day: dict) -> dict:
        """
        Randomizes start and end times in the day.
        Randomization is based on [work][work_day] parameters.

        Randomize starting from the minimal start time with 0-2 hours.
        Randomize end such that work day won't be longer than max length day [hours] or shorter than nominal-1 [hours]
        or that is won't end past maximal end time, as provided in the parameters file.

        :param dict work_day: the parsed input from JSON parameters file section [work][work_day]
        :return: dict with start datetime object and end datetime object representing the start/end of workday
        """
        ptn = r'(?P<hour>\d+)\:(?P<minute>\d+)'
        match_min = re.search(pattern=ptn, string=work_day['minimal_start_time'])
        match_max = re.search(pattern=ptn, string=work_day['maximal_end_time'])
        start_time = dt.datetime(
            year=self._date.year, month=self._date.month, day=self._date.day,
            hour=int(match_min.group('hour')) + randint(0, 2),
            minute=int(randint(0, 59)))
        end_time = start_time
        delta = end_time - start_time
        while delta.seconds // 3600 > work_day['max_length'] or \
                delta.seconds // 3600 < work_day['nominal_length'] - 1 or \
                end_time.hour > int(match_max.group('hour')):
            end_time = dt.datetime(
                year=self._date.year, month=self._date.month, day=self._date.day,
                hour=start_time.hour + work_day['nominal_length'] + randint(-1, 1),
                minute=int(randint(0, 59)))
            delta = end_time - start_time

        return {'start': start_time, 'end': end_time}

    def fixed_times(self, work_day: dict) -> dict:
        """
        Generate start and end dates according to the provided parameters.
        Start time is set to the minimal_start_time value, and
        end time is set to the maximal_start_time value.

        :param dict work_day: the parsed input from JSON parameters file section [work][work_day]
        :return: dict with start datetime object and end datetime object representing the start/end of workday
        """
        ptn = r'(?P<hour>\d+)\:(?P<minute>\d+)'
        match_min = re.search(pattern=ptn, string=work_day['minimal_start_time'])
        match_max = re.search(pattern=ptn, string=work_day['maximal_end_time'])
        start_time = dt.datetime(
            year=self._date.year, month=self._date.month, day=self._date.day,
            hour=int(match_min.group('hour')),
            minute=int(match_min.group('minute')))
        end_time = dt.datetime(
            year=self._date.year, month=self._date.month, day=self._date.day,
            hour=int(match_max.group('hour')),
            minute=int(match_max.group('minute')))

        return {'start': start_time, 'end': end_time}

class KMLFile:
    """
    Represents the KML file itself.
    Encapsulate file operations on KML file
    """

    def __init__(self, file_date, download_dir):
        self.file_date = file_date
        self._file_dir = download_dir
        self._download_process = None

    def __enter__(self):
        self._download_file()
        return self

    def __exit__(self, *exception):
        try:
            os.remove(self._generate_file_name())
            logger.debug('file %s was removed', self._generate_file_name())
        except PermissionError:
            logger.debug('unable to remove file %s',
                         self._generate_file_name())
        logger.debug('attempt to close download file browser window')
        self._download_process.kill()

    def read(self):
        """
        read kml data from the saved file into a raw string
        :return:
        """
        with open(file=self._generate_file_name(), mode='rb') as f:
            return f.read()

    def _generate_file_name(self):
        """
        Generate file name for the downloaded kml file.

        :return str: full path to file name with .kml extension
        """
        return os.path.join(
            self._file_dir, 'history-' + dt.datetime.strftime(self.file_date, '%Y-%m-%d') + '.kml')

    def _generate_timeline_url(self):
        """
        Generates url to download kml file from google based on required date.

        :return str: kml download link for class instance date
        """

        base_url = r'https://www.google.com/maps/timeline/kml?authuser=0&pb=!1m8!1m3!1'
        start_date_str = ('i' + str(self.file_date.year)
                          + '!2i' + str(self.file_date.month - 1)
                          + '!3i' + str(self.file_date.day))
        end_date_str = start_date_str

        out = base_url + start_date_str + '!2m3!1' + end_date_str
        logger.debug('Google Timeline download link is %s', out)
        return out

    def _download_file(self):
        logger.debug('Start download of kml file')
        if platform.system() == 'Linux':
            self._download_process = subprocess.Popen(args=('google-chrome', self._generate_timeline_url()),
                                                      stdout=subprocess.PIPE,
                                                      stdin=subprocess.PIPE,
                                                      stderr=subprocess.PIPE)
        elif platform.system() == 'Windows':
            chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            self._download_process = subprocess.Popen(args=(chrome_path, self._generate_timeline_url()),
                                                      stdout=subprocess.PIPE,
                                                      stdin=subprocess.PIPE,
                                                      stderr=subprocess.PIPE)
        else:
            raise ValueError(f'{platform.system()} is not a supported os')

        file_name = self._generate_file_name()

        counter = 0
        max_cycles = 1000
        sleep_time = 0.5  # seconds
        while not os.path.exists(file_name):
            if counter > max_cycles:
                raise RuntimeError(
                    'more that {} seconds waiting for file to be download - stopping'.format(
                        str(sleep_time * max_cycles)))
            else:
                time.sleep(sleep_time)
                counter += 1

        else:
            logger.debug('Finished kml file download: %s', file_name)


class KMLData:
    """
    Accepts download date in the ``DD-mm-YYYY`` format
    and generates kml from google for the date given.
    """

    kml_data = ''
    download_date = ''
    _driver = ''

    def __init__(self, kml_data):
        self.kml_data = kml.KML()
        self.kml_data.from_string(kml_data)
        self.work_date_times = {'start': {'hour': None, 'minute': None}, 'end': {'hour': None, 'minute': None}}
        self.work_location_tolerance = 3

    def is_at_work(self, work_location):
        try:
            work_times = self.get_work_times(work_location=work_location)
            return bool(work_times)
        except ValueError:
            return False

    def _gen_placemarks(self):
        try:
            for p in self.kml_data._features[0]._features:
                yield {'t': p._time_span, 'coords': p._geometry.geometry.coords}
        except IndexError:
            return

    def get_work_times(self, work_location):
        """
        Parses all the placemarks in the kml data and extract coordinates of each mark.
        Coordinates are measured for distance from work location (provided :param:)
        Each placemark that is deemed to be close enough to the work location is measured for
        time at arrival and departure.
        The largest difference (first arrival and last departure) are returned as total time spent at work.

        :param dict work_location: lat and long work location - from JSON paramters

        :returns: dict minimal start time and maximal end time
        """
        start_times = list()
        end_times = list()
        for p in self._gen_placemarks():
            if is_within_distance(work_location, p['coords'][0], self.work_location_tolerance):
                start_times.append(p['t'].begin[0].astimezone())
                end_times.append(p['t'].end[0].astimezone())
        try:
            return {'start': min(start_times), 'end': max(start_times)}
        except ValueError:
            return None


def date_list(start_date, end_date):
    """
    generator of dates in sequence between two given dates.\n
    yields dates in the sequence for iteration only if they are work days.

    :yields: date for upadte
    """
    delta = end_date - start_date
    for d in range(delta.days + 1):
        tmp_date = start_date + dt.timedelta(days=d)
        yield tmp_date


def is_within_distance(work_location, coordinates, tolerance):
    """
    Checks if coordinates provided are withhin a tolerance of the work location.

    :param lst coordinates: list of coordinates: lat, long, elevation in Decimal degrees notation
    :param int tolerance: multiplier to determine final search radius around coordinates
    :param dict work_location: lat and long of work location
    :return: True if provided coordinates are within tolerance of work coordinates
    """

    # round to 3 decimal places - gives a ~100 meters precision
    # assumes to be neighborhood or street
    # https://en.wikipedia.org/wiki/Decimal_degrees
    precision = pow(10, -3)

    is_close_long = isclose(coordinates[0], round(float(work_location['long']), 5), abs_tol=tolerance * precision)
    is_close_lat = isclose(coordinates[1], round(float(work_location['lat']), 5), abs_tol=tolerance * precision)

    return is_close_lat and is_close_long
