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

    @app.route('/callback', methods=['GET'])
    def login_callback():
        code = request.args.get('code', None)

        token = cred.request_user_token(code)
        with spotify.token_as(token):
            info = spotify.current_user()

        print(token)
        print(code)
        print(info)
        print('this is eval')

        session['user'] = info.id
        users[info.id] = info

        return redirect('/', 307)

    @app.route('/logout', methods=['GET'])
    def logout():
        uid = session.pop('user', None)
        if uid is not None:
            users.pop(uid, None)
        return redirect('/', 307)

    return app


if __name__ == '__main__':
    application = app_factory()
    application.run('localhost', 8080)