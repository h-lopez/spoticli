import socket
import errno
import webbrowser

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qsl
from tekore.auth.refreshing import RefreshingToken, RefreshingCredentials

from tekore import Spotify, util, scope

#cred = util.config_from_file('conf.spoticli')

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_s = urlparse(self.path).query
        form = dict(parse_qsl(query_s))

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        if "code" in form:
            self.server.auth_code = form["code"]
            self.server.error = None
            status = "successful"
        elif "error" in form:
            self.server.error = form["error"]
            self.server.auth_code = None
            status = "failed ({})".format(form["error"])
        else:
            self._write("<html><body><h1>Invalid request</h1></body></html>")
            return

        self._write(
            "<html><body><h1>authentication : {}</h1>you can close this window</body></html>".format(status))

    def _write(self, text):
        return self.wfile.write(text.encode("utf-8"))

    def log_message(self, format, *args):
        return
    
def start_local_http_server(port, handler=RequestHandler):
    while True:
        try:
            server = HTTPServer(("localhost", port), handler)
        except socket.error as err:
            if err.errno != errno.EADDRINUSE:
                raise
        else:
            server.auth_code = None
            return server

def prompt_for_user_token(
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scope=None
) -> RefreshingToken:
    """
    Prompt for manual authentication.
    Open a web browser for the user to log in with Spotify.
    Prompt to paste the URL after logging in to parse the `code` URL parameter.
    Parameters
    ----------
    client_id
        client ID q
    client_secret
        client secret
    redirect_uri
        whitelisted redirect URI
    scope
        access rights as a space-separated list
    Returns
    -------
    RefreshingToken
        automatically refreshing user token
    """
    cred = RefreshingCredentials(client_id, client_secret, redirect_uri)
    url = cred.user_authorisation_url(scope, show_dialog=True)

    print('Opening browser for Spotify login...')
    try:
        webbrowser.open(url)
        #print("Opened %s in your browser" % auth_url)
    except:
        print("Please navigate here: %s" % url)

    url_info = urlparse(redirect_uri)
    netloc = url_info.netloc
    if ":" in netloc:
        port = int(netloc.split(":", 1)[1])
    else:
        port = 80

    server = start_local_http_server(port)
    server.handle_request()
    if server.auth_code:
        #code = parse_code_from_url(redirected)
        return cred.request_user_token(server.auth_code)

    ### redirected = input('Please paste redirect URL: ').strip()
    ### code = parse_code_from_url(redirected)
    ### return cred.request_user_token(code)

    ### overload function by calling own web browser instead of having user copy/pasta. gross.