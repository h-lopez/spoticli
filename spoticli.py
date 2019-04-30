'''
SpotiCLI
Copyright 2019, Hugo A Lopez

to use, make sure you have your client-id, client-secret and username handy to build this out
i'll add a way to specify your client information details w/o hardcoding (eventually)

released under the do whatever the fuck you like license
'''

import argparse
import json
import os
import subprocess
import sys
import threading
import time

#spotipy library
#handles json calls to spotify API
import spotipy
import spotipy.util

#colorama library
#allows printing of text in different colors
from colorama import init, Fore, Back, Style
from datetime import datetime, timedelta

#cmd2 libary
#provides command line shell and interpreter
from cmd2 import Cmd, with_argparser

class SpotiCLI(Cmd):

	def __init__(self):
		#Cmd.__init__(self)
		#persistent history means that previous commands are saved between sessions, instead of being cleared after program is exited.
		super().__init__(persistent_history_file='~/.history', persistent_history_length=25)
		
		#depends on colorama
		#necessary for auto-resetting colors to white after color change is applied
		init(autoreset=True)
		
		app_name = 'SpotiCLI'
		author = 'Author:\t\tHugo A Lopez'
		version = 'Version:' + '\t' + '1.0.19.0424'
		self.app_info = Fore.CYAN + '\n' + app_name + '\n\n' + author + '\n' + version
		
		self.current_token = ''
		self.spotipy_instance = ''
		self.enable_logging = False
		self.intro = ''#self.app_info + '\n'
		self.prompt = Fore.GREEN + os.getlogin() + '@spoticli ~$ '
		self.allow_cli_args = False
		self.allow_redirection = False
		self.locals_in_py = False
		self.use_ipython = False
		self.transcript_files = False
		self.persistent_history_length = 25
		self.persistent_history_file = '~/.history'
		
		#default expiration time to 45min before exiting and requesting new token
		self.creation_time = (datetime.now().timestamp())
		self.expiration_time = self.creation_time
		os.system('title SpotiCLI')
		
		#need to look into setting title from cmd2 built-in vs importing another lib
		#self.set_window_title('Spoticli')

		#better to hide, we never know if we might need them (since they're actually useful)
		self.hidden_commands.append('alias')
		self.hidden_commands.append('unalias')
		self.hidden_commands.append('set')
		self.hidden_commands.append('edit')
		self.hidden_commands.append('load')
		self.hidden_commands.append('macro')
		self.hidden_commands.append('py')
		self.hidden_commands.append('pyscript')
		self.hidden_commands.append('shell')
		self.hidden_commands.append('shortcuts')
		self.hidden_commands.append('_relative_load')
		self.hidden_commands.append('quit')

	#basic data retrieval/mutator fuctions
	#used internally (within program) NOT from CLI context	
	#all have same basic functionality; 
	#check if returned is null, if it is then we hit a device inactivity timeout
	#will have spotipy try to reassign first available device
	#function will then attempt to retrieve/return requested data
	def get_current_playback_data(self):
		data = self.parse(self.spotipy_instance.current_user_playing_track())
		if data is None:
			self.force_device()
			data = self.parse(self.spotipy_instance.current_user_playing_track())
		return data

	def get_current_playback_state(self):
		data = self.parse(self.spotipy_instance.current_playback())
		if data is None:
			self.force_device()
			data = self.parse(self.spotipy_instance.current_playback())
		return data

	def get_is_playing(self, song_data):
		data = song_data['is_playing']
		if data is None:
			self.force_device()
			print('invalid device?')
			data = song_data['is_playing']
		return data

	def get_song(self, song_data):
		data = song_data['item']['name']
		if data is None:
			self.force_device()
			print('invalid device?')
			data = song_data['item']['name']
		return data

	def get_artist(self, song_data):
		data = song_data['item']['artists'][0]['name']
		if data is None:
			self.force_device()
			print('invalid device?')
			data = song_data['item']['artists'][0]['name']
		return data

	def get_album(self, song_data):
		data = song_data['item']['album']['name']
		if data is None:
			self.force_device()
			print('invalid device?')
			data = song_data['item']['album']['name']
		return data

	def get_duration(self, song_data):
		data = song_data['item']['duration_ms']
		if data is None:
			self.force_device()
			print('invalid device?')
			data = song_data['item']['duration_ms']
		return data

	def get_postion(self, song_data):
		data = song_data['progress_ms']
		if data is None:
			self.force_device()
			print('invalid device?')
			data = song_data['progress_ms']
		return data

	def get_repeat(self, playback_data):
		data = playback_data['repeat_state']
		if data is None:
			self.force_device()
			print('invalid device?')
			data = playback_data['repeat_state']
		return data

	def get_shuffle(self, playback_data):
		data = playback_data['shuffle_state']
		if data is None:
			self.force_device()
			print('invalid device?')
			data = playback_data['shuffle_state']
		return data

	def get_volume(self, playback_data):
		data = playback_data['device']['volume_percent']
		if data is None:
			self.force_device()
			print('invalid device?')
			data = playback_data['device']['volume_percent']
		return data

	def get_devices(self):
		data = self.parse(self.spotipy_instance.devices())
		return data
	
	#attempt to force device choice by selecting 1st available device, in case device timeout is reached
	#if it is, blindly select the first available (should be the same that user was using already)
	def force_device(self):
		data = self.get_devices()
		self.spotipy_instance.transfer_playback(data['devices'][0]['id'], False)
	
	#takes value in milliseconds, converts to MM:SS timestamp, returns value as string
	def ms_to_time(self, ms_timestamp):
		seconds=(ms_timestamp / 1000) % 60
		seconds = int(seconds)

		minutes=(ms_timestamp /(1000 * 60)) % 60
		minutes = str(int(minutes))

		if(seconds < 10):
			seconds = '0' + str(seconds)
		else:
			seconds = str(seconds)
		return(minutes + ':' + seconds)

	#takes song information and converts to formatted elapsed time stamp
	# Elapsed Time (format MM:SS) / Total Time (format MM:SS)
	def generate_timestamp(self, song_data):
		return self.ms_to_time(self.get_postion(song_data)) + ' / ' + self.ms_to_time(self.get_duration(song_data))

	#parses a string into indexed JSON format
	def parse(self, data):
		return json.loads(json.dumps(data))
	
	#prints blank line
	#necessary to overload cmd2's default behavior (retry previous command)
	def emptyline(self):
		return

	#overloads default error message
	def default(self, line):
		print(Fore.RED + 'Unrecognized command')

	#create initial spotipy object and program start
	def preloop(self):
		self.refresh_session()
	
	#check is token is dead before executing command
	#if dead, refresh token, then pass command
	#if not dead, pass command
	def precmd(self, line):
		if int(datetime.now().timestamp()) > self.expiration_time:
			#print('Attempting token refresh...')
			self.refresh_session()
		return line

	#this creates a new spotipy session with new token.
	#need to decouple user clientid/secret from this method 
	def refresh_session(self):
		#explicitly kill session
		self.spotipy_instance = ''
		scope = 'user-library-read user-library-modify user-read-currently-playing user-read-playback-state user-modify-playback-state user-read-recently-played'
		username = '95hlopez@gmail.com'
		client_id = 'ad61a493657140c8a663f8db17730c4f'
		client_secret = '3c403975a6874b238339db2231864294'
		redirect_uri = 'http://localhost'
		cache = '.spotipyoauthcache'
		access_token = spotipy.util.obtain_token_localhost(username,client_id,client_secret,redirect_uri,cache,scope)
		self.current_token = access_token
		if access_token:
			#assuming new token was retrieved successfully, create new session.
			self.spotipy_instance = spotipy.Spotify(access_token)
			#assuming this was successful, try to read spotipy auth token to get expiration
			self.creation_time = int(datetime.now().timestamp())
			try:
				self.expiration_time = json.loads(open('.spotipyoauthcache', 'r').read())['expires_at']
			except:
				#if token wasn't found, just set expiration to 5m from now
				print('cached token not found?!')
				self.expiration_time = int(datetime.timestamp(datetime.now() + timedelta(minutes=5)))
			#print('new token requested') 
	
	#used to write an extra blank line between commands
	def postcmd(self,line,stop):
		print('')
		return line
	
	# ######################################## #
	# ###### Begin CMD2 commands below ####### #
	# ######################################## #
	def do_exit(self, line):
		'''Exit SpotiCLI'''
		quit()

	def do_about(self, line):
		'''Show Build Information'''
		print(self.app_info)
		
	def do_diagnostics(self, line):
		'''Show Diagnostics'''
		print('')
		print('Time (Central ST): ' + Fore.CYAN + str(datetime.now()))
		print('Current UNIX time: ' + str(int(datetime.now().timestamp())))
		print('Token create time: ' + str(self.creation_time))
		print('Token expire time: ' + str(self.expiration_time))
		print('SP Memory Address: ' + Fore.CYAN + str(self.spotipy_instance))
		print('')
		print('Spotipy Token ID: \n' + str(self.current_token))

	def search_result_parser(self, search_type, result_count, args):
		args = ' '.join(args.query)
		#need to append 's' at of query type
		#spotify uses plurals as the keys in the search api
		return self.parse(self.spotipy_instance.search(args,type=search_type,limit=result_count))[search_type + 's']['items']

	def search_selection(self, parsed_results, result_limit, args):
		user_choice = input("\nSelect result: ")

		#if user sent no value (empty) exit to main command loop
		if(user_choice == ''):
			return
		try:
			user_choice = int(user_choice)

		#if user sent non-integer value, exit to main cmd loop
		except ValueError:
			print('invalid selection')
			return

		#if user sent value out of range, exit to main cmd loop
		if (user_choice <= 0 or user_choice > result_limit):
			print('invalid selection')
			return

		#return the uri/context uri
		#need to subtract 1 from user_choice because arrays start at 0
		return parsed_results[user_choice - 1]['uri']

	def action_selection(self, args):
		action_list = '\n1: Play\n' + '2: Queue\n' +  '3: Save\n' + '4: Unsave\n'
		print(action_list)
		user_choice = input("Select action: ")
		if(user_choice == ''):
			return
		try:
			user_choice = int(user_choice)

		except ValueError:
			print('invalid selection')
			return

		# 1 = play
		# 2 = queue
		# 3 = save
		# 4 = unsave

		if(user_choice == 1):
			return 'play'
		if(user_choice == 2):
			return 'queue'
		if(user_choice == 3):
			return 'save'
		if(user_choice == 4):
			return 'unsave'
		if(user_choice <= 0 or user_choice > 4):
			print('invalid selection')
			return

	def search_song(self, args):
		'''searches for song, and prints results
		Usage: search song [query]'''
		result_limit = 5
		parsed_results = self.search_result_parser('track', result_limit, args)

		#if results are less < 5, only print the # of returned results
		if(result_limit > len(parsed_results)):
			result_limit = len(parsed_results)

		#if size of results is 0, print out error of now songs found and return
		if(result_limit < 1):
			print('No results for query!')
			return

		#iterates through list of (parsed) results and prints out each one.
		print('')
		for x in range(0, result_limit):
			print(
				str(x + 1) + ': ' +
				parsed_results[x]['name'] + ' by ' +
				parsed_results[x]['album']['artists'][0]['name'] + ' on ' +
				parsed_results[x]['album']['name'])

		#presents users with options after a selection is made (via numkeys on keyboard)
		song_id = self.search_selection(parsed_results, result_limit, args)
		if(song_id):
			#self.spotipy_instance.start_playback(uris=song_id.split())
			#'do what' code goes right here.
			action_id = self.action_selection(args)
			if(action_id):
				song_id = song_id.split()
				if(action_id == 'play'):
					self.spotipy_instance.start_playback(uris=song_id)
					self.do_current('')
				if(action_id == 'queue'):
					print('queuing is not currently supported')
				if(action_id == 'save'):
					self.spotipy_instance.current_user_saved_tracks_add(song_id)
				if(action_id == 'unsave'):
					self.spotipy_instance.current_user_saved_tracks_delete(song_id)
		else:
			return

	def search_artist(self, args):
		'''searches for artist
		Usage: search artist [query]'''
		result_limit = 5
		parsed_results = self.search_result_parser('artist', result_limit, args)

		if(result_limit > len(parsed_results)):
			result_limit = len(parsed_results)

		if(result_limit < 1):
			print('No results for query!')
			return

		for x in range(0, result_limit):
			print(
				str(x + 1) + ': ' +
				parsed_results[x]['name'])

		artist_id = self.search_selection(parsed_results, result_limit, args)
		if(artist_id):
			self.spotipy_instance.start_playback(context_uri=artist_id)
		else:
			return

	def search_album(self, args):
		'''searches for album
		Usage: search album [query]'''
		result_limit = 5
		parsed_results = self.search_result_parser('album', result_limit, args)

		if(result_limit > len(parsed_results)):
			result_limit = len(parsed_results)

		if(result_limit < 1):
			print('No results for query!')
			return

		for x in range(0, result_limit):
			print(
				str(x + 1) + ': ' +
				parsed_results[x]['name'] + ' by ' +
				parsed_results[x]['artists'][0]['name'])

		#play playlist directly from results
		album_id = self.search_selection(parsed_results, result_limit, args)
		if(album_id):
			self.spotipy_instance.start_playback(context_uri=album_id)
		else:
			return

	def search_playlist(self, args):
		'''searches for playlist
		Usage: search playlist [query]'''
		result_limit = 5
		parsed_results = self.search_result_parser('playlist', result_limit, args)

		if(result_limit > len(parsed_results)):
			result_limit = len(parsed_results)

		if(result_limit < 1):
			print('No results for query!')
			return

		for x in range(0, result_limit):
			print(
				str(x + 1) + ': ' +
				parsed_results[x]['name'])

		#play playlist directly from results
		playlist_id = self.search_selection(parsed_results, result_limit, args)
		if(playlist_id):
			self.spotipy_instance.start_playback(context_uri=playlist_id)
		else:
			return

	search_parser = argparse.ArgumentParser(prog='search', add_help=False)
	search_subparsers = search_parser.add_subparsers(title='Search parameters')

	parser_song = search_subparsers.add_parser('song', help='Search by Track title (default behaviour)', add_help=False)
	parser_song.add_argument('query', nargs='+', help='search string')
	parser_song.set_defaults(func=search_song)

	parser_artist = search_subparsers.add_parser('artist', help='Search by Artist', add_help=False)
	parser_artist.add_argument('query', nargs='+', help='search string')
	parser_artist.set_defaults(func=search_artist)

	parser_album = search_subparsers.add_parser('album', help='Search by Album', add_help=False)
	parser_album.add_argument('query', nargs='+', help='search string')
	parser_album.set_defaults(func=search_album)

	parser_playlist = search_subparsers.add_parser('playlist', help='Search by Playlist', add_help=False)
	parser_playlist.add_argument('query', nargs='+', help='search string')
	parser_playlist.set_defaults(func=search_playlist)

	search_subcommands = ['song', 'artist', 'album','playlist']

	@with_argparser(search_parser)
	def do_search(self, args):
		'''Search by artist, album, track or playlist'''
		try:
			# Call whatever sub-command function was selected
			args.func(self, args)
		except AttributeError:
			# No sub-command was provided, so as called
			self.do_help('search')

	def do_current(self, line):
		'''Show Current Track'''

		#need delay to make sure data spotify gives us is up to date, especially if we recently (<100ms) changed track or changed playback state
		time.sleep(0.5)

		#pull JSON on currently playing track & parse into python friendly format
		now_playing = self.get_current_playback_data()
		#parsed = self.parse(self.spotipy_instance.current_user_playing_track())

		#pull song name, artist and album, print to console
		song_name = self.get_song(now_playing)
		artist_name = self.get_artist(now_playing)
		album_name = self.get_album(now_playing)
		timestamp = self.generate_timestamp(now_playing)
		playing_state = ''

		if(self.get_is_playing(now_playing)):
			playing_state = '[Playing'
		else:
			playing_state = '[Stopped'

		print(  playing_state + ' - ' +
				timestamp + ']' + ' - ' +
				song_name + ' by ' +
				artist_name + ' on ' +
				album_name)
	
	def do_play(self, line):
		'''Start Playback'''
		if(not self.get_is_playing(self.get_current_playback_data())):
			self.spotipy_instance.start_playback()
		self.do_current('')
		
	def do_pause(self, line):
		'''Pause Playback'''
		if(self.get_is_playing(self.get_current_playback_data())):
			self.spotipy_instance.pause_playback()
		self.do_current('')
		
	# wtf
	# AttributeError: 'Spotify' object has no attribute 'user_follow_artists'
	#
	#def do_follow(self, line):
	#	'''follows artist of currently playing track'''
	#	now_playing = self.get_current_playback_data()
	#	self.spotipy_instance.user_follow_artists(now_playing['item']['artist']['id'].split())
	#	print(Fore.RED + '<3 - Artist Followed')

	#not currently possible to unfollow artist in spotipy API...oh well...
	#def do_unfollow(self, line):
	#	'''unfollows artist of currently playing track'''
	#	now_playing = self.get_current_playback_data()
	#	print(Fore.RED + '<3 - Artist Unfollowed')

	def do_save(self, line):
		'''Save Track to user library '''
		now_playing = self.get_current_playback_data()
		self.spotipy_instance.current_user_saved_tracks_add(now_playing['item']['id'].split())
		print(Fore.RED + Style.BRIGHT + '<3 - Track Saved!')

	def do_unsave(self, line):
		'''Remove Track from user library'''
		now_playing = self.get_current_playback_data()
		self.spotipy_instance.current_user_saved_tracks_delete(now_playing['item']['id'].split())
		print(Fore.RED + Style.BRIGHT + '</3 - Track Unsaved!')

	def do_queue(self, line):
		'''Show queued songs'''
		print('queueing not implemented (awaiting future spotify API implementation)')

	def do_upcoming(self, line):
		'''Show List of upcoming songs (defaults to 5)'''
		print('upcoming songs not implemented (awaiting future spotify API implementation')
		# check if queue, get first 5
		# if queue has <5 songs or queue empty, check remainder from songs in playlist
		# if still <5 just print what we have
		# if nothing, display none
		
	def do_seek(self, line):
		'''Seek to specific time in a track
	Usage: seek [seconds]
	You can also specify a step increase by prefixing time with +/-'''

		#prints help command if no data is passed to seek
		if not line:
			self.do_help('seek')
			return

		try:
			new_pos = 1000 * int(line)
		except ValueError:
			print('invalid time')
			return

		now_playing = self.get_current_playback_state()
		song_duration = self.get_duration(now_playing)
		song_position = self.get_postion(now_playing)

		if((new_pos > song_duration) or (new_pos < (song_duration * -1))):
			print('invalid time')
			return

		if(line[0] == '+' or line[0] == '-'):
			song_position = song_position + new_pos
			self.spotipy_instance.seek_track(song_position)
		else:
			self.spotipy_instance.seek_track(new_pos)
		#print(str(new_pos/1000) + ' / ' + str(song_duration/1000))
		self.do_current('')

	def do_previous(self, line):
		'''Play Previous Track'''
		self.spotipy_instance.previous_track()
		self.do_current('')

	def do_next(self, line):
		'''Play Next Track'''
		self.spotipy_instance.next_track()
		self.do_current('')

	def do_again(self, line):
		'''Replay current track'''
		#literally the same as 'seek 0'
		self.spotipy_instance.seek_track(0)
		self.do_current('')

	def shuffle_on(self, args):
		self.spotipy_instance.shuffle(True)
		time.sleep(0.5)
		self.do_shuffle('')

	def shuffle_off(self, args):
		self.spotipy_instance.shuffle(False)
		time.sleep(0.5)
		self.do_shuffle('')

	shuffle_parser = argparse.ArgumentParser(prog='shuffle', add_help=False)
	shuffle_subparsers = shuffle_parser.add_subparsers(title='Shuffle States:')

	# create the parser for the "foo" sub-command
	parser_shuffle_on = shuffle_subparsers.add_parser('on', help='Enable shuffle', add_help=False)
	parser_shuffle_on.set_defaults(func=shuffle_on)

	# create the parser for the "foo" sub-command
	parser_shuffle_off = shuffle_subparsers.add_parser('off', help='Disable shuffle', add_help=False)
	parser_shuffle_off.set_defaults(func=shuffle_off)

	search_subcommands = ['on','off']

	@with_argparser(shuffle_parser)
	def do_shuffle(self, args):
		'''Show or change shuffle mode'''
		try:
			# Call whatever sub-command function was selected
			args.func(self, args)
		except AttributeError:
			# No sub-command was provided, so as called
			playback = self.get_shuffle(self.get_current_playback_state())
			if(playback==True):
				print("Shuffle is enabled")
			else:
				print("Shuffle is disabled")

	#these commands have minor delays as spotify API has to process our changes before we 
	#can read them, otherwise we'll be reading old data if there's little to no delay.
	#while we can just print the state we selected, there's no confirmation our changes were taken by spotify.
	#it's shitty, but no good alternative is available
	def repeat_on(self, args):
		self.spotipy_instance.repeat('context')
		time.sleep(0.5)
		self.do_repeat('')

	def repeat_track(self, args):
		self.spotipy_instance.repeat('track')
		time.sleep(0.5)
		self.do_repeat('')

	def repeat_off(self, args):
		self.spotipy_instance.repeat('off')
		time.sleep(0.5)
		self.do_repeat('')

	repeat_parser = argparse.ArgumentParser(prog='repeat', add_help=False)
	repeat_subparsers = repeat_parser.add_subparsers(title='Repeat States')

	parser_repeat_track = repeat_subparsers.add_parser('track', help='Repeat current track indefinitely', add_help=False)
	parser_repeat_track.set_defaults(func=repeat_track)

	parser_repeat_on = repeat_subparsers.add_parser('on', help='Enable Repeat within a context (ie. Album, Playlist, etc.', add_help=False)
	parser_repeat_on.set_defaults(func=repeat_on)

	parser_repeat_off = repeat_subparsers.add_parser('off', help='Disable Repeat', add_help=False)
	parser_repeat_off.set_defaults(func=repeat_off)

	search_subcommands = ['track', 'on','off']

	@with_argparser(repeat_parser)
	def do_repeat(self, args):
		'''Show or change repeat mode'''
		try:
			# Call whatever sub-command function was selected
			args.func(self, args)
		except AttributeError:
			# No sub-command was provided, so as called
			playback = self.get_repeat(self.get_current_playback_state())
			if(playback == 'track'):
				print("Repeating Track")
			elif(playback == 'context'):
				print("Repeating is contextual (Album, Playlist, etc)")
			else:
				print("Repeat is disabled")

	def do_history(self, line):
	#def do_old(self, line):
	#history is built-in cmd2 command, being overloaded by function that displays last 5 songs.
		'''Show last 5 played songs'''
		result_limit = 5
		history_list = self.spotipy_instance.current_user_recently_played(result_limit)
		parsed_results = self.parse(history_list['items'])
		#print(parsed_results)
		#if results are less < 5, only print the # of returned results
		if(result_limit > len(parsed_results)):
			result_limit = len(parsed_results)

		#if size of results is 0, print out error of now songs found and return
		if(result_limit < 1):
			print('No results for query!')
			return

		for x in range(0, result_limit):
			print(
				str(x + 1) + ': ' +
				parsed_results[x]['track']['name'] + ' by ' +
				parsed_results[x]['track']['artists'][0]['name'] + ' on ' +
				parsed_results[x]['track']['album']['name'])

		user_choice = input("\nSelect result: ")
		if(user_choice == ''):
			return
		try:
			user_choice = int(user_choice)

		#if user sent non-integer value, exit to main cmd loop
		except ValueError:
			print('invalid selection')
			return
			
		#if user sent value out of range, exit to main cmd loop
		if (user_choice <= 0 or user_choice > result_limit):
			print('invalid selection')
			return
		
		song_id = parsed_results[user_choice - 1]['track']['uri']
		print(song_id)
		if(song_id):
			#self.spotipy_instance.start_playback(uris=song_id.split())
			#'do what' code goes right here.
			action_id = self.action_selection(line)
			if(action_id):
				song_id = song_id.split()
				if(action_id == 'play'):
					self.spotipy_instance.start_playback(uris=song_id)
					self.do_current('')
				if(action_id == 'queue'):
					print('queuing is not currently supported')
				if(action_id == 'save'):
					self.spotipy_instance.current_user_saved_tracks_add(song_id)
				if(action_id == 'unsave'):
					self.spotipy_instance.current_user_saved_tracks_delete(song_id)
		else:
			return
				
	def do_volume(self, line):
		'''Set volume to specified level, range 0-100
	Usage: volume [value]
	Volume must be between 0 and 100, inclusive
	You can also specify a step increase by prefixing value with +/-, otherwise it defaults to 10'''
		current_vol = self.get_volume(self.get_current_playback_state())

		if not line:
			print('volume: ' + str(current_vol))
			return

		try:
			new_vol = int(line)
			if(line[0] == '+' or line[0] == '-'):
				new_vol = new_vol + current_vol
		except ValueError:
			if(line[0] == '+'):
				new_vol = current_vol + 10
			elif(line[0] == '-'):
				new_vol = current_vol - 10
			else:
				print('invalid volume')
				return
			#print(Style.BRIGHT + Fore.RED + 'Invalid volume ' + '\'' + line +'\'')

		if(new_vol > 100):
			new_vol = 100
		elif(new_vol < 0):
			new_vol = 0

		self.spotipy_instance.volume(new_vol)
		print('volume: ' + str(new_vol))

	#moved to separate function to allow
	#otherwise, this will break stuff when device timeout is reached.
	def current_device(self):
		print('current device: ' + self.get_current_playback_state()['device']['name'])
		
	def do_devices(self, line):
		'''Transfer playback between devices'''
		device_list = self.get_devices()
		device_length = len(self.get_devices()['devices'])

		self.current_device()
		
		for x in range (0, device_length):
			print(str(x + 1) + ': ' + device_list['devices'][x]['name'])

		user_choice = input("Select device: ")

		#if user sent no value (empty) exit to main command loop
		if(user_choice == ''):
			return
		try:
			user_choice = int(user_choice)
		#if user sent non-integer value, exit to main cmd loop
		except ValueError:
			print('invalid selection')
			return

		#if user sent value out of range, exit to main cmd loop
		if (user_choice <= 0 or user_choice > device_length):
			print(user_choice)
			print(device_length)
			print('invalid selection')
			return

		#transfer playback on selected device, but don't actually start playing yet.
		#subtract one because arrays start at 0
		
		self.spotipy_instance.transfer_playback(device_list['devices'][user_choice - 1]['id'], False)