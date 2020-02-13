import requests
from json import dumps


def is_it_blocked(ip):
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://www.isitblockedinrussia.com',
        'Sec-Fetch-Dest': 'empty',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
        'Content-Type': 'application/json;charset=UTF-8',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Referer': f'https://www.isitblockedinrussia.com/?host={ip}',
        'Accept-Language': 'en-GB,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,en-US;q=0.6',
    }

    data = dumps({"host": str(ip)})

    response = requests.post('https://www.isitblockedinrussia.com/', headers=headers, data=data).json()
    if len(response["ips"][0]["blocked"]) > 0:
        return True
    else:
        return False
