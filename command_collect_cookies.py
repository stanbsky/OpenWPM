
import logging
import pickle
import os
import time 
import hashlib
import json
from re import U

from selenium.webdriver import Firefox

from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket

from command_common import * 


class CollectCookiesCommand(BaseCommand):
    """This command colelcts the cookies in a website and writes them in a persistent medium"""

    def __init__(self, stage) -> None:
        self.logger = logging.getLogger("openwpm")
        self.stage = stage

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "CollectCookiesCommand"

    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:

        if not os.path.exists('./pickled_cookies'):
            os.makedirs('./pickled_cookies')

        sanitized_url = self._sanitize_url(webdriver.current_url)
        filepath = './pickled_cookies/{}_{}_{}_{}.pkl'.format(self.visit_id, self.stage, sanitized_url, round(time.time()))
        self.logger.info('visit_id {}: collect_cookies: pickling_cookies, stage={}, path={}'.format(self.visit_id, self.stage, filepath))
        cookies = []

        for cookie in webdriver.get_cookies():
            cookies.append({
                'cookie': cookie,
                'cookie_hash': self._cookie_hash(cookie),
                'access_date': round(time.time())
            })

        pickle.dump(cookies, open(filepath, 'wb'))

    def _sanitize_url(self, url: str):
        sanitized = url.replace('http://', '')
        sanitized = sanitized.replace('https://', '')
        sanitized = sanitized.replace('/', '')
        sanitized = sanitized.replace('.', '_')
        return sanitized

    def _cookie_hash(self, cookie):
        hash_fn = hashlib.sha512()
        encoded = json.dumps(cookie, sort_keys=True).encode()
        hash_fn.update(encoded)
        return hash_fn.hexdigest()