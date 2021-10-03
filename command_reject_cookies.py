
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
    re.compile(r'reject')
]



class RejectCookiesCommand(BaseCommand):
    """This command rejects the cookies in a website"""

    def __init__(self, cookie_selector) -> None:
        self.logger = logging.getLogger("openwpm")
        self.cookie_selector = cookie_selector

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
        # Will be used later so that if an Accept Button is found, we can easily target it
        index = 1  
        clickableElements = webdriver.find_elements_by_tag_name('button') + webdriver.find_elements_by_tag_name('a')
        for element in clickableElements: 
            element_id = element.get_attribute('id')
            if element.get_attribute('id') is None or len(element_id) == 0:
                webdriver.execute_script("arguments[0].id = arguments[1];", element, 'custom-id-{}'.format(index)) 
                index += 1
