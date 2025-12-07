import re
import socket
import whois
import datetime
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# ------------------- Basic URL Features -------------------
def having_ip_address(url):
    """1 if URL contains IP address, else -1"""
    try:
        return 1 if re.search(r'[0-9]{1,3}(\.[0-9]{1,3}){3}', url) else -1
    except:
        return 0

def url_length(url):
    """-1 if short, 0 if medium, 1 if long"""
    if len(url) < 54:
        return -1
    elif len(url) <= 75:
        return 0
    else:
        return 1

def shortening_service(url):
    """1 if URL uses shortening service, else -1"""
    if re.search(r"(bit\.ly|goo\.gl|tinyurl\.com|ow\.ly|t\.co|tinyurl)", url):
        return 1
    return -1

def having_at_symbol(url):
    """1 if '@' present, else -1"""
    return 1 if '@' in url else -1

def double_slash_redirecting(url):
    """1 if '//' in path (not protocol), else -1"""
    parts = urlparse(url)
    if '//' in parts.path[1:]:
        return 1
    return -1

def prefix_suffix(url):
    """1 if '-' in domain, else -1"""
    domain = urlparse(url).netloc
    return 1 if '-' in domain else -1

def having_sub_domain(url):
    """-1 if no subdomain, 0 if 1, 1 if >1"""
    domain = urlparse(url).netloc
    parts = domain.split('.')
    if len(parts) <= 2:
        return -1
    elif len(parts) == 3:
        return 0
    else:
        return 1

def ssl_final_state(url):
    """-1 if HTTPS with valid certificate, 1 if HTTP, 0 if HTTPS invalid"""
    try:
        if url.startswith("https://"):
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                return -1
            else:
                return 0
        else:
            return 1
    except:
        return 0

def domain_registration_length(url):
    """-1 if domain age >1 year, 1 if <1 year"""
    try:
        domain_info = whois.whois(urlparse(url).netloc)
        if isinstance(domain_info.creation_date, list):
            creation_date = domain_info.creation_date[0]
        else:
            creation_date = domain_info.creation_date
        age = (datetime.datetime.now() - creation_date).days
        return -1 if age >= 365 else 1
    except:
        return 1

def favicon(url):
    """-1 if favicon domain matches URL, 1 if different"""
    try:
        r = requests.get(url, timeout=3)
        soup = BeautifulSoup(r.content, 'html.parser')
        icon = soup.find("link", rel="shortcut icon")
        if icon and urlparse(icon.get("href")).netloc != urlparse(url).netloc:
            return 1
        return -1
    except:
        return -1

def port(url):
    """-1 if standard port, 1 if unusual port"""
    domain = urlparse(url).netloc
    if ':' in domain:
        p = int(domain.split(':')[1])
        return -1 if p in [80, 443] else 1
    return -1

def https_token(url):
    """1 if 'https' in domain name, else -1"""
    domain = urlparse(url).netloc
    return 1 if 'https' in domain else -1

# ------------------- URL content / HTML features -------------------
def request_url(url):
    """1 if many requests go to external domain, else -1"""
    try:
        r = requests.get(url, timeout=3)
        soup = BeautifulSoup(r.content, 'html.parser')
        imgs = soup.find_all('img', src=True)
        total = len(imgs)
        external = sum(1 for i in imgs if urlparse(i['src']).netloc != urlparse(url).netloc)
        if total == 0:
            return -1
        ratio = external / total
        if ratio < 0.22:
            return -1
        elif ratio <= 0.61:
            return 0
        else:
            return 1
    except:
        return 0

def url_of_anchor(url):
    """1 if many anchor links go to external domains, else -1"""
    try:
        r = requests.get(url, timeout=3)
        soup = BeautifulSoup(r.content, 'html.parser')
        anchors = soup.find_all('a', href=True)
        total = len(anchors)
        external = sum(1 for a in anchors if urlparse(a['href']).netloc != urlparse(url).netloc)
        if total == 0:
            return -1
        ratio = external / total
        if ratio < 0.31:
            return -1
        elif ratio <= 0.67:
            return 0
        else:
            return 1
    except:
        return 0

def links_in_tags(url):
    """Dummy placeholder"""
    return -1

