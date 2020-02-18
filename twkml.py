# imports


class KMLFile:
    """
    Represents the KML file itself.
    Encapsulate file operations on KML file
    """

    def __init__(self):
        pass


    def __enter__(self):
        pass

    def __exit__(self, *exception):
        pass

    def _read_from_file(self):
        pass

    def _download_file(self):
        pass


class KMLData:
    """
    Accepts download date in the ``DD-mm-YYYY`` format
    and generates kml from google for the date given.
    """

    def __init__(self, download_date: dt.datetime, chrome_driver, params):
        pass

    def __enter__(self):
        pass

    def __exit__(self, *exception):
        pass
    
    def set_workday_hours(self, times):
        pass

    def _extract_kml_data(self):
        pass


def format_time(d):
    pass