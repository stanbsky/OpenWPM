
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

accept_button_keywords = [
    re.compile(r'accept'), 
    re.compile(r'agree'), 
    re.compile(r'allow'), 
    re.compile(r'understand'), 
    re.compile(r'continue'), 
    re.compile(r'thank you'), 
    re.compile(r'confirm'), 
    re.compile(r'thanks'), 
    re.compile(r'understood'), 
    re.compile(r'close'), 
    re.compile(r'got it'), 
    re.compile(r'happy'), 
    re.compile(r'fine'), 
    re.compile(r'yes'), 
    re.compile(r'no problem'), 
    re.compile(r'deal'), 
    re.compile(r'okay'), 
    re.compile(r'^ok$')
]



class AcceptCookiesCommand(BaseCommand):
    """This command accept the cookies in a website"""

    def __init__(self, css_selectors) -> None:
        self.logger = logging.getLogger("openwpm")
        self.css_selectors = css_selectors

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "AcceptCookiesCommand"

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
        # Will be used later so that if an Accept Button is found, we can easily target it
        index = 1  
        clickableElements = webdriver.find_elements_by_tag_name('button') + webdriver.find_elements_by_tag_name('a')
        for element in clickableElements: 
            element_id = element.get_attribute('id')
            if element.get_attribute('id') is None or len(element_id) == 0:
                webdriver.execute_script("arguments[0].id = arguments[1];", element, 'custom-id-{}'.format(index)) 
                # element.set_attribute('id', 'custom-id-{}'.format(index))
                index += 1

        found_cookie_selector = self._get_cookie_banner_selectors(webdriver)

        if found_cookie_selector is not None:
            self.logger.info('visit_id {}: accept_cookies: banner_found, website={}, selector={}'.format(self.visit_id, current_url, found_cookie_selector))
            elements = webdriver.find_elements_by_css_selector(found_cookie_selector)
            for element in elements:
                self._find_accept_btn_and_click(element, webdriver)
        else:
            self.logger.info('visit_id {}: accept_cookies: banner_not_found, website={}'.format(self.visit_id, current_url))
        

    def _get_cookie_banner_selectors(self, webdriver: Firefox):
        if self.css_selectors is None or len(self.css_selectors) == 0:
            return None

        found_cookie_selector = None

        for selector in self.css_selectors:

            if 'footer' in selector:
                continue

            try:
                elements = webdriver.find_elements_by_css_selector(selector)
                if len(elements) > 0:
                    cookie_banner_html = ''
                    # Go over the elements, storing their HTML
                    for element in elements:
                        cookie_banner_html += element.get_attribute('innerHTML')

                        if len(cookie_banner_html.strip()) > 0 and 'cookie' in cookie_banner_html:
                            found_cookie_selector = selector
                            break
                if found_cookie_selector is not None:
                    break
            except Exception as e:
                continue
                
        return found_cookie_selector

    def _find_accept_btn_and_click(self, element, webdriver: Firefox):

        try:
            soup = BeautifulSoup(element.get_attribute('innerHTML'), 'html.parser')
            
            buttons = soup.find_all(['button', 'a'])
            found_accept_button = False
            call_to_actions = []

            for button in buttons:
                # 1. Find the accept btn
                # 2. Get the ID
                # 3. Click it!
                try:
                    encoded_call_to_action = str(unicodedata.normalize('NFKD', button.get_text()).encode('ascii', 'ignore').lower(), 'ascii')
                    call_to_actions.append(encoded_call_to_action)
                    for keyword in accept_button_keywords:
                        if self._keyword_matches_cta(keyword, encoded_call_to_action):
                            if button['id'] is not None:
                                button_id = button['id']
                                found_accept_button = True
                                webdriver.find_element_by_id(button_id).click()
                                self.logger.info('visit_id {}: accept_cookies: accept_button_found, website={}, id={}, call_to_action={}'.format(self.visit_id, webdriver.current_url, button_id, encoded_call_to_action))
                                break
                            else:
                                self.logger.warning('visit_id {}: accept_cookies: accept_button_not_found_id, website={}, button={}, call_to_action={}, matched_call_to_action={}'.format(self.visit_id, webdriver.current_url, webdriver.current_url, button, encoded_call_to_action, keyword))

                except Exception as e:
                    self.logger.error('visit_id {}: accept_cookies: accept_button_error, website={}, button={}, error={}'.format(self.visit_id, webdriver.current_url, button, e))
                    continue
                
                if found_accept_button:
                    break
            
            if not found_accept_button:
                if len(call_to_actions) > 10:
                    self.logger.warning('visit_id {}: accept_cookies: accept_button_not_found, website={}'.format(self.visit_id, webdriver.current_url))
                else:
                    self.logger.warning('visit_id {}: accept_cookies: accept_button_not_found, website={}, buttons={}, call_to_actions={}'.format(self.visit_id, webdriver.current_url, buttons, call_to_actions))

        except Exception as e:
            self.logger.error('visit_id {}: accept_cookies: error when parsing cookie banner. website={}, message={}'.format(self.visit_id, webdriver.current_url, e))


    def _keyword_matches_cta(self, keyword, encoded_call_to_action):
        return bool(keyword.search(encoded_call_to_action))
