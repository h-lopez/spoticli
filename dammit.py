from spotipy import Spotify
from spotipy.scope import every
from spotipy.sender import PersistentSender
from spotipy.util import prompt_for_user_token

client_id = 'ad61a493657140c8a663f8db17730c4f'
client_secret = '3c403975a6874b238339db2231864294'
redirect_uri = 'http://localhost'

token = prompt_for_user_token(
    client_id,
    client_secret,
    redirect_uri,
    scope=every
)


s = Spotify(token=token, sender=PersistentSender())
print(s)

tracks = s.current_user_top_tracks(limit=10)
for track in tracks.items:
    print(track.name)