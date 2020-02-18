from selenium import webdriver

import twlog

logger = twlog.TimeWatchLogger()

class TimeWatch:
    """
    Class that embodies TimeWatch data/site.
    This class is a context manager.
    `with` statement opens a chrome driver instance and logs into *TimeWatch* site.
    """
    
    _user_cred = ''
    _url = r'https://checkin.timewatch.co.il/punch/punch.php'

    def __init__(self, chrome_driver, params):        
        self._user_cred = params.parameters['user']
        self.chrome_driver = chrome_driver
        self._driver = None

    def __enter__(self):
        self._driver = webdriver.Chrome(self.chrome_driver.driver_path)
        self.login_into_time_watch()
        return self

    def __exit__(self, *exception):
        self._driver.close()

    def login_into_time_watch(self):
        """
        Login into Timewatch website.
        user login information from params file
        """
        logger.debug('Try to login to %s', self._url)
        self._driver.get(self._url)
        self._driver.find_element_by_xpath('// *[@id="compKeyboard"]').send_keys(self._user_cred['company'])
        self._driver.find_element_by_xpath('//*[@id="nameKeyboard"]').send_keys(self._user_cred['worker'])
        self._driver.find_element_by_xpath('//*[@id="pwKeyboard"]').send_keys(self._user_cred['pswd'])
        self._driver.find_element_by_xpath(
            '//*[@id="cpick"]/table/tbody/tr[1]/td/div/div[2]/p/table/tbody/tr[4]/td[2]/input').click()
        logger.info('Logged in for worker %s', self._user_cred['worker'])

    def edit_single_date(self, start_time, end_time, download_date):
        pass


