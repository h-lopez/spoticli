from flask import Flask, request, redirect, session

from spotipy import Spotify, Credentials
from spotipy.util import credentials_from_environment
from spotipy.scope import every

client_id = 'ad61a493657140c8a663f8db17730c4f'
client_secret = '3c403975a6874b238339db2231864294'
redirect_uri = 'http://127.0.0.1:5000'

conf = credentials_from_environment()
conf = (client_id, client_secret, redirect_uri)
cred = Credentials(*conf)
spotify = Spotify()

users = {}


def app_factory() -> Flask:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'aliens'

    @app.route('/', methods=['GET'])
    def main():
        in_link = '<a href="/login">login</a>'
        out_link = '<a href="/logout">logout</a>'
        user = session.get('user', None)
        return f'User ID: {user}<br>You can {in_link} or {out_link}'

    @app.route('/login', methods=['GET'])
    def login():
        auth_url = cred.user_authorisation_url(scope=every)
        return redirect(auth_url, 307)
        #return auth_url

    @app.route('/callback', methods=['GET'])
    def login_callback():
        code = request.args.get('code', None)

        token = cred.request_user_token(code, scope=every)
        with spotify.token_as(token):
            info = spotify.current_user()
        session['user'] = info.id
        users[info.id] = info
        return redirect('/', 307)

    @app.route('/playing', methods=['GET'])
    def get_playing():
        return [spotify.current_user(), spotify.playback_currently_playing()]

    @app.route('/logout', methods=['GET'])
    def logout():
        uid = session.pop('user', None)
        if uid is not None:
            users.pop(uid, None)
        return redirect('/', 307)

    return app


if __name__ == '__main__':
    application = app_factory()
    application.run('127.0.0.1', 5000)