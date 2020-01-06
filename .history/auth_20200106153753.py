from spotipy import util

#conf = util.credentials_from_environment()
#cliuent ID, secret, and callback url
conf = ("ad61a493657140c8a663f8db17730c4f", "3c403975a6874b238339db2231864294", "localhost")
app_token = util.request_client_token(*conf[:2])
user_token = util.prompt_for_user_token(*conf)

# Save the refresh token to avoid authenticating again
refresh_token = ...     # Load refresh token
user_token = util.refresh_user_token(*conf[:2], refresh_token)
