
import logging
from selenium import webdriver

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket

from lxml import html
from bs4 import BeautifulSoup


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
        clickableElements = webdriver.find_elements_by_tag_name('button') + webdriver.find_elements_by_tag_name('button')
        for element in clickableElements: 
            element_id = element.get_attribute('id')
            if element.get_attribute('id') is None or len(element_id) == 0:
                webdriver.execute_script("arguments[0].id = arguments[1];", element, 'custom-id-{}'.format(index)) 
                # element.set_attribute('id', 'custom-id-{}'.format(index))
                index += 1

        page_source = webdriver.page_source.encode('utf8')
        found_cookie_selector = self._get_cookie_banner_selectors(page_source=page_source)

        if found_cookie_selector is not None:
            self.logger.info('accept_cookies: banner_found, website={}, selector={}'.format(current_url, found_cookie_selector))
            elements = webdriver.find_elements_by_css_selector(found_cookie_selector)
            for element in elements:
                self._find_accept_btn_and_click(element)

        else:
            self.logger.info('accept_cookies: banner_not_found, website=%s', current_url)
        

    def _get_cookie_banner_selectors(self, page_source=''):
        if self.css_selectors is None or len(self.css_selectors) == 0:
            return None

        found_cookie_selector = None
        tree = html.fromstring(page_source)

        for selector in self.css_selectors:
            try:
                tree_css_elements = tree.cssselect(selector)
            except Exception as e:
                self.logger.error('accept_cookies: error in css_selector lookup. message={}, selector={}'.format(e, selector))
                continue

            if len(tree_css_elements) > 0:
                found_cookie_selector = selector
                break
                
        return found_cookie_selector

    def _find_accept_btn_and_click(self, element):

        try:
            soup = BeautifulSoup(element.get_attribute('innerHTML'), 'html.parser')
            buttons = soup.find_all(['button', 'a'])
            
            for button in buttons:
                #TODO: 
                # 1. Find the accept btn
                # 2. Get the ID
                # 3. Click it!
                self.logger.info('accept_cookies: clickable_item={}, str={}'.format(button, button.get_text()))
        except Exception as e:
            self.logger.error('accept_cookies: error in when parsing cookie banner. message={}'.format(e))

