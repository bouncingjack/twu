from selenium import webdriver
from selenium.webdriver.support.ui import Select
import re

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

    def __init__(self, chrome_driver, params, overwrite=False):        
        self._user_cred = params.parameters['user']
        try:
            self._holiday_index = params.parameters['holiday_index']
        except KeyError:
            logger.info('no holiday_index section in parameters, setting to default')
            self._holiday_index= {'vacation_index': 3, 'eve_text':  [1506, 1512, 1489, 32, 1495, 1490], 'eve_index': 17, 'vacation_text': [1495, 1490]}
        self.chrome_driver = chrome_driver
        self._driver = None
        self.overwrite = overwrite

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

    def edit_single_date(self, download_date, start_time=None, end_time=None, excuse=None):
        """
        Enter values into a single date form
        if input is None ,will not enter it
        :param tuple start: the time of the start end of the workday, default is None 
        :param tuple end: the time of the end of the workday, default is None
        :param datetime download_date: the date of the kml data
        :param Boolean overwrite: if True will overwrite values, if not will leave them as they are
        :param int excuse: index of the excuse that will be used. default is None
        :return: Nothing
        """

        
        self._driver.get(self._generate_specific_date_url(edit_date=download_date))
        self.set_excuse(excuse_index=excuse)
        if not (self.is_holdiay_eve() or self.is_holiday()):
            self._fill_hours(start_time=start_time, end_time=end_time)      
        self._click_enter()

        logger.info('Finished updating for %s', download_date.strftime('%d-%m-%Y'))

    def _fill_hours(self, start_time, end_time):
        if self.overwrite:
            self._clear_all_hours()
            if start_time and end_time:
                
                self._enter_value(element_id='ehh', value=start_time.hour)
                self._enter_value(element_id='emm', value=start_time.minute)
                logger.debug('Entered entrance time: %d:%d', start_time.hour, start_time.minute)
                
                self._enter_value(element_id='xhh', value=end_time.hour)
                self._enter_value(element_id='xmm', value=end_time.minute)
                logger.debug('Entered exit time: %d:%d', end_time.hour, end_time.minute)
        else:
            logger.debug('Not filling in hours because overwrite is not allowed')

    def _click_enter(self):
        enter_possibles = [x for x in self._driver.find_elements_by_tag_name('input') if 'update.jpg' in x.get_attribute('src')]
        if len(enter_possibles) > 1:
            raise TooManyUpdateButtons('too many inputs with update.jpg image found')
        enter = enter_possibles[0].click()

    def _has_hours_for_this_date(self):
        element_name = ['ehh', 'xhh']
        return all([self._driver.find_element_by_name(e).get_attribute("value") == '' for e in element_name])

    def _has_excuse_for_this_date(self):
        element_options = Select(self._driver.find_element_by_name('excuse'))
        return not (element_options.first_selected_option.id == element_options.options[0].id)
    
    def _get_date_excuse(self):
        element_options = Select(self._driver.find_element_by_name('excuse'))
        return element_options.first_selected_option.text

    def set_excuse(self, excuse_index):
        """
        set excuse for this date
        will only set if the value is empty or overwrite is turned on

        :param int excuse_index: index (zero based) of the excuse to set

        :return Boolean: True if need hours , false if not
        """

        if self.overwrite or not self._has_excuse_for_this_date():
            
            if self.is_holiday():
                self._clear_all_hours()
                self._set_excuse_value(int(self._holiday_index['vacation_index']))
                logger.info('Set date as vacation')
            elif self.is_holdiay_eve():
                self._clear_all_hours()
                self._set_excuse_value(int(self._holiday_index['eve_index']))
                logger.info('Set date as holiday eve')
            else:
                self._set_excuse_value(excuse_index)
        else:
            logger.debug('Not setting excuse because overwrite is not allowed')


    def _set_excuse_value(self, excuse_index):
        element_options = Select(self._driver.find_element_by_name('excuse'))
        element_options.select_by_index(excuse_index)
        logger.debug('Set excuse %s', element_options.options[excuse_index].text)

    def is_holiday(self):
        return set(self._get_date_text_ascii()) ==  set([int(x) for x in self._holiday_index['vacation_text']])
    
    def is_holdiay_eve(self):
        return set(self._get_date_text_ascii()) ==  set([int(x) for x in self._holiday_index['eve_text']])
    
    def _get_date_text_ascii(self):
        element = self._driver.find_element_by_xpath('/html/body/div/span/form/table/tbody/tr[7]/td/table/tbody/tr/td[2]/font[2]/b')
        return [ord(x) for x in getattr(element, 'text').strip()]

    def _clear_all_hours(self):
        element_list = ['ehh', 'xhh', 'emm', 'xmm']
        row_number = [0, 1, 2, 3]
        for row in row_number:
            for e in element_list:
                # element = self._driver.find_elements_by_xpath('//*[@id="{}{}"]'.format(e, str(row)))
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
                match = re.search(pattern=('(?<=ee\=)\d*(?=\&e)'), string=elems[0])
            except IndexError as e:
                raise IndexError('source of html page has no href with token')
            
            if match:
                self._user_cred['token'] = match[0]
            else:
                raise ValueError('did not extract token from %s', elems[0])

class TooManyUpdateButtons(Exception):
    pass