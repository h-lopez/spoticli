import os

import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import spotipy.util 
from spotipy.scope import every
from urllib.parse import urlparse, parse_qs
from spotipy.auth import AccessToken, Token, Credentials

#create requests

### need to overload default behaviour of user token prompting
### instead of opening browser, we'll authenticate using requests to create auth/receive redirect url with the auth code.
def prompt_for_user_token(
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scope=None):
    """
    Open a web browser for manual authentication.
    Parameters
    ----------
    client_id
        client ID of a Spotify App
    client_secret
        client secret
    redirect_uri
        whitelisted redirect URI
    scope
        access rights as a space-separated list
    Returns
    -------
    RefreshingToken
        automatically refreshing access token
    """
    cred = Credentials(client_id, client_secret, redirect_uri)
    url = cred.user_authorisation_url(scope)
    print(url)
    #print('Opening browser for Spotify login...')
    #webbrowser.open(url)
    
    #print(s.get(url, allow_redirects=True).url)
    #print(s.get(url).text)
    #redirected = input('Please paste redirect URL: ').strip()
    #code = parse_code_from_url(redirected)
    #token = cred.request_user_token(code, scope)
    #return RefreshingToken(token, cred)

client_id = 'ad61a493657140c8a663f8db17730c4f'
client_secret = '3c403975a6874b238339db2231864294'
redirect_uri = 'http://localhost'

token = prompt_for_user_token(
    client_id,
    client_secret,
    redirect_uri,
    scope=every
)

def assert_port_available(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("", port))
    except socket.error:
        raise spotipy.SpotifyException(200, -1, "Port {} is not available. If you are currently running a server, "
                                                "please halt it for a min.".format(port))
    finally:
        s.close()


def get_authentication_code():
    httpd = MicroServer((REDIRECT_URI.replace("http:", "").replace("https:", "").replace("/", ""), 80), CustomHandler)
    while not httpd.latest_query_components:
        httpd.handle_request()
    httpd.server_close()
    if "error" in httpd.latest_query_components:
        if httpd.latest_query_components["error"][0] == "access_denied":
            raise spotipy.SpotifyException(200, -1, 'The user rejected Spotify access')
        else:
            raise spotipy.SpotifyException(200, -1, 'Unknown error from Spotify authentication server: {}'.format(
                httpd.latest_query_components["error"][0]))
    if "code" in httpd.latest_query_components:
        code = httpd.latest_query_components["code"][0]
    else:
        raise spotipy.SpotifyException(200, -1, 'Unknown response from Spotify authentication server: {}'.format(
            httpd.latest_query_components))
    return code


class CustomHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.server.latest_query_components = parse_qs(urlparse(self.path).query)
        self.wfile.write(b"<html><body><p>You can close this tab</p></body></html>")


class MicroServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        self.latest_query_components = None
        super().__init__(server_address, RequestHandlerClass)
