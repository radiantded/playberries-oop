import json
import os

from colorama import Fore
from dotenv import load_dotenv
from sys import platform


load_dotenv()

PROXY_SITE = os.environ.get('PROXY_SITE')
PROXY_LOGIN = os.environ.get('PROXY_LOGIN')
PROXY_PASS = os.environ.get('PROXY_PASS')
WEBSITE = 'https://www.wildberries.ru'

AUTH_USERS = json.loads(os.environ.get('AUTH_USERS'))
PAGE_LIMIT = 21
OPTIONS_RETRIES = 11
ERROR_LIMIT = 150
WAIT_AFTER_FINISH = 15
WAIT_AFTER_CART = 3

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 OPR/70.0.3728.95',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 Edg/86.0.622.51',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/80.0.3987.95 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 9; HUAWEI OS) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Mobile Safari/537.36'
]

BROWSER_ARGS = [
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--window-size=1920,1080"
]

CONSOLE_COLORS = [
    Fore.RED, Fore.GREEN, Fore.BLUE, 
    Fore.YELLOW, Fore.WHITE, Fore.MAGENTA, Fore.CYAN
]

if platform == 'linux' or platform == "linux2":
    BOT_TOKEN = os.environ.get('TOKEN')
    HEADLESS = True
    LINUX = True
else:
    BOT_TOKEN = os.environ.get('TEST_TOKEN')
    HEADLESS = False
    LINUX = False