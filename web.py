from selenium import webdriver
from selenium.webdriver.support.ui import Select
import re
import json
import platform
import os

import twlog
import work

logger = twlog.TimeWatchLogger()


class Timewatch:

    def __init__(self, chrome_driver_path=os.path.join(os.path.dirname(__file__), 'executables', 'chromedriver'),
                 params_file=os.path.join(os.path.dirname(__file__), 'params.json'),
                 overwrite=False,
                 url=r'https://checkin.timewatch.co.il/punch/punch.php'):

        with open(params_file, 'r') as f:
            params = json.loads(f.read())

        self._user_cred = params['user']
        self._url = url
        
        self._holiday_index = params['holiday']['holiday_index']
        self._holiday_text = params['holiday']['holiday_text']

        self._holiday_eve_index = params['holiday']['holiday_eve_index']
        self._holiday_eve_text = params['holiday']['holiday_eve_text']

        self._download_dir = params['download_dir']

        self._work_location = params['work']

        self.excuse = params['home']['work_from_home_excuse_index']

        if platform.system() == 'Windows':
            self._driver = webdriver.Chrome(chrome_driver_path + '.exe')
        elif platform.system() == 'Linux':
            self._driver = webdriver.Chrome(chrome_driver_path)

        self._overwrite = overwrite

    def update_date(self, d):
        wd = work.WorkDate(date=d, download_dir=self._download_dir, work_location=self._work_location)
        work_day_times = wd.query_work_date()
        if not wd.mode == 'weekend':
            self._driver.get(self._generate_specific_date_url(edit_date=d))
            if self.is_holiday():
                self._clear_all_hours()
                self._set_excuse_value(int(self._holiday_index))
                logger.info('Set date as vacation')
            elif self.is_holdiay_eve():
                self._clear_all_hours()
                self._set_excuse_value(int(self._holiday_eve_index))
                logger.info('Set date as holiday eve')
            elif wd.mode == 'non_gps':
                self._clear_all_hours()
                self.fill_hours(work_day_times)
                self._set_excuse_value(self.excuse)
            elif wd.mode == 'gps':
                self._clear_all_hours()
                self.fill_hours(work_day_times)
            else:
                raise RuntimeError(
                    'date {} is neither holiday, nor eve nor work home nor office'.format(d.strftime('%d-%m-%Y')))
            self._click_enter()

    def fill_hours(self, work_day_times):
        self._enter_value(element_id='ehh', value=work_day_times['start'].hour)
        self._enter_value(element_id='emm', value=work_day_times['start'].minute)
        self._enter_value(element_id='xhh', value=work_day_times['end'].hour)
        self._enter_value(element_id='xmm', value=work_day_times['end'].minute)

    def _click_enter(self):
        enter_possibles = [x for x in self._driver.find_elements_by_tag_name('input') if
                           'update.jpg' in x.get_attribute('src')]
        if len(enter_possibles) > 1:
            raise TooManyUpdateButtons('too many inputs with update.jpg image found')
        enter = enter_possibles[0].click()

    def _set_excuse_value(self, excuse_index):
        if excuse_index:
            element_options = Select(self._driver.find_element_by_name('excuse'))
            element_options.select_by_index(excuse_index)
            logger.debug('Set excuse %s', element_options.options[excuse_index].text)

    def is_holiday(self):
        """
        Checks whether current date is a holiday.
        Criteria is based on
        :return:
        """
        return set(self._get_date_text_ascii()) == set([int(x) for x in self._holiday_text])

    def is_holdiay_eve(self):
        return set(self._get_date_text_ascii()) == set([int(x) for x in self._holiday_eve_text])

    def _get_date_text_ascii(self):
        element = self._driver.find_element_by_xpath(
            '/html/body/div/span/form/table/tbody/tr[7]/td/table/tbody/tr/td[2]/font[2]/b')
        return [ord(x) for x in getattr(element, 'text').strip()]

    def _clear_all_hours(self):
        element_list = ['ehh', 'xhh', 'emm', 'xmm']
        row_number = [0, 1, 2, 3]
        for row in row_number:
            for e in element_list:
                element = self._driver.find_elements_by_id('{}{}'.format(e, str(row)))
                element[0].clear()

    def _enter_value(self, element_id, value):
        """
        Enter values into specific place in webpage - specified by id

        :param str id: id of the element into which value will be entered
        :param str value: hours/minute in 24H format to be entered to the element located using x_path parameter
        :return:
        """
        element = self._driver.find_element_by_id('{}0'.format(element_id))
        element.send_keys(value)

    def _generate_specific_date_url(self, edit_date):
        """
        generate url for specific date edit form in the TimeWatch webpage.
        requires session to be logged in

        :param datetime edit_date: date that needs to be edited
        :return str: url for direct edit form for edit_date
        """
        self._set_token()
        base_url = 'http://checkin.timewatch.co.il/punch/editwh2.php?ie='
        comp_num = str(self._user_cred['company']) + '&e=' + str(self._user_cred['token']) + '&d='
        start_date = str(edit_date.year) + '-' + str(edit_date.month) + '-' + str(edit_date.day) + '&jd='
        end_date = str(edit_date.year) + '-' + str(edit_date.month) + '-' + str(edit_date.day + 1) + '&tl=' \
                   + str(self._user_cred['token'])
        return base_url + comp_num + start_date + end_date

    def _set_token(self):
        """
        checks if user token has already been processed. if so, does nothing.
        if not, this function recovers user token from source of web page and puts it in this class user credential paramters.
        :return: Nothing

        """
        if 'token' in self._user_cred.keys():
            logger.debug('user token already set')
        else:
            logger.debug('setting user token')

            elems = [e.get_attribute('href') for e in self._driver.find_elements_by_xpath("//a[@href]")]
            elems = [e for e in elems if 'editwh.php' in e]
            try:
                match = re.search(pattern=(r'(?<=ee\=)\d*(?=\&e)'), string=elems[0])
            except IndexError as e:
                raise IndexError('source of html page has no href with token')

            if match:
                self._user_cred['token'] = match[0]
            else:
                raise ValueError('did not extract token from %s', elems[0])

    def __enter__(self):
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
        self._driver.find_element_by_xpath(
            '// *[@id="compKeyboard"]').send_keys(self._user_cred['company'])
        self._driver.find_element_by_xpath(
            '//*[@id="nameKeyboard"]').send_keys(self._user_cred['worker'])
        self._driver.find_element_by_xpath(
            '//*[@id="pwKeyboard"]').send_keys(self._user_cred['pswd'])
        self._driver.find_element_by_xpath(
            '//*[@id="cpick"]/table/tbody/tr[1]/td/div/div[2]/p/table/tbody/tr[4]/td[2]/input').click()
        logger.info('Logged in for worker %s', self._user_cred['worker'])


class TooManyUpdateButtons(Exception):
    pass
