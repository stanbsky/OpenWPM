from bs4 import BeautifulSoup
import unicodedata
import re

def add_unique_ids_to_clickable_elements(webdriver):
    # Pre-process the buttons and links
    # If one of them doesn't have and ID, assign it one
    # Will be used later so that if an Reject Button is found, we can easily target it

    index = 1  
    clickableElements = webdriver.find_elements_by_tag_name('button') + webdriver.find_elements_by_tag_name('a')
    for element in clickableElements: 
        element_id = element.get_attribute('id')
        if element.get_attribute('id') is None or len(element_id) == 0:
            webdriver.execute_script("arguments[0].id = arguments[1];", element, 'custom-id-{}'.format(index)) 
            index += 1


def find_btn_and_click(element, webdriver, logger, visit_id, keywords, caller):

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
                for keyword in keywords:
                    if _keyword_matches_cta(keyword, encoded_call_to_action):
                        if button['id'] is not None:
                            button_id = button['id']
                            found_accept_button = True
                            webdriver.find_element_by_id(button_id).click()
                            logger.info('visit_id {}: {}: button_found, website={}, id={}, call_to_action={}'.format(visit_id, caller, webdriver.current_url, button_id, encoded_call_to_action))
                            break
                        else:
                            logger.warning('visit_id {}: {}: button_not_found_id, website={}, button={}, call_to_action={}, matched_call_to_action={}'.format(visit_id, caller, webdriver.current_url, webdriver.current_url, button, encoded_call_to_action, keyword))

            except Exception as e:
                logger.error('visit_id {}: {}: button_error, website={}, button={}, error={}'.format(visit_id, caller, webdriver.current_url, button, e))
                continue
            
            if found_accept_button:
                break
        
        if not found_accept_button:
            if len(call_to_actions) > 10:
                logger.warning('visit_id {}: {}: accept_button_not_found, website={}'.format(visit_id, caller,webdriver.current_url))
            else:
                logger.warning('visit_id {}: {}: accept_button_not_found, website={}, buttons={}, call_to_actions={}'.format(visit_id, caller, webdriver.current_url, buttons, call_to_actions))

    except Exception as e:
        logger.error('visit_id {}: {}: error when parsing cookie banner. website={}, message={}'.format(visit_id, caller, webdriver.current_url, e))


def _keyword_matches_cta(keyword, encoded_call_to_action):
    return bool(keyword.search(encoded_call_to_action))