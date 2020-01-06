from spotipy import util

conf = util.credentials_from_environment()
app_token = util.request_client_token(*conf[:2])
user_token = util.prompt_for_user_token(*conf)

# Save the refresh token to avoid authenticating again
refresh_token = ...     # Load refresh token
user_token = util.refresh_user_token(*conf[:2], refresh_token)

cred = util.RefreshingCredentials(*conf)

# Client credentials flow
app_token = cred.request_client_token()

# Authorisation code flow
url = cred.user_authorisation_url()
code = ...  # Redirect user to login and retrieve code
user_token = cred.request_user_token(code)

# Reload a token
user_token = cred.refresh_user_token(refresh_token)