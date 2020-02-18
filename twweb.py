# imports

class TimeWatch:
    """
    Class that embodies TimeWatch data/site.
    This class is a context manager.
    `with` statement opens a chrome driver instance and logs into *TimeWatch* site.
    """

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exception):
        pass

    def login_into_time_watch(self):
        pss

