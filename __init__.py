'''
SpotiCLI
Copyright 2020, Hugo A Lopez

released under the MIT license
'''

## import auth library for authentication
import auth
import getpass
import os
import pickle
import tekore

from cli import SpotiCLI
from os import path
from os.path import expanduser

if __name__ == '__main__':

    #spotify scope
    ##need to convert to tekore friendly format before we pass it along
    #scope = 'user-library-read user-library-modify user-read-currently-playing user-read-playback-state user-modify-playback-state user-read-recently-played playlist-read-private'

    #slash_type = user_home.endswith

    spotify_scopes = (  
        tekore.scope.user_library_read +
        tekore.scope.user_library_modify +
        tekore.scope.user_read_currently_playing +
        tekore.scope.user_read_playback_state +
        tekore.scope.user_modify_playback_state +
        tekore.scope.user_read_recently_played +
        tekore.scope.playlist_read_private
        )
    
    os.chdir(expanduser('~'))
    if(path.exists('.config/spoticli')):
        os.chdir('.config/spoticli')
    else:
        try:
            os.makedirs('.config/spoticli')
            os.chdir('.config/spoticli')
        except:
            ('failed to create directory, do you have write access?')
            exit()

    #dir = os.getcwd()

    if(path.exists('auth.spoticli')):
        try:
            spot_token = pickle.load(open('auth.spoticli', 'rb'))
        except:
            print('cannot read token.spoticli')
            exit()
        ##skip directly to authentication portion

    #explicitly check if conf file exists then create new session based on that
    elif(path.exists('conf.spoticli')):
        spot_creds = tekore.config_from_file('conf.spoticli')
        spot_token = tekore.prompt_for_user_token(*spot_creds, scope=spotify_scopes)

    elif(not path.exists('conf.spoticli')):
        print('you will need your client id and secret')
        print('you can find this from the spotify developer dashboard')
        print('devloper.spotify.com/dashboard')
        print('remember most api functionality is locked to premium subscriptions')
        client_id = getpass.getpass('input client id: ')
        client_key = getpass.getpass('input client secret: ')

        #quick sanity check to make sure secret and id are same length and are 32 characters long
        if(len(client_id) != len(client_key) or (len(client_id) != 32)):
            print('invalid id or secret')
            exit()
        try:
            print('creating auth file')
            conf_file = open('conf.spoticli', 'w')
            conf_file.write('[DEFAULT]')
            conf_file.write('\n')
            conf_file.write(f'SPOTIFY_CLIENT_ID={client_id}')
            conf_file.write('\n')
            conf_file.write(f'SPOTIFY_CLIENT_SECRET={client_key}')
            conf_file.write('\n')
            conf_file.write('SPOTIFY_REDIRECT_URI=http://localhost:8080/callback')
            conf_file.close()
            #blank_or_create()
        except:
            print('error while creating auth file, do you have proper permissions?')
            exit()
        spot_creds = tekore.config_from_file('conf.spoticli')
        spot_token = auth.prompt_for_user_token(*spot_creds, scope=spotify_scopes)

            #creds.prompt(client_id, secret) #redirect uri not needed from user, will always be localhost:8080
            #write_to_conf.spoticli   

    ##load local creds
    ##retrieve token using local creds    
    #### spotify = Spotify(token)
    #### tracks = spotify.current_user_top_tracks(limit=10)
    #### print(tracks)
    ### pass token to spoticli, spoticli with instantiate spotify object and handle refreshing
    ### spoticli will handle auth user and periodically refresh token as needed

    #if auth failed and returned a null token, exit program
    if(spot_token is None):
        print('invalid token detected')
        exit()
    try:
        ## for session presevation, serialize/dump the token into readable file
        ## this will attempt to be loaded next time user uses the program

        ## will this always work? theoretically yes as tekore uses self-refreshing tokens. 
        pickle.dump(spot_token, open('auth.spoticli', 'wb'))
    except:
        print('warning, failed to write token! session will not be preserved!')
        pass

    exit_code = SpotiCLI(token=spot_token).cmdloop()