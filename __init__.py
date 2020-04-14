from cli import SpotiCLI
from tekore import util, scope
#from tekore import Spotify, util, scope
import auth

if __name__ == '__main__':

    #spotify scope
    ##need to convert to tekore friendly format before we pass it along
    #scope = 'user-library-read user-library-modify user-read-currently-playing user-read-playback-state user-modify-playback-state user-read-recently-played playlist-read-private'

    ### procedure
    '''
    if (cached_token_exists)
        token = cached_token
        ##skip directly to authentication portion
    check if conf file exists...

        exist = check_if_exists()
        valid = check_if_valid()

        if(!valid || !exist) #if file invalid (ie. unreadable) or doesn't exist
            try:
                blank/create it
            except:
                print error and exit program

            creds.prompt(client_id, secret) #redirect uri not needed from user, will always be localhost:8080
            write to conf.spoticli in user directory

    
    '''
    
    ##load local creds
    ##retrieve token using local creds
    cred = util.config_from_file('conf.spoticli')
    token = auth.prompt_for_user_token(*cred, scope=scope.every)
    #### spotify = Spotify(token)
    #### tracks = spotify.current_user_top_tracks(limit=10)
    #### print(tracks)
    ### pass token to spoticli, spoticli with instantiate spotify object and handle refreshing
    ### spoticli will handle auth user and periodically refresh token as needed
    SpotiCLI(token=token).cmdloop()