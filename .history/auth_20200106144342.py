from spotipy import Spotify, util
from spotipy.scope import every
from spotipy.sender import PersistentSender

conf = util.credentials_from_environment()
token = util.prompt_for_user_token(*conf, scope=every)
s = Spotify(token=token, sender=PersistentSender())

user = s.current_user()

refresh_token = ...
token = util.refresh_user_token(*conf, refresh_token)
