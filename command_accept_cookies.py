
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

from command_common import * 

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

        add_unique_ids_to_clickable_elements(webdriver)

        found_cookie_selector = self._get_cookie_banner_selectors(webdriver)

        if found_cookie_selector is not None:
            self.logger.info('visit_id {}: accept_cookies: banner_found, website={}, selector={}'.format(self.visit_id, current_url, found_cookie_selector))
            elements = webdriver.find_elements_by_css_selector(found_cookie_selector)
            for element in elements:
                find_btn_and_click(element, webdriver, self.logger, self.visit_id, accept_button_keywords, 'accept_btn')
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

