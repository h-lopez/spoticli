from cli import SpotiCLI
from tekore import Spotify, util, scope
import auth

if __name__ == '__main__':

    ##load local creds
    ##retrieve token using local creds
    cred = util.config_from_file('conf.spoticli')
    token = auth.prompt_for_user_token(*cred, scope=scope.every)
    ### pass token to spoticli, spoticli with instantiate spotify object and handle refreshing
    ### spoticli will handle auth user and periodically refresh token as needed
    SpotiCLI().cmdloop()