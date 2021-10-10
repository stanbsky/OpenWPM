
import logging
from selenium import webdriver

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket

#from lxml import html
from bs4 import BeautifulSoup
import unicodedata
import re

reject_button_keywords = [
    re.compile(r'reject'),
    re.compile(r'decline'),
    re.compile(r'nope'),
    re.compile(r'cancel'),
    re.compile(r'no, give me more info'),
    re.compile(r'i do not accept'),
    re.compile(r'i do not agree'),
    re.compile(r'disagree'),
    re.compile(r'no, thanks'),
    re.compile(r'no, find out more'),
    re.compile(r'no, give me more info'),
    re.compile(r'disable cookies'),
    re.compile(r'^no$')
]



class RejectCookiesCommand(BaseCommand):
    """This command rejects the cookies in a website"""

    def __init__(self, cookie_banner_selector) -> None:
        self.logger = logging.getLogger("openwpm")
        self.cookie_banner_selector = cookie_banner_selector

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "RejectCookiesCommand"

    # Have a look at openwpm.commands.types.BaseCommand.execute to see
    # an explanation of each parameter
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:
        current_url = webdriver.current_url

        # Pre-process the buttons and links
        # If one of them doesn't have and ID, assign it one
        # Will be used later so that if an Reject Button is found, we can easily target it
        index = 1  
        clickableElements = webdriver.find_elements_by_tag_name('button') + webdriver.find_elements_by_tag_name('a')
        for element in clickableElements: 
            element_id = element.get_attribute('id')
            if element.get_attribute('id') is None or len(element_id) == 0:
                webdriver.execute_script("arguments[0].id = arguments[1];", element, 'custom-id-{}'.format(index)) 
                index += 1

        elements = webdriver.find_elements_by_css_selector(self.cookie_banner_selector)
        for element in elements:
            self._find_reject_btn_and_click(element, webdriver)

    def _find_reject_btn_and_click(self, element, webdriver):

        try:
            soup = BeautifulSoup(element.get_attribute('innerHTML'), 'html.parser')
            
            buttons = soup.find_all(['button', 'a'])
            found_reject_button = False
            call_to_actions = []

            for button in buttons:
                try:
                    encoded_call_to_action = str(unicodedata.normalize('NFKD', button.get_text()).encode('ascii', 'ignore').lower(), 'ascii')
                    call_to_actions.append(encoded_call_to_action)
                    for keyword in reject_button_keywords:
                        if self._keyword_matches_cta(keyword, encoded_call_to_action):
                            if button['id'] is not None:
                                button_id = button['id']
                                found_reject_button = True
                                webdriver.find_element_by_id(button_id).click()
                                self.logger.info('visit_id {}: reject_cookies: reject_button_found, website={}, id={}, call_to_action={}'.format(self.visit_id, webdriver.current_url, button_id, encoded_call_to_action))
                                break
                            else:
                                self.logger.warning('visit_id {}: reject_cookies: reject_button_not_found_id, website={}, button={}, call_to_action={}, matched_call_to_action={}'.format(self.visit_id, webdriver.current_url, webdriver.current_url, button, encoded_call_to_action, keyword))

                except Exception as e:
                    self.logger.error('visit_id {}: reject_cookies: reject_button_error, website={}, button={}, error={}'.format(self.visit_id, webdriver.current_url, button, e))
                    continue

                if found_reject_button:
                    break

            if not found_reject_button:
                if len(call_to_actions) > 10:
                    self.logger.warning('visit_id {}: reject_cookies: reject_button_not_found, website={}'.format(self.visit_id, webdriver.current_url))
                else:
                    self.logger.warning('visit_id {}: reject_cookies: reject_button_not_found, website={}, buttons={}, call_to_actions={}'.format(self.visit_id, webdriver.current_url, buttons, call_to_actions))



        except Exception as e:
            self.logger.error('visit_id {}: reject_cookies: error when parsing cookie banner. website={}, message={}'.format(self.visit_id, webdriver.current_url, e))


    def _keyword_matches_cta(self, keyword, encoded_call_to_action):
        return bool(keyword.search(encoded_call_to_action))
