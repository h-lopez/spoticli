'''
SpotiCLI
Copyright 2020, Hugo A Lopez

released under the MIT license
'''

from tekore import Spotify, util
from cmd2 import Cmd, with_argparser
#from colorama import init, Fore, Back, Style

class SpotiCLI(Cmd):
    def __init__(self, token):
        super().__init__()

        app_name = 'SpotiCLI'
        version = '1.20.0413.dev'
        
        ###define app parameters
        self.app_info = f'\n{app_name} {version}'
        self.intro = self.app_info + '\n'
        self.prompt = 'spoticli ~$ '

        self.sp_user = Spotify(token)

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
        self.hidden_commands.append('shell')
        self.hidden_commands.append('shortcuts')
        self.hidden_commands.append('_relative_load')
        self.hidden_commands.append('run_pyscript')
        self.hidden_commands.append('run_script')

        ##define permissions scope...

    #### cmd2 native functions
    ##########################################
    
    #prints blank line
    #necessary to overload cmd2's default behavior (retry previous command)
    def emptyline(self):
        return

    #overloads default error message
    def default(self, line):
        print('Unrecognized command')

    #used to write an extra blank line between commands...just a formatting thing.
    def postcmd(self,line,stop):
        print('')
        return line

    #### Begin CMD2 commands below 
    ##########################################

    def do_about(self, line):
        '''show build information'''
        print(self.app_info)

    def do_diagnostics(self, line):
       '''show program diagnostics'''
       #print(self.sp_user.current_user_top_tracks(limit=10))
       print('no diagnostics to show')
    
    #### playback commands
    ##########################################

    def do_current(self, line):
        '''show currently playing track'''
        print('placeholder')

    def do_play(self, line):
        '''start or resume playback, or play next/previous song'''
        if(line == 'previous'):
            self.sp_user.playback_previous()
            print('playing previous')
        if(line == 'next'):
            self.sp_user.playback_next()
            print('playing next')
        else:
            try:
                self.sp_user.playback_resume()
            except:
                print('')
            print('playing')

    def do_pause(self, line):
        '''pause playback'''
        try:
            self.sp_user.playback_pause()
        except:
            print('')
        print('paused')
    
    def do_seek(self, line):
        '''seek to specific time in a track
        usage: seek [seconds]
        you can also specify a step increase by prefixing time with +/-'''
        self.sp_user.playback_seek()
        print('placeholder')

    #### playback properties
    ##########################################

    def do_volume(self, line):
        '''set volume to specified level, range 0-100
        usage: volume [value]
        specify a step increase by prefixing value with +/-, otherwise it defaults to 10% step'''
        print('placeholder')

    def do_mute(self, line):
        '''mutes current track. invoking command while muted will return to orignal volume.'''
        print('placeholder')
    
    def do_endpoint(self, line):
        '''transfer playback between valid spotify connect endpoints'''
        print('placeholder')
    
    def do_repeat(self, line):
        '''show or modify repeat state'''
        ### valid states: 
        ### track - repeat enabled for track
        ### enabled - repeat enabled for playlist/album
        ### disabled - repeat disabled
        print('placeholder')

    def do_shuffle(self, line):
        '''show or modify shuffle state'''
        ### valid states: 
        ### enabled - shuffle enabled
        ### disabled - shuffle disabled
        print('placeholder')
            
    #### playlist modification
    ##########################################

    def do_list(self, line):
        '''display user playlists'''
        print('placeholder')

    def do_previous(self, line):
        '''show previous songs'''
        print('placeholder')
    
    def do_queue(self, line):
        '''show and modify queue'''
        print('not implemented. pending expansion of spotify api')

    def do_save(self, line):
        '''add currently playing track to liked songs'''
        print('placeholder')
    
    def do_unsave(self, line):
        '''remove currently playing track from liked songs'''
        print('placeholder')

    def do_search(self, line):
        '''search by song, artist or album'''
        print('placeholder')