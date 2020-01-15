from flask import Flask, request, redirect, session

from tekore import Spotify, Credentials
from tekore.util import config_from_file
from tekore.scope import every

conf = config_from_file('conf.spoticli')
cred = Credentials(*conf)
spotify = Spotify()

users = {}

def app_factory() -> Flask:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'aliens'
    user_token_id = ''

    @app.route('/', methods=['GET'])
    def main():
        auth_url = cred.user_authorisation_url(scope=every)
        return redirect(auth_url, 307)

    @app.route('/callback', methods=['GET'])
    def login_callback():
        code = request.args.get('code', None)

        token = cred.request_user_token(code)
        with spotify.token_as(token):
            info = spotify.current_user()

        print(f'token {token}')
        print(f'code {code}')
        print(f'info {info}')
        print('this is eval')

        session['user'] = info.id
        users[info.id] = info

        user_token_id = info

        if(info):
            return redirect('/success', 307)
        return redirect('/fail', 307)

    @app.route('/success', methods=['GET'])
    def success():
        return 'authentication successful. you can close this window.'

    @app.route('/fail', methods=['GET'])
    def fail():
        return 'authentication unsuccessful. check your login creds and try again.'
        
    return app


if __name__ == '__main__':
    application = app_factory()
    application.run('localhost', 8080)