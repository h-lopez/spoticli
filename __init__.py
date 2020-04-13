from cli import SpotiCLI
from tekore import Spotify, util, scope
import auth

if __name__ == '__main__':
    cred = util.config_from_file('conf.spoticli')
    token = auth.prompt_for_user_token(*cred, scope=scope.every)
    print(token)

    #print(spotify.curre)

    #racks = spotify.current_user_top_tracks(limit=10)
    #potify.playback_start_tracks([t.id for t in tracks.items])

    ### auth user
    ### pass along auth token to spoticli
    ### spoticli will handle auth user and periodically refresh token as needed
    SpotiCLI().cmdloop()