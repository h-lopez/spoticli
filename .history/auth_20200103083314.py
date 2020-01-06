#needed for local web server
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

#import spotipy.util 
from spotipy import Spotify
from spotipy.auth import Credentials
from spotipy.scope import every
from spotipy.sender import PersistentSender
from spotipy.util import RefreshingToken

#import requests lib
import requests
import re

#create requests
client_id = 'ad61a493657140c8a663f8db17730c4f'
client_secret = '3c403975a6874b238339db2231864294'
redirect_uri = 'http://localhost'

### need to overload default behaviour of user token prompting
### instead of opening browser, we'll authenticate using requests to create auth/receive redirect url with the auth code.
def get_user_token(client_id: str, client_secret: str, redirect_uri: str, scope=None) -> RefreshingToken:
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
    auth_url = cred.user_authorisation_url(scope)
    
    #authorize and capture auth token
    try:
        '''
        #attempt to capture token via request library. 
        try:

        #if we fail to capture via request library, fallback to capturing from browser.
        except:
            import webbrowser
            webbrowser.open(auth_url)
            print("Opened %s in your browser" % auth_url)
        '''
        #import webbrowser
        #webbrowser.open(auth_url)
        response = requests.get(auth_url)
        print(response)
        print(response.request.url)
        print(response.request)
        #print("Opened %s in your browser" % auth_url)
    except:
        print("Please navigate here: %s" % auth_url) 
        webbrowser.open(auth_url)

    code = get_authentication_code()
    #print('Opening browser for Spotify login...')
    #webbrowser.open(url)
    
    #code = parse_code_from_url(redirected)
    token = cred.request_user_token(code, scope)
    return RefreshingToken(token, cred)

def get_authentication_code():
    httpd = MicroServer((redirect_uri.replace("http:", "").replace("https:", "").replace("/", ""), 80), CustomHandler)
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
        self.wfile.write(b"<html><body><p style=\"font-family:sans-serif\">You can close this tab</p></body></html>")

class MicroServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        self.latest_query_components = None
        super().__init__(server_address, RequestHandlerClass)

token = get_user_token(
    client_id,
    client_secret,
    redirect_uri,
    scope=every
)

s = Spotify(token=token, sender=PersistentSender())

tracks = s.current_user_top_tracks(limit=10)
for track in tracks.items:
    print(track.name)