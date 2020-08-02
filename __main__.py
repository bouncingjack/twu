import twlog
import twargs

import web
import work
import sys
import time


t = time.time()
logger = twlog.TimeWatchLogger()
logger.info('Start')

a = twargs.TWArgs()
args = a.parse_args(sys.argv)


with web.Timewatch() as tw:
    for d in work.date_list(start_date=args.start_date, end_date=args.end_date):
        tw.update_date(d)


logger.info('Finished in {:.2f} seconds'.format(time.time() - t))
