from tekore import Spotify, util
from tekore.scope import every
from tekore.sender import PersistentSender

conf = util.config_from_file('conf.spoticli')
token = util.prompt_for_user_token(*conf, scope=every)
s = Spotify(token=token, sender=PersistentSender())

print(s.current_user())
#print(s)

#refresh_token = ...
#token = util.refresh_user_token(*conf[:2], refresh_token)