def sfh(url):
    """Dummy placeholder for server form handler"""
    return -1

def submitting_to_email(url):
    """1 if mailto in form, else -1"""
    try:
        r = requests.get(url, timeout=3)
        soup = BeautifulSoup(r.content, 'html.parser')
        forms = soup.find_all('form', action=True)
        for form in forms:
            if "mailto:" in form['action']:
                return 1
        return -1
    except:
        return -1

def abnormal_url(url):
    """Check if domain in URL matches WHOIS"""
    try:
        domain = urlparse(url).netloc
        domain_info = whois.whois(domain)
        if domain_info.domain_name and domain in domain_info.domain_name:
            return -1
        else:
            return 1
    except:
        return 1

def redirect(url):
    """1 if meta refresh or javascript redirect"""
    try:
        r = requests.get(url, timeout=3)
        if "refresh" in r.text.lower() or "window.location" in r.text.lower():
            return 1
        return -1
    except:
        return 0

def on_mouseover(url):
    """1 if onmouseover javascript exists, else -1"""
    try:
        r = requests.get(url, timeout=3)
        return 1 if "onmouseover" in r.text.lower() else -1
    except:
        return -1

def right_click(url):
    """1 if right click disabled"""
    try:
        r = requests.get(url, timeout=3)
        return 1 if "event.button==2" in r.text.lower() else -1
    except:
        return -1

def pop_up_window(url):
    """1 if popup window detected"""
    try:
        r = requests.get(url, timeout=3)
        return 1 if "window.open" in r.text.lower() else -1
    except:
        return -1

def iframe(url):
    """1 if iframe exists"""
    try:
        r = requests.get(url, timeout=3)
        soup = BeautifulSoup(r.content, 'html.parser')
        return 1 if soup.find_all('iframe') else -1
    except:
        return -1

def age_of_domain(url):
    """Domain age in days"""
    try:
        domain_info = whois.whois(urlparse(url).netloc)
        if isinstance(domain_info.creation_date, list):
            creation_date = domain_info.creation_date[0]
        else:
            creation_date = domain_info.creation_date
        age = (datetime.datetime.now() - creation_date).days
        if age < 180:
            return 1
        else:
            return -1
    except:
        return 1

def dns_record(url):
    """1 if DNS exists, else -1"""
    try:
        socket.gethostbyname(urlparse(url).netloc)
        return -1
    except:
        return 1

def web_traffic(url):
    """Placeholder"""
    return -1

def page_rank(url):
    """Placeholder"""
    return -1

def google_index(url):
    """1 if indexed in Google, -1 otherwise (placeholder)"""
    return -1

def links_pointing_to_page(url):
    """Placeholder"""
    return -1

def statistical_report(url):
    """Placeholder"""
    return -1

# ------------------- Master function -------------------
def extract_features(url):
    return {
        'having_IP_Address': having_ip_address(url),
        'URL_Length': url_length(url),
        'Shortining_Service': shortening_service(url),
        'having_At_Symbol': having_at_symbol(url),
        'double_slash_redirecting': double_slash_redirecting(url),
        'Prefix_Suffix': prefix_suffix(url),
        'having_Sub_Domain': having_sub_domain(url),
        'SSLfinal_State': ssl_final_state(url),
        'Domain_registeration_length': domain_registration_length(url),
        'Favicon': favicon(url),
        'port': port(url),
        'HTTPS_token': https_token(url),
        'Request_URL': request_url(url),
        'URL_of_Anchor': url_of_anchor(url),
        'Links_in_tags': links_in_tags(url),
        'SFH': sfh(url),
        'Submitting_to_email': submitting_to_email(url),
        'Abnormal_URL': abnormal_url(url),
        'Redirect': redirect(url),
        'on_mouseover': on_mouseover(url),
        'RightClick': right_click(url),
        'popUpWidnow': pop_up_window(url),
        'Iframe': iframe(url),
        'age_of_domain': age_of_domain(url),
        'DNSRecord': dns_record(url),
        'web_traffic': web_traffic(url),
        'Page_Rank': page_rank(url),
        'Google_Index': google_index(url),
        'Links_pointing_to_page': links_pointing_to_page(url),
        'Statistical_report': statistical_report(url)
    }
