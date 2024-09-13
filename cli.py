#!/usr/bin/python3

'''
Copyright (c) 2023, Hugo A Lopez <95hlopez@gmail.com>
'''

'''
SpotiCLI

this handles the actual cli that user is presented with
'''

import argparse
import fsop
import getpass
import time

from colorama import init, Fore, Back, Style

from tekore import Spotify
from cmd2 import Cmd, with_argparser
from clear_screen import clear

#from colorama import init, Fore, Back, Style

class SpotiCLI(Cmd):
    def __init__(self, token):
        super().__init__()

        self.sp_user = Spotify(token)

        app_name = 'SpotiCLI'
        version = '1.23.0602.dev'

        ###define app parameters
        self.app_info = f'{Fore.CYAN}{Style.BRIGHT}\n{app_name} {version}{Style.RESET_ALL}'
        self.intro = self.app_info + '\n'
        self.prompt = f'{Fore.GREEN}{Style.BRIGHT}spoticli ~$ {Style.RESET_ALL}'

        self.current_endpoint = ''
        self.api_delay = 0.5

        #hide built-in cmd2 functions. this will leave them available for use but will be hidden from tab completion (and docs)
        self.hidden_commands.append('alias')
        self.hidden_commands.append('unalias')
        self.hidden_commands.append('set')
        self.hidden_commands.append('edit')
        self.hidden_commands.append('history')
        self.hidden_commands.append('load')
        self.hidden_commands.append('macro')
        self.hidden_commands.append('py')
        self.hidden_commands.append('pyscript')
        self.hidden_commands.append('quit')
        self.hidden_commands.append('shell')
        self.hidden_commands.append('shortcuts')
        self.hidden_commands.append('_relative_load')
        self.hidden_commands.append('run_pyscript')
        self.hidden_commands.append('run_script')

        # debug false by default
        self.debug = True

        ##define permissions scope...

    #### Misc / Util methods
    ##########################################

    '''
    convert milliseconds into human readable time stamp in format MM:SS
    '''
    def ms_to_time(self, time_to_convert):

        #modulus to get seconds from ms timestamp
        seconds = (time_to_convert / 1000) % 60
        seconds = str(int(seconds))

        #modulus to get minutes from ms timestamp
        minutes = (time_to_convert / (1000 * 60)) % 60
        minutes = str(int(minutes))

        #if seconds is single digit, prefix with 0
        if(len(seconds) < 2):
            seconds = '0' + seconds

        #return formatted value
        return f'{minutes}:{seconds}'

    '''
    generate timestamp in format "length / duration" from song playback data
    '''
    def generate_timestamp(self, song_data):
        pos_ms = self.ms_to_time(self.get_position(song_data))
        dur_ms = self.ms_to_time(self.get_duration(song_data.item))

        return f'{pos_ms} / {dur_ms}'

    ### I don't remember what this did and it's probably no longer needed....
    ### I'll leave it here in case I remember
    def print_list(self, list_to_print):
        for index, item in enumerate(list_to_print):
            self.poutput(f'{index + 1}:\t{item}')

    '''
    formats a track string in format:

    song by artist on album

    params: current playback object
    returns: formatted string
    '''
    def display_song(self, song_data):
        song_name = self.get_song(song_data)
        song_artist = self.get_artist(song_data)
        song_album = self.get_album(song_data)

        return f'{song_name} by {song_artist} on {song_album}'

    '''
    just using this function to standardize the 'no endpoint' error
    '''
    def handle_error_and_print(self, error = None):
        if(error == None):
            self.pwarning('unknown error')
        else:
            self.pwarning(error)
        # self.pwarning('no available playback devices detected')
        # self.pwarning('assign one with the endpoint command')

    #### accessor / mutators
    #### getter / setter, whatever
    #### these make the spotify api calls
    ##########################################

    def get_playback(self):
        return self.sp_user.playback()

    def get_queue(self):
        return self.sp_user.playback_queue()

    def get_current_playback(self):
        return self.sp_user.playback_currently_playing()

    ## accessors
    ############################

    # track specific
    ################

    def get_album(self, song_data):
        try:
            return f'{Fore.MAGENTA}{Style.BRIGHT}{song_data.album.name}{Style.RESET_ALL}'
        except:
            return f'{Fore.MAGENTA}{Style.BRIGHT}{song_data.name}{Style.RESET_ALL}'

    def get_artist(self, song_data):
        ### artists is an array as a song can have multiple artists
        ### if there is multiple artists, return name of _first_ artist in array (usually main artist)
        try:
            return f'{Fore.CYAN}{Style.BRIGHT}{song_data.artists[0].name}{Style.RESET_ALL}'
        except:
            return f'{Fore.CYAN}{Style.BRIGHT}{song_data.name}{Style.RESET_ALL}'


    def get_song(self, song_data):
        return f'{Fore.GREEN}{Style.BRIGHT}{song_data.name}{Style.RESET_ALL}'

    def get_song_id(self, song_data):
        return song_data.id

    def get_duration(self, song_data):
        return song_data.duration_ms

    def get_is_playing(self, song_data):
        return song_data.is_playing

    def get_position(self, song_data):
        return song_data.progress_ms

    # generic functions
    ################

    ### sometimes a device is no longer marked 'active' if it's been idle too long
    ### this 'forces' playback/activity on last active device
    ### need to make this more seemless for the user
    ### def force_device(self):
    ###     current_dev = self.get_device()
    ###     self.sp_user.playback_transfer(current_dev[0].asdict()['id'])
    ###
    ### def do_force(self, line):
    ###     self.force_device()

    # generic accessors
    ################

    def get_device(self):
        return self.sp_user.playback_devices()

    def get_history(self, last_songs):
        return self.sp_user.playback_recently_played(last_songs)

    def get_repeat_state(self):
        try:
            return self.get_playback().repeat_state
        except Exception as error:
            self.handle_error_and_print(error)
            return None

    def get_shuffle_state(self):
        try:
            return self.get_playback().shuffle_state
        except Exception as error:
            self.handle_error_and_print(error)
            return None

    def get_volume(self):
        try:
            return self.get_playback().device.volume_percent
        except Exception as error:
            self.handle_error_and_print(error)
            return None

    ## mutator
    ############################

    ## these methods add artificial delay after calling API
    ## this is needed to allow the API some time to 'catch-up' with our request
    ## needed as we'll usually send a 'get' request not long after and if we send too soon
    ## API might return wrong info

    def set_device(self, new_device):
        self.sp_user.playback_transfer(new_device)
        time.sleep(self.api_delay)

    def set_playback_context(self, playback_uri):
        self.sp_user.playback_start_context(context_uri=playback_uri)
        time.sleep(self.api_delay)

    def set_playback_track(self, new_track):
        if(not isinstance(new_track, list)):
            track_list = []
            track_list.append(new_track)
            self.sp_user.playback_start_tracks(track_ids=track_list)
        else:
            self.sp_user.playback_start_tracks(track_ids=new_track)
        time.sleep(self.api_delay)

    def set_play_next(self):
        try:
            self.sp_user.playback_next()
            time.sleep(self.api_delay)
            self.do_current('')
        except Exception as error:
            self.handle_error_and_print(error)
            return None

    def set_play_resume(self):
        try:
            self.sp_user.playback_resume()
            time.sleep(self.api_delay)
            self.do_current('')
        except Exception as error:
            self.handle_error_and_print(error)
            return None

    def set_play_pause(self):
        try:
            self.sp_user.playback_pause()
            time.sleep(self.api_delay)
            self.do_current('')
        except Exception as error:
            self.handle_error_and_print(error)
            return None

    def set_play_previous(self):
        try:
            self.sp_user.playback_previous()
            time.sleep(self.api_delay)
            self.do_current('')
        except Exception as error:
            self.handle_error_and_print(error)
            return None

    def set_position(self, new_time):
        try:
            self.sp_user.playback_seek(new_time)
            time.sleep(self.api_delay)
            self.do_current('')
        except Exception as error:
            self.handle_error_and_print(error)
            return None

    def set_repeat_state(self, new_repeat_state):
        try:
            self.sp_user.playback_repeat(new_repeat_state)
            time.sleep(self.api_delay)
        except Exception as error:
            self.handle_error_and_print(error)
            return None

    def set_save(self, song_id):
        self.sp_user.saved_tracks_add(song_id)
        time.sleep(self.api_delay)

    def set_unsave(self, song_id):
        self.sp_user.saved_tracks_delete(song_id)
        time.sleep(self.api_delay)

    def set_shuffle_state(self, new_shuffle_state):
        try:
            self.sp_user.playback_shuffle(new_shuffle_state)
            time.sleep(self.api_delay)
        except:
            self.handle_error_and_print()
            return None

    def set_volume(self, new_volume):
        self.sp_user.playback_volume(new_volume)
        time.sleep(self.api_delay)

    #### cmd2 native functions
    ##########################################

    #prints blank line
    #necessary to overload cmd2's default behavior (retry previous command)
    def emptyline(self):
        return

    def precmd(self, line):
        clear()
        return line

    #overloads default error message
    def default(self, line):
        self.perror('unrecognized command')

    #used to write an extra blank line between commands...just a formatting thing.
    def postcmd(self, line, stop):
        self.poutput('')
        return line

    #### Begin CMD2 commands below
    ##########################################

    def do_about(self, line):
        '''
        show build information

        usage:
            about
        '''
        self.poutput(self.app_info)

    def do_diagnostics(self, line):
        '''
        display diagnostic info relating to current session
        '''
        self.poutput(f'current user: \t{self.sp_user.current_user().display_name}')
        #self.poutput(f'device name: \t{self.current_endpoint.name}')
        #self.poutput(f'device id: \t{self.current_endpoint.id}')
        self.poutput(f'api delay: \t{self.api_delay}')

    def do_exit(self, line):
        '''
        exit application

        usage:
            exit
        '''
        return True

    def do_logout(self, line):
        '''
        logout current session and force login next program start

        usage:
            logout
        '''
        is_user_sure = getpass.getpass('are you sure? type \'yes\' to proceed: ')
        self.poutput(is_user_sure)
        if(is_user_sure == 'yes'):
            if(fsop.fsop.delete_conf(self)):
                self.pwarning('user creds deleted')
                return
            self.perror('failed to logout!')
            self.pwarning('unable to delete config files, please try manual removal')
            self.pwarning('can be found in your home config directory, .config/spoticli/')
        else:
            self.pwarning('not logged out')


    #### playback commands
    ##########################################

    ###
    ### [Playing - 0:05 / 4:24] Make Me Wanna Die by The Pretty Reckless on Make Me Wanna Die
    ### [Stopped - 0:05 / 4:24] Make Me Wanna Die by The Pretty Reckless on Make Me Wanna Die
    def do_current(self, line):
        '''
        show currently playing track

        usage:
            current
        '''
        #now_playing = f'[{playing_state} - {timestamp}] {song_name} by {artist_name} on {album_name}'
        song_data = self.get_current_playback()

        if(song_data == None):
            self.handle_error_and_print()
            return

        song_playing = self.get_is_playing(song_data)

        if(song_playing == True):
            song_playing = f'{Fore.BLUE}{Style.BRIGHT}Playing'
        else:
            song_playing = f'{Fore.RED}{Style.BRIGHT}Stopped'

        time_stamp = self.generate_timestamp(song_data)

        now_playing = f'[{song_playing} - {time_stamp}{Style.RESET_ALL}] {self.display_song(song_data.item)}'
        self.poutput(now_playing)

    def play_next(self, args):
        if(self.set_play_next() == None):
            return
        self.poutput('playing next')
        self.do_current(self)

    def play_previous(self, args):
        if(self.set_play_previous() == None):
            return
        self.poutput('playing previous')
        self.do_current(self)

    play_parser = argparse.ArgumentParser(prog='play', add_help=False)
    play_subparsers = play_parser.add_subparsers(title='playback options')

    parser_play_next = play_subparsers.add_parser('next', help='next track', add_help=False)
    parser_play_next.set_defaults(func=play_next)

    parser_play_previous = play_subparsers.add_parser('previous', help='previous track', add_help=False)
    parser_play_previous.set_defaults(func=play_previous)

    play_subcommands = ['next', 'previous']

    @with_argparser(play_parser)
    def do_play(self, line):
        '''
        start or resume playback, or play next/previous song

        usage:
            play [next|previous]
        '''

        # Call whatever sub-command function was selected
        try:
            line.func(self, line)
        #if none specified do default action (start playback)
        except AttributeError:
            try:
                if(self.set_play_resume() == None):
                    return
            except:
                pass
            self.do_current(self)

    def do_pause(self, line):
        '''
        pause playback

        usage:
            pause
        '''
        try:
            if(self.set_play_pause() == None):
                return
        except:
            pass
        self.do_current(self)

    def do_replay(self, line):
        '''
        instantly restart current track

        usage:
            replay
        '''

        ###just re-use existing function
        self.do_seek('0')

    def do_seek(self, line):
        ### time should be in seconds or as a timestamp value, ie. 1:41
        ### not implemented yet...
        '''
        seek to specific time in a track. specify a step increase by prefixing time with +/-

        usage:
            seek [+/-] time
        '''

        ## no value specified; exit
        if(not line):
            self.do_help('seek')
            return

        try:
            new_pos = 1000 * int(line)
        #non-numerical value specified; exit
        except ValueError:
            self.perror('invalid time')
            return

        song_data = self.get_current_playback()
        if(song_data == None):
            self.handle_error_and_print()
            return

        song_pos = self.get_position(song_data)
        song_dur = self.get_duration(song_data.item)

        #if new time is larger than song duration, quit
        if((new_pos > song_dur) or (new_pos < (song_dur * -1))):
            self.perror('invalid time')
            return

        if(line[0] == '+' or line[0] == '-'):
            song_pos = song_pos + new_pos
            self.set_position(song_pos)
        else:
            self.set_position(new_pos)

    #### playback properties
    ##########################################

    def do_volume(self, line):
        '''
        set volume to specified level, range 0-100
        specify a step increase by prefixing value with +/-, otherwise it defaults to 10% step

        usage:
            volume [+/-][value]
        '''

        current_vol = self.get_volume()

        if(current_vol == None):
            return

        if(line):
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
                    self.perror('invalid volume')
                    return

            if new_vol > 100:
                new_vol = 100
            elif new_vol < 0:
                new_vol = 0
            self.set_volume(new_vol)
        self.poutput(f'current volume: {self.get_volume()}')


    def do_endpoint(self, line):
        '''
        transfer playback between valid spotify connect endpoints

        usage:
            endpoint
        '''
        endpoint_list = self.get_device()

        if(len(endpoint_list) == 0):
            self.pwarning('no available endpoints detected')
            self.pwarning('make sure there is an available endpoint before assigning playback again')
            return

        max_index = 0

        print_string = ''
        current_active = ''

        for index, item in enumerate(endpoint_list):
            max_index = index

            print_string += f'{index + 1}:\t{item.name}'

            if(item.is_active):
                current_active = item.name
                print_string += ' (active)'
            print_string += '\n'

        if(current_active == ''):
            current_active = 'No active endpoint'

        self.poutput(f'current endpoint: {current_active}')
        self.poutput('available endpoints:')
        self.poutput(print_string)

        user_input = getpass.getpass('select endpoint: ')
        if(user_input == ''):
            return
        self.poutput(f'selected: {user_input}')

        try:
            user_input = int(user_input) - 1
            if(user_input > max_index or user_input < 0):
                raise ValueError
        except:
            self.pwarning('invalid selection')
            return

        self.set_device(endpoint_list[user_input].id)
        #self.current_endpoint = endpoint_list[user_input]
        #self.set_device(self.current_endpoint.id)

    def repeat_enable(self, args):
        if(self.set_repeat_state('context') == None):
            self.do_repeat('')

    def repeat_track(self, args):
        if(self.set_repeat_state('track') == None):
            self.do_repeat('')

    def repeat_disable(self, args):
        if(self.set_repeat_state('off') == None):
            self.do_repeat('')

    repeat_parser = argparse.ArgumentParser(prog='repeat', add_help=False)
    repeat_subparsers = repeat_parser.add_subparsers(title='repeat states')

    parser_repeat_track = repeat_subparsers.add_parser('track', help='repeat track', add_help=False)
    parser_repeat_track.set_defaults(func=repeat_track)

    parser_repeat_enable = repeat_subparsers.add_parser('enable', help='enable repeat', add_help=False)
    parser_repeat_enable.set_defaults(func=repeat_enable)

    parser_repeat_disable = repeat_subparsers.add_parser('disable', help='disable repeat', add_help=False)
    parser_repeat_disable.set_defaults(func=repeat_disable)

    repeat_subcommands = ['track', 'enable','disable']

    @with_argparser(repeat_parser)
    def do_repeat(self, line):
        '''
        show or modify repeat state

        usage:
            repeat [enable|disable|track]
        '''

        # Call whatever sub-command function was selected
        try:
            line.func(self, line)
        except AttributeError:
            current_repeat = self.get_repeat_state()
            if(current_repeat == None):
                return
            current_repeat = current_repeat.value

            ### valid states:
            ### track - repeat enabled for track
            ### enabled - repeat enabled for playlist/album
            ### disabled - repeat disabled

            if(current_repeat == 'context'):
                self.poutput('repeat is enabled')
            elif(current_repeat == 'off'):
                self.poutput('repeat is disabled')
            elif(current_repeat == 'track'):
                self.poutput('repeating track')

    def shuffle_enable(self, args):
        if(self.set_shuffle_state(True) == None):
            self.do_shuffle('')

    def shuffle_disable(self, args):
        if(self.set_shuffle_state(False) == None):
            self.do_shuffle('')

    shuffle_parser = argparse.ArgumentParser(prog='shuffle', add_help=False)
    shuffle_subparsers = shuffle_parser.add_subparsers(title='shuffle states')

    # create the parser for the "foo" sub-command
    parser_shuffle_enable = shuffle_subparsers.add_parser('enable', help='enable shuffle', add_help=False)
    parser_shuffle_enable.set_defaults(func=shuffle_enable)

    # create the parser for the "foo" sub-command
    parser_shuffle_disable = shuffle_subparsers.add_parser('disable', help='disable shuffle', add_help=False)
    parser_shuffle_disable.set_defaults(func=shuffle_disable)

    shuffle_subcommands = ['enable','disable']

    @with_argparser(shuffle_parser)
    def do_shuffle(self, line):
        '''
        show or modify shuffle state

        usage:
            shuffle [enable|disable]
        '''
        ### valid states:
        ### enabled - shuffle enabled
        ### disabled - shuffle disabled

        #if line is empty, print shuffle state
        try:
            line.func(self, line)
        except AttributeError:
            current_shuffle = self.get_shuffle_state()
            if(current_shuffle == None):
                return

            if(current_shuffle):
                self.poutput('shuffle is enabled')
            else:
                self.poutput('shuffle is disabled')

    #### playlist modification
    ##########################################

    def do_list(self, line):
        '''
        display user playlists

        usage:
            lists
        '''
        max_index = 0
        user_playlists = self.sp_user.followed_playlists().items
        for index, item in enumerate(user_playlists):
            max_index += 1
            self.poutput(f'{index + 1}: \t{item.name}')

        user_input = getpass.getpass('select playlist: ')
        if(user_input == ''):
            return
        self.poutput(f'selected: {user_input}')

        try:
            user_input = int(user_input) - 1
            if(user_input > max_index or user_input < 0):
                raise ValueError
        except:
            self.pwarning('invalid selection')

        self.set_playback_context(user_playlists[user_input].uri)

    def do_previous(self, line):
        '''
        show last 10 songs (or more)

        usage:
            previous [integer]
        '''
        items_to_fetch = 10

        if(line):
            try:
                items_to_fetch = int(line)

                if(items_to_fetch <= 0):
                    items_to_fetch = 3
                    self.pwarning('value too low, retrieving last 3 items')
                    pass

                if(items_to_fetch > 50):
                    items_to_fetch = 50
                    self.pwarning('value too high, retrieving last 50 items')
                    pass
            except:
                self.pwarning('invalid value, retrieving last 10 items')


        for index, prev_song in enumerate(self.get_history(items_to_fetch).items):
            self.poutput(f'{index + 1}: {self.display_song(prev_song.track)}')

    def do_queue(self, line):
        '''
        show upcoming songs

        usage:
            queue
        '''
        playback_list = self.get_queue()

        for index, song in enumerate(playback_list.queue):
            self.poutput(f'{index + 1}: {self.display_song(song)}')

    def do_save(self, line):
        '''
        add currently playing track to liked songs

        usage:
            save
        '''
        song_data = self.get_playback()

        if(song_data == None):
            self.handle_error_and_print()
            return

        song_id = self.get_song_id(song_data.item)

        self.set_save([song_id])
        self.poutput(f'{Fore.RED}{Style.BRIGHT}<3{Style.RESET_ALL} - saved song - {self.display_song(song_data.item)}')

    def do_unsave(self, line):
        '''
        remove currently playing track from liked songs

        usage:
            unsave
        '''

        song_data = self.get_playback()

        if(song_data == None):
            self.handle_error_and_print()
            return

        song_id = self.get_song_id(song_data.item)

        self.set_unsave([song_id])
        self.poutput(f'{Fore.RED}{Style.BRIGHT}</3{Style.RESET_ALL} - removed song - {self.display_song(song_data.item)}')

    def do_search(self, line):
        '''
        search by track, artist or album

        usage:
            search [filter] [-c amount] query

        filters:
            -a, --artist
            -b, --album
            -p, --playlist
            -t, --track

        examples:
            search -t seven nation army
            search -a eminem
            search --playlist -c 3 cool songs
        '''

        if(not line):
            self.pwarning('no query detected')
            self.do_help('search')
            return

        result_limit = 10
        result_type = ()

        ### turn into a list so we can check first flag (if any)
        search_string = line.split(' ')

        ### check for flags in beginning of search string.
        ### if found, remove (so we don't do a search for the flag)
        if('-a' in search_string[0]):
            result_type = result_type + ('artist',)
            search_string.remove('-a')
        elif('-b' in search_string[0]):
            result_type = result_type + ('album',)
            search_string.remove('-b')
        elif('-p' in search_string[0]):
            result_type = result_type + ('playlist',)
            search_string.remove('-p')
        elif('-t' in search_string[0]):
            result_type = result_type + ('track',)
            search_string.remove('-t')

        if(result_type == ()):
            result_type = ('track',)

        #if no flags detected, default search for track

        ##once we finish checking flags turn back into a string and pass along to search call
        search_string = ' '.join(search_string)

        if(search_string == ''):
            self.pwarning('no query detected')
            self.do_help('search')
            return

        search_results = self.sp_user.search(types=result_type, limit=result_limit, query=search_string)
        #print(search_results)

        item_id = []
        for index, item in enumerate(search_results[0].items):
            media_type = item.type

            if(media_type == 'track'):
                self.poutput(f'{str(index + 1)}. \t{media_type} - {self.display_song(item)}')

                ### tekore playback track uses ID or uri depending on what you want to do
                ### save entire item for future ref so we can decide action later
                item_id.append(item)
            if(media_type == 'artist'):
                self.poutput(f'{str(index + 1)}. \t{media_type} - {self.get_artist(item)}')
                item_id.append(item.uri)
            if(media_type == 'album'):
                self.poutput(f'{str(index + 1)}. \t{media_type} - {self.get_album(item)} by {self.get_artist(item)}')
                item_id.append(item.uri)
            if(media_type == 'playlist'):
                self.poutput(f'{str(index + 1)}. \t{media_type} - {item.name}')
                item_id.append(item.uri)

        #for index, item in enumerate(search_results):
            #print(f'{index} : {self.get_song(item[index].items[0].name)}')

        ### check user input for sanity
        user_input = getpass.getpass('select item: ')
        if(user_input == ''):
            return
        self.poutput(f'selected: {user_input}')

        try:
            user_input = int(user_input) - 1
            if(user_input > 9 or user_input < 0):
                raise ValueError
        except:
            self.pwarning('invalid selection')
            return

        ### if input is sane, insta-play. unless it's a track. then prompt for action
        if(result_type == ('track',)):
            self.poutput('1. play')
            self.poutput('2. queue')
            user_action = getpass.getpass('select action: ')
            if(user_action == ''):
                return
            self.poutput(f'selected: {user_action}')

            try:
                user_action = int(user_action) - 1
                if(user_action > 2 or user_action < 0):
                    raise ValueError
            except:
                self.pwarning('invalid action')
                return

            #play
            if(user_action == 0):
                self.set_playback_track(item_id[user_input].id)
                time.sleep(self.api_delay)
                self.do_current('')
                return
            #queue
            if(user_action == 1):
                self.sp_user.playback_queue_add(uri=item_id[user_input].uri)

                self.poutput(f'song queued - {self.display_song(item_id[user_input])}')
                return

        else:
            self.set_playback_context(item_id[user_input])
            time.sleep(self.api_delay)
            self.do_current('')