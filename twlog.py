import logging


class TimeWatchLogger(logging.Logger):
    """
    Subclass for the logger - predefined
    """
    def __init__(self, log_level=logging.DEBUG):
        super().__init__(name='time_watch_logger')
        self.handlers = []
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter('%(levelname)8s - %(asctime)s - %(module)s - %(message)s'))
        self.addHandler(console_handler)
