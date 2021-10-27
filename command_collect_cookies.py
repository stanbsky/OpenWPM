
import logging
import pickle
import os
import time 
import hashlib
import json

from selenium.webdriver import Firefox

from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket

from command_common import * 


class CollectCookiesCommand(BaseCommand):
    """This command colelcts the cookies in a website and writes them in a persistent medium"""

    def __init__(self, stage, output_path = './datadir/pickled-cookies') -> None:
        self.logger = logging.getLogger("openwpm")
        self.stage = stage
        self.output_path = output_path

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

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        sanitized_url = self._sanitize_url(webdriver.current_url)
        filepath = '{}/{}_{}_{}_{}.pkl'.format(self.output_path, self.visit_id, self.stage, sanitized_url, round(time.time()))
        self.logger.info('visit_id {}: collect_cookies: pickling_cookies, stage={}, path={}'.format(self.visit_id, self.stage, filepath))
        cookies = []

        for cookie in webdriver.get_cookies():
            cookies.append({
                'openwpm_cookie': cookie,
                'cookie_hash': self._cookie_hash(cookie),
                'access_date': round(time.time()),
                'stage': self.stage,
                'original_url': webdriver.current_url,
                'visit_id': self.visit_id
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