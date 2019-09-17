from datetime import datetime, timedelta

import json

from flask import current_app, redirect, url_for, request
from rauth import OAuth2Service


class TwitchSignIn(object):
    def __init__(self):
        self.service = OAuth2Service(
            name='twitch',
            client_id=current_app.config['TWITCH_CLIENT_ID'],
            client_secret=current_app.config['TWITCH_CLIENT_SECRET'],
            authorize_url='https://id.twitch.tv/oauth2/authorize',
            access_token_url='https://id.twitch.tv/oauth2/token',
            base_url='https://api.twitch.tv/helix/',
        )

    def authorize(self):
        #scope='user:read:email'
        return redirect(self.service.get_authorize_url(
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if 'code' not in request.args:
            return None, None

        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=decode_json
        )

        token_response = json.loads(oauth_session.access_token_response.content.decode('utf-8'))
        user_response = oauth_session.get('users').json()['data'][0]

        return user_response, token_response

    def get_callback_url(self):
        return url_for('auth.oauth_callback', _external=True)
