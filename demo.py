from pathlib import Path
from command_collect_cookies import CollectCookiesCommand

from custom_command import LinkCountingCommand
from command_accept_cookies import AcceptCookiesCommand
from command_reject_cookies import RejectCookiesCommand
from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager

from idcac_cookie_selectors import get_idcac_css_selectors

# The list of sites that we wish to crawl
NUM_BROWSERS = 1
sites = ['https://www.audit-scotland.gov.uk']

# f = open("sites.txt", "r")
# sites = f.read().split('\n')

# Loads the default ManagerParams
# and NUM_BROWSERS copies of the default BrowserParams

manager_params = ManagerParams(num_browsers=NUM_BROWSERS)
browser_params = [BrowserParams(display_mode="headless") for _ in range(NUM_BROWSERS)]

# Update browser configuration (use this for per-browser settings)
for browser_param in browser_params:
    # Record HTTP Requests and Ressponses
    browser_param.http_instrument = True
    # Record cookie changes
    browser_param.cookie_instrument = True
    # Record Navigations
    browser_param.navigation_instrument = True
    # Record JS Web API calls
    browser_param.js_instrument = True
    # Record the callstack of all WebRequests made
    browser_param.callstack_instrument = True
    # Record DNS resolution
    browser_param.dns_instrument = True

# Update TaskManager configuration (use this for crawl-wide settings)
manager_params.data_directory = Path("./datadir/")
manager_params.log_path = Path("./datadir/openwpm.log")

# memory_watchdog and process_watchdog are useful for large scale cloud crawls.
# Please refer to docs/Configuration.md#platform-configuration-options for more information
# manager_params.memory_watchdog = True
# manager_params.process_watchdog = True


# Commands time out by default after 60 seconds
with TaskManager(
    manager_params,
    browser_params,
    SQLiteStorageProvider(Path("./datadir/crawl-data-pre.sqlite")),
    None,
) as manager:

    # Visits the sites
    for index, site in enumerate(sites):

        def callback(success: bool, val: str = site) -> None:
            print(
                f"CommandSequence for {val} ran {'successfully' if success else 'unsuccessfully'}"
            )

        # Parallelize sites over all number of browsers set above.
        command_sequence = CommandSequence(
            site,
            site_rank=index,
            callback=callback,
        )

        # Start by visiting the page
        command_sequence.append_command(GetCommand(url=site, sleep=6), timeout=60)

        command_sequence.append_command(CollectCookiesCommand(stage='pre-accept'))

        # Run commands across all browsers (simple parallelization)
        manager.execute_command_sequence(command_sequence)

# Commands time out by default after 60 seconds
with TaskManager(
    manager_params,
    browser_params,
    SQLiteStorageProvider(Path("./datadir/crawl-data-post.sqlite")),
    None,
) as manager:

    css_selectors = get_idcac_css_selectors()

    # Visits the sites
    for index, site in enumerate(sites):

        def callback(success: bool, val: str = site) -> None:
            print(
                f"CommandSequence for {val} ran {'successfully' if success else 'unsuccessfully'}"
            )

        # Parallelize sites over all number of browsers set above.
        command_sequence = CommandSequence(
            site,
            site_rank=index,
            callback=callback,
        )

        # Start by visiting the page
        command_sequence.append_command(GetCommand(url=site, sleep=6), timeout=60)

        command_sequence.append_command(AcceptCookiesCommand(css_selectors=css_selectors), timeout=60)

        command_sequence.append_command(CollectCookiesCommand(stage='post-accept'))

        # Run commands across all browsers (simple parallelization)
        manager.execute_command_sequence(command_sequence)
