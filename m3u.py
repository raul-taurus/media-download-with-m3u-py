"""System module."""
import os
import sys
import http.client
from urllib.parse import urlparse


def main(m3u8_url, target):
    """The main function to download media files."""
    uri = urlparse(m3u8_url)

    conn = http.client.HTTPSConnection(uri.hostname, uri.port)

    last_slash = uri.path.rfind("/")
    relative_url = f"{uri.scheme}://{uri.netloc}{uri.path[:last_slash]}/"

    conn.request("GET", m3u8_url)
    response = conn.getresponse()

    if response.status != 200:
        print(response.status)
        return

    m3u = response.read().decode("utf-8")
    m3u_lines = m3u.splitlines()
    media = open(target, "wb")

    part_urls = [x for x in m3u_lines if not x.startswith("#")]
    part_total = len(part_urls)
    part_index = 0

    for line in part_urls:
        part_url = relative_url + line
        conn.request("GET", part_url)
        part = conn.getresponse()
        media.write(part.read())

        part_index += 1
        percent = f"{float(part_index) * 100 / part_total:9.2f}"
        sys.stdout.write(f"{percent}%, ({part_index}/{part_total})\r")
        sys.stdout.flush()

    media.flush()
    media.close()


url = sys.argv[1]

TEMP_OUTPUT = "media.mp4"
FINAL_OUTPUT = "final-media.mp4"
main(url, TEMP_OUTPUT)

os.system(f"ffmpeg -i {TEMP_OUTPUT} -c copy {FINAL_OUTPUT}")
