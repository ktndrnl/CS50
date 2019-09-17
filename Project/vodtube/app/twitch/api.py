from datetime import datetime, timedelta

import json

from flask import current_app
from rauth import OAuth2Service

from app import db
from app.models import User, Channel, Video


def decode_json(payload):
    return json.loads(payload.decode('utf-8'))


class TwitchAPI(object):
    def __init__(self, user):
        """

        :type user: User
        """
        self.service = OAuth2Service(
            name='twitch',
            client_id=current_app.config['TWITCH_CLIENT_ID'],
            client_secret=current_app.config['TWITCH_CLIENT_SECRET'],
            authorize_url='https://id.twitch.tv/oauth2/authorize',
            access_token_url='https://id.twitch.tv/oauth2/token',
            base_url='https://api.twitch.tv/helix/',
        )
        self.user = user
        if datetime.utcnow() - timedelta(minutes=5) > self.user.access_token_expiration:
            self.refresh_token()

        self.session = self.service.get_session(self.user.access_token)

    def check_auth(self):
        status_code = self.session.get(f'users?id={self.user.twitch_id}').status_code
        return status_code != 401

    def refresh_token(self):
        data = {'client_id': self.service.client_id,
                'client_secret': self.service.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': self.user.refresh_token}
        token_response = json.loads(self.service.get_raw_access_token(data=data).text)
        self.user.update_user(token_response)
        db.session.commit()

    def get_followed_channels(self):
        response: dict = self.session.get(f'users/follows?from_id={self.user.twitch_id}&first=100',
                                          params={'format': 'json'}).json()
        follows = []
        follows.extend(response["data"])

        while len(response["data"]) >= 100:
            response = self.session.get(
                f'users/follows?from_id={self.user.twitch_id}'
                f'&first=100'
                f'&after={response["pagination"]["cursor"]}',
                params={'format': 'json'}).json()
            follows.extend(response["data"])

        followed_channels = []
        for chunk in [follows[i * 100:(i+1) * 100] for i in range((len(follows) * 100 - 1) // 100)]:
            ids = [f['to_id'] for f in chunk]
            if len(ids) == 0:
                break
            url = f'users?id={"&id=".join(ids)}'
            response = self.session.get(url, params={'format': 'json'}).json()
            followed_channels.extend(response["data"])
        return followed_channels

    def get_followed_videos(self):
        videos = []
        follows = self.user.follows.all()

        for follow in follows:
            response: dict = self.session.get(f'videos?user_id={follow.id}'
                                              '&type=archive',
                                              params={'format': 'json'}).json()

            if len(response['data']) == 0:
                continue

            channel_videos = []
            channel_videos.extend(response["data"])

            video = Video.query.get(response['data'][-1]['id'])
            if video is not None and video.created_at < datetime.utcnow() - timedelta(days=1):
                videos.extend(channel_videos)
                continue

            while True:
                response = self.session.get(f'videos?user_id={follow.id}'
                                            '&first=100'
                                            '&type=archive'
                                            f'&after={response["pagination"]["cursor"]}',
                                            params={'format': 'json'}).json()

                channel_videos.extend(response["data"])

                if len(response['data']) < 100:
                    break

                video = Video.query.get(response['data'][-1]['id'])
                if video is not None and video.created_at < datetime.utcnow() - timedelta(days=1):
                    break

            videos.extend(channel_videos)

        videos.sort(key=lambda item:item["created_at"], reverse=True)
        return videos

    def update_user_follows(self):
        channels = self.get_followed_channels()
        for channel in channels:
            result = Channel.query.get(channel['id'])
            if not result:
                result = Channel()
                result.update_channel(channel, new_channel=True)
                db.session.add(result)
            else:
                result.update_channel(channel)
            self.user.follow(result)

        for followed_channel in self.user.follows.all():
            if followed_channel.id not in [int(channel['id']) for channel in channels]:
                self.user.unfollow(followed_channel)

        db.session.commit()

    def update_followed_videos(self):
        videos = self.get_followed_videos()
        for video in videos:
            result = Video.query.get(video['id'])
            if not result:
                result = Video()
                result.update_video(video, new_video=True)
                db.session.add(result)
            elif result.created_at > datetime.utcnow() - timedelta(days=1):
                result.update_video(video)
            else:
                break
        self.user.last_api_update = datetime.utcnow()
        db.session.commit()
