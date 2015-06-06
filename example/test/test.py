import urllib
import urllib2
import json
import urlparse
import time
import traceback
import logging


import hmac
import hashlib
import base64
from urllib2 import HTTPError

API_KEY = "483a570a"
SEC_KEY = "d7228d70cd7f456d9bfdc35ed8fee375"
URL = "http://localhost:8000"

logging.basicConfig()
logger = logging.getLogger("API_CLIENT")
logger.setLevel(logging.DEBUG)

class APIException(Exception):
    def __init__(self, reason, code, *args, **kwargs):
        super(APIException, self).__init__(reason, code, *args, **kwargs)
        self.code = code
        self.message = reason



class APIClient(object):
    def __init__(self, apikey, seckey, url):
        self.opener = urllib2.build_opener()
        self._baseurl = url
        self._ak = str(apikey)
        self._sk = str(seckey)

    def _sign_msg(self, msg):
        dig = hmac.new(self._sk, msg, digestmod=hashlib.sha256).digest()
        return base64.b64encode(dig).decode()

    def _sign_url(self, _url, data):
        url = ("/" + _url) if not _url.startswith("/") else _url
        url_parts = urlparse.urlparse(url)
        qs = urlparse.parse_qs(url_parts.query)
        qs["timestamp"] = time.time()  # UNIX time
        qs["apikey"] = self._ak
        new_qs = urllib.urlencode(qs, True)
        tmpurl = urlparse.urlunparse(list(url_parts[0:4]) + [new_qs] + list(url_parts[5:]))
        final_url = tmpurl + "&signature=" + self._sign_msg(tmpurl+data if data else tmpurl)  # sign url
        return final_url

    def send_request(self, url, data=None, datafunc=json.loads):
        try:
            resp = self.opener.open(urlparse.urljoin(self._baseurl, self._sign_url(url, data)), data)
            return resp.code, datafunc(resp.read()) if datafunc else resp.read()
        except HTTPError as e:
            # logger.debug(e.fp.read() if e.fp else e.msg)
            raise APIException(e.code, e.fp.read() if (e.fp and e.code==403) else e.msg)


apiclient = APIClient(API_KEY, SEC_KEY, URL)



print "\n1 send GET to /api/hello/"
httpcode, httpresp = apiclient.send_request("/api/hello/", datafunc=None)
print httpresp


print "\n2.1 send GET to /api/goodbye/"
httpcode, httpresp = apiclient.send_request("/api/goodbye/")
print httpresp

print "\n2.2 send POST to /api/goodbye/"
httpcode, httpresp = apiclient.send_request("/api/goodbye/", data="world")
print httpresp

print "\n3.1 send GET to /api/classbased1/"
httpcode, httpresp = apiclient.send_request("/api/classbased1/")
print httpresp

print "\n3.2 send GET to /api/classbased1/"
httpcode, httpresp = apiclient.send_request("/api/classbased1/", data="world")
print httpresp


print "\n4 send to /api/classbased2/ without auth"
print urllib.urlopen(URL+"/api/classbased2/").read()




