import os, requests

IDCAC_URL = 'https://www.i-dont-care-about-cookies.eu/abp/'

additional_css_selectors = [
'#iubenda-cs-banner',
'#COSLAcookie',
'.brave_popup__step__inner', 
'.cookiemessage__buttons',
'.cookie-consent-prompt',
'.cookieBox',
'.gdprcookie',
'.cookiemessage',
'#wisepops-wisepop-scrollable',
'.p-site-cookie-alert',
'.cookies-notice',
'.ch2-container',
'#ctl00_CookieControl_pnlCookieBar',
'.site-cookie-alert',
'.privacy-alert',
'#cookieStrip',
'#cassie-widget',
'.region-cookie',
'#ds-cookie-consent-banner',
'.cookies-banner',
'.privacy-content',
'.cookie-banner__container',
'.cookie-banner',
'#wg_cookie', 
'#cocc-banner', 
'#CookieConsentForm', 
'#sliding-popup', 
'#cookie-notice',
'#global-cookie-message', 
'#qcCmpUi',
'#qc-cmp2-ui',
'.cookieinfo',
'#CybotCookiebotDialog',
'.cookie-bubble',
'div.cc-window.cc-floating',
'.cc_banner.cc_container',
'#ns-cookie-popup',
'.cookie-pop',
'#cadre_alert_cookies',
'.cookies-widget-container',
'#cookie-law-info-bar',
'#consentPrompt',
'.cb-cookiesbox',
'div.cookies',
'#hw_cookie_law',
'div#accept',
'#ckieconsent',
'#cookies_rep',
'.mpp-box.mpp-popup',
'.prvmodal-wrapper.prvmodal-transition',
'div#cookies',
'.gdpr',
'#sid-container',
'#cookies-agreed-wrapper',
'#popup_cookie_law',
'#cpolicyPanel',
'.gdprModal__placeholder',
'#ccc',
'.gdpr.gdpr-privacy-bar',
'.cc-bar',
'.qc-cmp-ui-content',
'.gdpr_accept_cookie',
'#moove_gdpr_cookie_info_bar',
'.cb-cookiesbox',
'.consent',
'.glcn_accept_cookie',
'.cc-dialog',
'#brands-galaxy-cookie',
'.gdpr-cookies-warning-float-box',
'#_evidon_banner',
'.gdpr-cookie-modal',
'#cookies-accept-container',
'#ck_cookies',
'#cookies_box',
'#cp-inner',
'.pleaseaccept',
'#cookie-main',
'#cookieprefs',
'#cookieDialogue',
'#cookieconsent:desc',
'#cookies-settings-modal',
'.setCookies',
'.nasa-cookie-notice-container',
'#notif--privacy',
'.cookie_popup_bottom',
'#btm_terms',
'#mstm-cookie',
'#ct-ultimate-gdpr-cookie-popup',
'#gdpr-cookie-block',
'#divCookiealert',
'#coi-banner-wrapper',
'#cookiepolicybox',
'.cookies-tooltip',
'#cmp-banner',
'#cookie-consent',
'.eupopup-container'
]

def get_idcac_css_selectors():
    r = requests.get(IDCAC_URL)
    css_selectors = additional_css_selectors

    for line in r.text.split('\n'):
        first_character = line[0]
        banned_characters = {'!', '[', '@', '|', '/'}

        # Ignore the lines starting with !. They are comments
        if first_character in banned_characters:
            continue

        # If the line starts with ~ then this indicates a global rule. e.g.: ~site1.com, site2.com###cookie-notice
        if first_character == '~':
            selector_index = line.find('#')
            if selector_index != -1:
                selector = line[selector_index + 2:]
                css_selectors.append(selector.strip())
            continue

        # If the line starts with ## then this indicates a selector. e.g.: ###cookie-notice
        if line[0:2] == '##':
            selector = line[2:]
            if selector[0] != '#' and selector[0] != '.':
                selector = '#{}'.format(selector)
            css_selectors.append(selector.strip())
            continue

        # If the line starts with a domain name then site specific selectors. e.g.: site.com###cookie-notice-1,...
        selectors = line.split('##')
        if len(selectors) > 1:
            selector = selectors[1]

            if selector.startswith('body >') or selector.startswith('main > footer') or selector.startswith('main + div >'):
                continue
            elif selector == 'overlay':
                continue
            elif selector[0] == '.' or selector[0] == '#':
                css_selectors.append(selector)
            else:
                css_selectors.append('#{}'.format(selector))

    css_selectors.remove('#main-wrapper > header[role="banner"] > div:first-child')
    return list(filter(lambda x: (x[0] == '.' or x[0] == '#') and not (x[0:2] == '#[' or '~' in x or ':' in x), css_selectors))
