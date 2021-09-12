
import logging
from selenium import webdriver

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket

from lxml import html


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

        page_source = webdriver.page_source.encode('utf8')
        found_cookie_selector = self._find_cookie_banner_website(page_source=page_source)

        if found_cookie_selector is not None:
            self.logger.info('accept_cookies: banner_found, website=%s, selector=%s', current_url, found_cookie_selector)
        else:
            self.logger.info('accept_cookies: banner_not_found, website=%s', current_url)
        

    def _find_cookie_banner_website(self, page_source=''):
        if self.css_selectors is None or len(self.css_selectors) == 0:
            return None

        tree = html.fromstring(page_source)
        found_cookie_selector = None

        for selector in self.css_selectors:
            try:
                tree_css_elements = tree.cssselect(selector)
            except Exception as e:
                self.logger.error('error in css_selector lookup. message={}'.format(e))
                continue

            if len(tree_css_elements) > 0:
                found_cookie_selector = selector
                break
        return found_cookie_selector
