import spotipy
import spotipy.util
from colorama import init, Fore, Back, Style
from spoticli import SpotiCLI

def initialize_env():
	#define scope and user info
	#will eventually remove this from being hardcoded.
	#prompt for info then save locally?
	#prompt for info and keep alive for session?
	#idk yet.
	scope = 'user-library-read user-library-modify user-read-currently-playing user-read-playback-state user-modify-playback-state user-read-recently-played'
	username = '95hlopez@gmail.com'
	client_id = 'ad61a493657140c8a663f8db17730c4f'
	client_secret = '3c403975a6874b238339db2231864294'
	redirect_uri = 'http://127.0.0.1'
	cache = '.spotipyoauthcache'
	
	#spotify_creds_manager = SpotifyClientCredentials(client_id, client_secret)
	#spotify_auth_manager = SpotifyOAuth(client_id,client_secret,redirect_uri,None,scope,cache,None)
	#token_info = spotify_auth_manager.get_cached_token()

	#return spotipy.util.obtain_token_localhost(username,client_id,client_secret,redirect_uri,cache,scope)
	access_token = spotipy.util.obtain_token_localhost(username,client_id,client_secret,redirect_uri,cache,scope)

	#check if generated/saved token is valid before continuing
	#if valid creates spotipy object
	if access_token:
		#sp = spotipy.Spotify(access_token)
		#sp.trace = True
		#sp.trace_out = True
		return access_token


if __name__ == '__main__':
	active = True
	sp = spotipy.Spotify(initialize_env())
	while(active):
		try:
			active = SpotiCLI(sp).cmdloop()
		except:
			sp = spotipy.Spotify(initialize_env())
			print('re-AUTHORIZED')