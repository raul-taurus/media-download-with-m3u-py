import os
import subprocess
import sys
import http.client
from urllib.parse import urlparse


def main(url, target):

    u = urlparse(url)

    conn = http.client.HTTPSConnection(u.hostname, u.port)

    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    }

    last_slash = u.path.rfind("/")
    relative_url = f"{u.scheme}://{u.netloc}{u.path[:last_slash]}/"

    conn.request("GET", url, headers=headers)
    response = conn.getresponse()

    if response.status != 200:
        print(response.status)
        return

    m3u = response.read().decode('utf-8')
    m3u_lines = m3u.splitlines()
    media = open(target, "wb")

    part_urls = [x for x in m3u_lines if not x.startswith("#")]
    part_total = len(part_urls)
    part_index = 0

    for line in part_urls:
        part_url = relative_url + line
        conn.request("GET", part_url, headers=headers)
        part = conn.getresponse()
        media.write(part.read())

        part_index += 1
        percent = "{:9.2f}".format(float(part_index)*100/part_total)
        sys.stdout.write(f"{percent}%, ({part_index}/{part_total})\r")
        sys.stdout.flush()

    media.flush()
    media.close()


url = sys.argv[1]

temp_output = "media.mp4"
final_output = "final-media.mp4"
main(url, temp_output)

os.system(f"ffmpeg -i {temp_output} -c copy {final_output}")
