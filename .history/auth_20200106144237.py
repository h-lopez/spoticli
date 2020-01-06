import spotipy.util

conf = spotipy.util.credentials_from_environment()
app_token = spotipy.util.request_client_token(*conf[:2])
user_token = spotipy.util.prompt_for_user_token(*conf)

refresh_token = ...     # Load refresh token
user_token = util.refresh_user_token(*conf[:2], refresh_token)
