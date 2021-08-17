DEBUG = False

SCRIPT_FOLDER = r"/usr/local/anticc/"
SCRIPT_NAME = r"anticc.py"
IPSET_SAVE_NAME = r"save.txt"
WHITE_LIST = r"whitelist.txt"
CRON_FOLDER = r"/etc/cron.d/"
CRON_NAME = r"anticc"
LOG_FOLDER = SCRIPT_FOLDER
LOG_NAME = r"anticc.py.log"

IPTABLES = r"/usr/sbin/iptables"
IPSET = r"/usr/sbin/ipset"
SERVICE = r"/usr/sbin/service"
IPSET_NAME = r"anticc"

MAX_CONNECTION = 40

LOCAL_NAME = r"美国"
EMAIL_HOST = r"smtp.qq.com"
EMAIL_PORT = 465
EMAIL_FROM = r"from@qq.com"
EMAIL_FROM_NAME = r"from"
EMAIL_PASS = r"################"
EMAIL_TO = r"to@qq.com"
EMAIL_TO_NAME = r"to"

CRON_CONTENT = r'''0-59/1 * * * * root /usr/bin/anticc >/dev/null 2>&1
0-59/1 * * * * root sleep 30s; /usr/bin/anticc >/dev/null 2>&1
'''

RECOVERY_CODE = [r"/usr/bin/nginx -s quit", r"/usr/sbin/service php-fpm stop", 0,
                 r"/usr/bin/nginx", r"/usr/sbin/service php-fpm start"]
