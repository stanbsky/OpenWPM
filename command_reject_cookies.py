
import logging
from selenium import webdriver

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket

from bs4 import BeautifulSoup
import unicodedata
import re

from command_common import * 

reject_button_keywords = [
    re.compile(r'reject'),
    re.compile(r'decline'),
    re.compile(r'nope'),
    re.compile(r'cancel'),
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

        add_unique_ids_to_clickable_elements(webdriver)

        elements = webdriver.find_elements_by_css_selector(self.cookie_banner_selector)
        for element in elements:
            find_btn_and_click(element, webdriver, self.logger, self.visit_id, reject_button_keywords, 'reject_btn')
