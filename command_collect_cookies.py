
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

from pprint import pprint
import os
import shutil
import sqlite3


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

        entry = {
            'visit_id': self.visit_id,
            'browser_id': self.browser_id,
            'stage': self.stage,
            'host': webdriver.current_url,
            'access_date': round(time.time())
        }
        filepath = '{}/{}_{}_{}_{}.pkl'.format(self.output_path, self.visit_id, self.stage, self._sanitize_url(webdriver.current_url), round(time.time()))
        pickle.dump(entry, open(filepath, 'wb'))

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
