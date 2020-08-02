import os
import datetime as dt
import platform
from random import randint
from math import isclose
import subprocess
import time
from fastkml import kml

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

    def query_work_date(self):
        if self.is_work_day():
            logger.debug('Data %s is a work day', self._date.strftime('%Y-%m-%d'))
            with KMLFile(file_date=self._date, download_dir=self._download_dir) as f:
                kml_data = f.read()
            k = KMLData(kml_data=kml_data)
            if k.is_at_work(work_location=self._work_location):
                self.mode = 'gps'
                logger.debug('Date %s has valid gps data - work from office', self._date.strftime('%Y-%m-%d'))
                return k.get_work_times(work_location=self._work_location)
            else:
                self.mode = 'non_gps'
                self.excuse = 16
                logger.debug('Date %s has no valid gps data - not in office', self._date.strftime('%Y-%m-%d'))
                return self.spoof_times(
                    start={'hour': 8, 'minute': 0},
                    end={'hour': 17, 'minute': 0})
        else:
            self.mode = 'weekend'

    def is_work_day(self):
        return not self._date.weekday() in [4, 5]

    def spoof_times(self, start: dict, end: dict):
        start_time = dt.datetime(
            year=self._date.year, month=self._date.month, day=self._date.day,
            hour=int(start['hour']),
            minute=int(start['minute']))
        end_time = dt.datetime(
            year=self._date.year, month=self._date.month, day=self._date.day,
            hour=int(end['hour']),
            minute=int(end['minute']))
        start_time += dt.timedelta(minutes=randint(-23, 23))
        end_time += dt.timedelta(minutes=randint(-23, 23))

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
        generator for times at work
        :param string: end or start of day

        :yields: a time point (start or end) that is verfied at work
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
    check if coordinates provided in placemark is withhin a tolerance of work coordinates
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
