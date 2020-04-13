from cli import SpotiCLI
from tekore import util, scope
#from tekore import Spotify, util, scope
import auth

if __name__ == '__main__':

    #spotify scope
    ##need to convert to tekore friendly format before we pass it along
    #scope = 'user-library-read user-library-modify user-read-currently-playing user-read-playback-state user-modify-playback-state user-read-recently-played playlist-read-private'

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