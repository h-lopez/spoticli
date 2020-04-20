## import auth library for authentication
import auth
import os

from cli import SpotiCLI
from tekore import util, scope
from os.path import expanduser

if __name__ == '__main__':

    #spotify scope
    ##need to convert to tekore friendly format before we pass it along
    #scope = 'user-library-read user-library-modify user-read-currently-playing user-read-playback-state user-modify-playback-state user-read-recently-played playlist-read-private'
    user_home = expanduser('~')

    #slash_type = user_home.endswith

    spotify_scopes = (  
        scope.scopes.user_library_read +
        scope.scopes.user_library_modify +
        scope.scopes.user_read_currently_playing +
        scope.scopes.user_read_playback_state +
        scope.scopes.user_modify_playback_state +
        scope.scopes.user_read_recently_played +
        scope.scopes.playlist_read_private
        )
    

    os.chdir(expanduser('~'))
    try:
        os.chdir('.config/spoticli')
    except:
        try:
            os.makedirs('.config/spoticli')
            os.chdir('.config/spoticli')
        except:
            ('failed to create directory, do you have write access?')
            exit()

    dir = os.getcwd()

    try:
        auth_file = open('.config')

    if(cached_token_exists):
        token = cached_token
        ##skip directly to authentication portion
    elif(conf_exists):
        exist = check_if_exists()
        valid = check_if_valid()

        if(not valid or not exist): #if file invalid (ie. unreadable) or doesn't exist
            client_id = input('input client id: \n')
            client_key = input('input client secret: \n')

            #quick sanity check to make sure secret and id are same length and are 32 characters long
            if(len(client_id) != len(client_key) or (len(client_id) != 32)):
                print('invalid id or secret')
                exit()
            try:
                pass
                print('valid!')
                #blank_or_create()
            except:
                print ('')

            #creds.prompt(client_id, secret) #redirect uri not needed from user, will always be localhost:8080
            #write_to_conf.spoticli   

    ##load local creds
    ##retrieve token using local creds
    cred = util.config_from_file('conf.spoticli')
    token = auth.prompt_for_user_token(*cred, scope=spotify_scopes)
    #### spotify = Spotify(token)
    #### tracks = spotify.current_user_top_tracks(limit=10)
    #### print(tracks)
    ### pass token to spoticli, spoticli with instantiate spotify object and handle refreshing
    ### spoticli will handle auth user and periodically refresh token as needed

    #if auth failed and returned a null token, exit program
    if (token is None):
        exit()
    
    SpotiCLI(token=token).cmdloop()