#!/usr/bin/python3

'''
Copyright (c) 2023, Hugo A Lopez <95hlopez@gmail.com>
'''

## import auth library for authentication
import auth
import getpass
import fsop
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

    file_auth = 'auth.spoticli'
    file_conf = 'conf.spoticli'
    path_cred = '.config/spoticli'

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
    if(path.exists(path_cred)):
        os.chdir(path_cred)
    else:
        try:
            os.makedirs(path_cred)
            os.chdir(path_cred)
        except:
            ('failed to create directory, do you have write access?')
            exit()

    #dir = os.getcwd()

    if(path.exists(file_auth)):
        try:
            #fourth element is the refresh token
            #try to create new session based on this token
            spot_token = tekore.config_from_file(file_auth, return_refresh=True)
            client_id = spot_token[0]
            client_key = spot_token[1]
            user_re_token = spot_token[3]
            spot_token = tekore.refresh_user_token(client_id, client_key, user_re_token)
            #spot_token = pickle.load(open(file_auth, 'rb'))
            ##skip directly to authentication portion
        except:
            print('cannot read auth.spoticli')
            print('attempting to delete auth.spoticli')
            if(fsop.fsop.delete_conf('')):
                print('auth.spoticli deleted')
                print('please restart spoticli')
                exit()
            print('unable to delete auth.spoticli')
            print('do you have read/write access to directory?')
            print('please attempt manually deleting the file and restarting spoticli')
            print('file is located in .config/spoticli/ directory')
            exit()

    #if we made it here the auth file doesn't exist for some reason
    #explicitly check if conf file exists then create new session based on that
    ### elif(path.exists(file_conf)):
    ###     spot_creds = tekore.config_from_file(file_conf)
    ###     print('found conf.spoticli but not new auth.spoticli')
    ###     print('spinning up new session using conf.spoticli')
    ###
    ###     spot_token = auth.prompt_for_user_token(*spot_creds, scope=spotify_scopes)
    ###     #re-save the auth token
    ###     tekore.config_to_file(file_auth, ('', '', '', spot_token.refresh_token))

    #elif(not path.exists(file_conf)):
    else:
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


        new_creds = (client_id, client_key, 'http://localhost:8080/callback', None)

        try:
            ##save method, client ID, secret, redirect URL, refresh token
            ## we don't have refresh token yet, so we'll just save this to a config file that tekore can read
            tekore.config_to_file(file_conf, new_creds)

            #old way, deprecated in place of tekore's builtin method
            #print('creating auth file')
            #auth_file_contents = '[DEFAULT]\n' + f'SPOTIFY_CLIENT_ID={client_id}\n' + f'SPOTIFY_CLIENT_SECRET={client_key}\n' + 'SPOTIFY_REDIRECT_URI=http://localhost:8080/callback\n'
            #conf_file = open(file_conf, 'w')
            #conf_file.write(auth_file_contents)
            #conf_file.close()
            #blank_or_create()
        except:
            print('error while creating auth file, do you have proper permissions?')
            exit()
        spot_creds = tekore.config_from_file(file_conf)
        spot_token = auth.prompt_for_user_token(*spot_creds, scope=spotify_scopes)
        new_creds = (client_id, client_key, 'http://localhost:8080/callback', spot_token.refresh_token)

        #save spot refresh token to 4th element
        #re-save the auth token separately
        tekore.config_to_file(file_auth, new_creds)

            #creds.prompt(client_id, secret) #redirect uri not needed from user, will always be localhost:8080
            #write_to_conf.spoticli

    exit_code = SpotiCLI(token=spot_token).cmdloop()