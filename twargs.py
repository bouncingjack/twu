import argparse
import os
import datetime as dt
import platform


class TWArgs:

    def __init__(self):
        # TODO add mutually exclusive groups for --month --year and --start/end dates
        # TODO add verification class for month and year
        self.parser = argparse.ArgumentParser(
            description='Build and import projects')
        self.parser.add_argument('--start-date', dest='start_date', action=VerifyDateFormatAction,
                                 help='enter start date (included) in DD-MM-YYYY format')
        self.parser.add_argument('--end-date', dest='end_date', action=VerifyDateFormatAction,
                                 help='enter end date (included) in DD-MM-YYYY format')
        self.parser.add_argument('--parameters-file',
                                 dest='parameters_file',
                                 default=os.path.join(os.path.dirname(__file__), 'params', 'params.json'),
                                 help='full path to local parameters file')

    def parse_args(self, argv):
        args_output = self.parser.parse_args(args=argv[1::])

        if args_output.start_date and args_output.end_date:
            if args_output.start_date > args_output.end_date:
                raise ValueError('start date is after end date')

        return args_output


class VerifyDateFormatAction(argparse.Action):
    """
    Action subclass to verfiy that dates provided by cli are in the correct format.
    This class is callable.
    """
    DATE_FORMAT_LIST = ['d', 'm', 'Y']
    DATE_FORMAT_DIGIT_NUMS = [2, 2, 4]

    def __call__(self, parser, namespace, values, option_string=None):
        """
        Call function when this class is called.
        Checks that the format of the input 'values' (str) is correct - based on the class attributes:
        DATE_FORMAT_LIST - list of chars that comprise the format
        DATE_FORMAT_DIGIT_NUMS - number of repetitions of each char in DATE_FROMAT_LIST.

        If 'values' is provided in the correct format, A datetime object is created from 'values' string
        and passed into namespace. This datetime object will be passed subsequently in the 'args' tuple
        at the output of the argument parser function.

        :param parser: (parser object) that calls this callable
        :param namespace: (namespace object) into which args are provided
        :param values: (str) arguments provided by cli
        :param option_string: (str) not used in the instance
        :return: Nothing
        """
        try:
            tmp = dt.datetime.strptime(values, '%' + '-%'.join(self.DATE_FORMAT_LIST))
            setattr(namespace, self.dest, tmp)
        except ValueError:
            msg = '{} is not a a valid date. please use format: {}'.format(
                values, '-'.join(
                    [x * y for x, y in zip(self.DATE_FORMAT_LIST, self.DATE_FORMAT_DIGIT_NUMS)]))
            raise argparse.ArgumentTypeError(msg)
