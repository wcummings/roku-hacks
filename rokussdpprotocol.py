import time
import random
import socket
from http.client import HTTPResponse
from fakesocket import FakeSocket
import requests
from bs4 import BeautifulSoup
import inquirer
import urllib.parse


SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900
SSDP_ST = "roku:ecp"

SSDP_DISCOVER_REQUEST = "M-SEARCH * HTTP/1.1\r\n" + \
                        "Host: %s:%d\r\n" % (SSDP_ADDR, SSDP_PORT) + \
                        "Man: \"ssdp:discover\"\r\n" + \
                        "ST: %s\r\n" % (SSDP_ST,) + "\r\n" + \
                        "\r\n"

DEVICE_INFO_ENDPOINT = "query/device-info"
SEARCH_ENDPOINT = "search/browse"
KEYPRESS_ENDPOINT = "keypress/"

DOWN_KEY = "Down"
ENTER_KEY = "Select"
LEFT_KEY = "Left"


class RokuSSDPProtocol:


    def __init__(self):
        self._devices = {}


    def get_devices(self):
        return self._devices


    def search_for_devices_n_times(self, n):
        for i in range(n):
            self.search_for_devices()


    def search_devices_until_one_found(self):
        while self._devices == {}:
            self.search_for_devices()


    def search_for_devices(self, timeout=3):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(SSDP_DISCOVER_REQUEST.encode('ASCII'), (SSDP_ADDR, SSDP_PORT))
        sock.settimeout(timeout)
        try:
            while True:
                # (b'HTTP/1.1 200 OK\r\nCache-Control: max-age=3600\r\nST: roku:ecp\r\nUSN: uuid:roku:ecp:X00400PWJ59L\r\nExt: \r\nServer: Roku/11.5.0 UPnP/1.0 Roku/11.5.0\r\nLOCATION: http://192.168.68.103:8060/\r\ndevice-group.roku.com: 85A8EF4EB241C10A60F3\r\n\r\n', ('192.168.68.103', 1900))
                (resp_bytes, address) = sock.recvfrom(1000)
                http_resp = HTTPResponse(FakeSocket(resp_bytes))
                http_resp.begin()
                loc = self._parse_msearch_response(resp_bytes)
                device_info = self._query_device_info(loc)
                device_name = device_info.find("user-device-name").text
                print("Device found: {} @ {}".format(device_name, loc))
                self._devices[device_name] = (loc, device_info)
        except TimeoutError:
            sock.close()


    def launch(self, device_name, keyword, app):
        (url, _) = self._devices[device_name]
        return self._query_search(url, keyword, app)

    def keypress(self, device_name, key):
        (url, _) = self._devices[device_name]
        return self._query_keypress(url, key)


    def _query_device_info(self, base_url):
        resp = requests.get(base_url + DEVICE_INFO_ENDPOINT)
        if resp.status_code != 200:
            raise Exception("Error querying device info endpoint, status code was {}".format(resp.status_code))
        return BeautifulSoup(resp.text, 'lxml')


    def _parse_msearch_response(self, resp_bytes):
        http_resp = HTTPResponse(FakeSocket(resp_bytes))
        http_resp.begin()
        for header in http_resp.getheaders():
            if header[0] == "LOCATION":
                return header[1]


    def _query_search(self, base_url, keyword, app):
        resp = requests.post(base_url + SEARCH_ENDPOINT + "?type=tv-show&keyword=" + keyword + "&launch=true&match-any=true&season=1&provider=" + app)
        if resp.status_code != 200:
            raise Exception("Error querying search endpoint, status code was {}".format(resp.status_code))
        return BeautifulSoup(resp.text, 'lxml')


    def _query_keypress(self, base_url, key):
        resp = requests.post(base_url + KEYPRESS_ENDPOINT + key)
        if resp.status_code != 200:
            raise Exception("Error querying keypress endpoint, status code was {}".format(resp.status_code))
        return BeautifulSoup(resp.text, 'lxml')


SHOWS = [
    ("king of the hill", "hulu"),
    ("seinfeld", "netflix"),
    ("community", "hulu")
]


if __name__ == '__main__':
    protocol = RokuSSDPProtocol()
    protocol.search_for_devices_n_times(1)
    protocol.search_devices_until_one_found()
    device_map = protocol.get_devices()
    questions = [
        inquirer.List('device',
            message="Select a device",
            choices=device_map.keys())
        ]
    answers = inquirer.prompt(questions)
    selected_device_name = answers['device']
    (show_name, app) = random.choice(SHOWS)
    print("Chose {}".format(show_name))
    print("Launching...")
    protocol.launch(selected_device_name, show_name, app)
    time.sleep(30)
    print("A C T I V A T I N G")
    protocol.keypress(selected_device_name, LEFT_KEY)
    time.sleep(.5)
    for n in range(random.randint(1, 13)):
        protocol.keypress(selected_device_name, DOWN_KEY)
        time.sleep(.5)
    protocol.keypress(selected_device_name, ENTER_KEY)
    for n in range(random.randint(1, 13)):
        protocol.keypress(selected_device_name, DOWN_KEY)
        time.sleep(.5)
    protocol.keypress(selected_device_name, ENTER_KEY)
