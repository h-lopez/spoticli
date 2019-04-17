import json
from datetime import datetime, timedelta

token_data = open('.spotipyoauthcache', 'r').read()
token_expiration = json.loads(token_data)['expires_at']
current_time = int(datetime.now().timestamp())
print(token_expiration)
print(current_time)
print(current_time > token_expiration)