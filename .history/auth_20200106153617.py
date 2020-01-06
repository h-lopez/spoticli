from spotipy import util

#conf = util.credentials_from_environment()
conf = (client_id_var, client_secret_var, redirect_uri_var)
app_token = util.request_client_token(*conf[:2])
user_token = util.prompt_for_user_token(*conf)

# Save the refresh token to avoid authenticating again
refresh_token = ...     # Load refresh token
user_token = util.refresh_user_token(*conf[:2], refresh_token)
