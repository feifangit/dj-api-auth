var http = require('http'),
  crypto = require('crypto'),
  querystring = require('querystring');

var API_KEY = "483a570a",
  SEC_KEY = "d7228d70cd7f456d9bfdc35ed8fee375",
  host = "localhost",
  port = 8000;


function APIClient(API_KEY, SEC_KEY, host, port) {
  this._ak = API_KEY;
  this._sk = SEC_KEY;
  this._host = host;
  this._port = port;
}

APIClient.prototype.send_request = function (url, data, callback) {
  var opts = {
    hostname: this._host,
    port: this._port,
    path: this.sign_url(url),
    method: 'GET'
  };
  var req = http.request(opts, function (res) {
    res.on('data', function (chunk) {
      console.log('URL:' + url + ' BODY: ' + chunk);
      typeof callback === 'function' && callback(chunk);
    });
  });

  req.on('error', function (e) {
    console.log('problem with request: ' + e.message);
  });

  req.write(querystring.stringify(data));
  req.end();
};

APIClient.prototype.sign_msg = function (_msg) {
  return crypto.createHmac('sha256', this._sk).update(_msg).digest('base64');
};

APIClient.prototype.sign_url = function (_url) {
  var url = (_url.indexOf('/') === 0 ? _url : '/' + _url);
  url += '?';
  url += ('timestamp=' + new Date().getTime() / 1000);
  url += ('&apikey=' + this._ak);
  url += ('&signature=' + this.sign_msg(url));
  return url;
};


apiclient = new APIClient(API_KEY, SEC_KEY, host, port);

console.log("send to /api/hello/");
apiclient.send_request("/api/hello/");

console.log("send to /api/goodbye/");
apiclient.send_request("/api/goodbye/");


console.log("send to /api/classbased1/");
apiclient.send_request("/api/classbased1/");