import datetime as dt
from math import isclose
import os
from fastkml import kml
import collections
import webbrowser
import platform
import time

import twlog

logger = twlog.TimeWatchLogger()

class KMLFile:
    """
    Represents the KML file itself.
    Encapsulate file operations on KML file
    """

    def __init__(self, file_date, download_dir):
        self.file_date = file_date
        self._file_dir = download_dir



    def __enter__(self):
        self._download_file()
        return self

    def __exit__(self, *exception):
        try:
            os.remove(self._generate_file_name())
            logger.debug('file %s was removed', self._generate_file_name())
        except PermissionError:
            logger.debug('unable to remove file %s', self._generate_file_name())

    def _read_from_file(self):
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
            webbrowser.get('google-chrome').open_new(self._generate_timeline_url())
        elif platform.system() == 'Windows':
            chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path), 1)
            webbrowser.get('chrome').open_new(self._generate_timeline_url())
        else:
            raise ValueError(f'{platform.system()} is not a supported os')

        file_name = self._generate_file_name()
        
        while not os.path.exists(file_name):
            time.sleep(0.5)
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

    def __init__(self, download_date: dt.datetime, chrome_driver, params):
        self.download_date = download_date
        self.download_dir = params.parameters['download_dir']
        self.chrome_driver = chrome_driver 
        self.work_lat = round(float(self._get_value_from_parameters(params, 'work', 'lat')), 5)
        self.work_long = round(float(self._get_value_from_parameters(params, 'work', 'long')), 5)
        self.work_location_tolerance = int(self._get_value_from_parameters(params, 'work', 'tolerance'))
        self.start = None
        self.end = None

    def __enter__(self):
        self._extract_kml_data()
        return self

    def __exit__(self, *exception):
        pass
    
    def _get_value_from_parameters(self, params, value_category, value_name):
        try:
            return params.parameters[value_category][value_name]
        except KeyError:
            raise KeyError(f'{value_category}.{value_name} does not appear in params file')

    def set_workday_hours(self, times):
        self.start = format_time(times['start'])
        self.end = format_time(times['end'])

    def check_time_at_work(self, times, required_diff=1):
        if not times:
            return False
        diff = times['end'] - times['start']
        is_at_work_enough_time = diff > dt.timedelta(hours=required_diff)
        return is_at_work_enough_time

    def _extract_kml_data(self):
        """
        Extract kml data from kml file and into memory.
        Utilize KMLFile context manager to read content of file and deal with it afterwards
        """
        logger.debug('Start kml extraction for %s', self.download_date.strftime('%d-%m-%Y'))
        with KMLFile(file_date=self.download_date, download_dir=self.download_dir) as f:
            doc = f._read_from_file()
            self.kml_data = kml.KML()
            self.kml_data.from_string(doc)


    def _is_at_work(self, coordinates, tolerance):
        """
        check if coordinates provided in placemark is withhin a tolerance of work coordinates
        :param lst coordinates: list of coordinates: lat, long, elevation in Decimal degrees notation
        :params int tolerance: multiplier to determine final search radius around coordinates
        :return: True if provided coordinates are within tolerance of work coordinates
        """

        # round to 3 decimal places - gives a ~100 meters precision
        # assumes to be neighborhood or street
        # https://en.wikipedia.org/wiki/Decimal_degrees
        precision = pow(10, -3)

        is_close_long = isclose(coordinates[0], self.work_long, abs_tol=tolerance * precision)
        is_close_lat = isclose(coordinates[1], self.work_lat, abs_tol=tolerance * precision)

        return is_close_lat and is_close_long


    def _gen_placemarks(self):
        try: 
            for p in self.kml_data._features[0]._features:
                yield {'t': p._time_span, 'coords': p._geometry.geometry.coords}
        except IndexError:
            return 

    def get_work_times(self):
        """
        generator for times at work
        :param string: end or start of day

        :yields: a time point (start or end) that is verfied at work
        """
        start_times = list()
        end_times = list()
        for p in self._gen_placemarks():
            if self._is_at_work(p['coords'][0], self.work_location_tolerance):
                start_times.append(p['t'].begin[0].astimezone())
                end_times.append(p['t'].end[0].astimezone())
        if len(start_times) == 0 or len(end_times) == 0:
            return None
        else:
            return {'start': min(start_times), 'end': max(end_times)}


def format_time(dt):
    Time = collections.namedtuple('Time', ['hour', 'minute'])
    return Time(hour=str(dt.astimezone().hour).zfill(2),
                        minute=str(dt.astimezone().minute).zfill(2))
