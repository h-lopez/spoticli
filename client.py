import spotipy
import spotipy.util
import datetime

from spoticli import SpotiCLI
from datetime import datetime

#what if we pass time as parameter into spoticli object
#spoticli checks preloop if current time > creation time + 40
#if it is, exit, and have client re-loop it.

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
		return access_token

	#if you return an exit code, it kills the entire program
	#if you DONT return an exit code it doesn't...okay.
		
if __name__ == '__main__':
	#declare spotipy object
	#create spotipy object and pass along to spoticli object
	#while(True):
		#sp = spotipy.Spotify(initialize_env())
		#active = SpotiCLI(sp, current_time).cmdloop()
	SpotiCLI(spotipy.Spotify(initialize_env()), datetime.now()).cmdloop()
	'''
	while(True):
		reauth_exit = SpotiCLI(spotipy.Spotify(initialize_env()), datetime.now())
		reauth_exit.cmdloop()
		print('current state')
		print(reauth_exit)
		if reauth_exit is 1:
			print('exit')
			break
		if reauth_exit is 2:
			print('re-iterate')
			'''