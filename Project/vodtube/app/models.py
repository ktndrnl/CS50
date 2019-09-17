from datetime import datetime, timedelta
from dateutil import parser

from flask_login import UserMixin

from app import db, login


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('channel.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    twitch_id = db.Column(db.Integer, index=True, unique=True)
    twitch_name = db.Column(db.String(64), index=True)
    profile_image_url = db.Column(db.String(256))
    follows = db.relationship("Channel", secondary=followers, lazy='dynamic')
    email = db.Column(db.String(128), index=True)
    access_token = db.Column(db.String(128))
    access_token_expiration = db.Column(db.DateTime, index=True)
    refresh_token = db.Column(db.String(128))
    last_api_update = db.Column(db.DateTime, index=True)

    def avatar(self, size=70):
        """valid sizes are 70 and 380"""
        if size > 380:
            size = 380
        elif size < 380:
            size = 70

        return self.profile_image_url.replace("300x300.", f"{size}x{size}.")

    def update_user(self, token_response, user_response=None,
                    new_user=False):
        if user_response is not None:
            if new_user:
                self.twitch_id = user_response['id']
            self.twitch_name = user_response['display_name']
            self.profile_image_url = user_response['profile_image_url']

        self.access_token = token_response['access_token']
        self.access_token_expiration = datetime.utcnow() + timedelta(seconds=int(token_response['expires_in']))
        self.refresh_token = token_response['refresh_token']

    def follow(self, channel):
        if not self.is_following(channel):
            self.follows.append(channel)

    def unfollow(self, channel):
        if self.is_following(channel):
            self.follows.remove(channel)

    def is_following(self, channel):
        return self.follows.filter(followers.c.followed_id == channel.id).count() > 0

    def followed_videos(self):
        followed = Video.query.join(
            followers, (followers.c.followed_id == Video.channel_id)).filter(
            followers.c.follower_id == self.id)
        return followed.order_by(Video.created_at.desc()).join(Channel)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_name = db.Column(db.String(64), index=True)
    display_name = db.Column(db.String(64), index=True)
    profile_image_url = db.Column(db.String(256))
    videos = db.relationship('Video', foreign_keys='Video.channel_id',
                             backref='channel', lazy='dynamic')

    def update_channel(self, channel_dict, new_channel=False):
        if new_channel:
            self.id = channel_dict['id']
        self.login_name = channel_dict['login']
        self.display_name = channel_dict['display_name']
        self.profile_image_url = channel_dict['profile_image_url']

    def avatar(self, size=70):
        """valid sizes are 70 and 380"""
        if size > 380:
            size = 380
        elif size < 380:
            size = 70

        return self.profile_image_url.replace("300x300.", f"{size}x{size}.")


class Video(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    title = db.Column(db.String(256))
    description = db.Column(db.String(256))
    created_at = db.Column(db.DateTime(), index=True)
    url = db.Column(db.String(256))
    thumbnail_url = db.Column(db.String(256))
    video_type = db.Column(db.String(16), index=True)
    duration = db.Column(db.String(16))

    def update_video(self, video_dict, new_video=False):
        if new_video:
            self.id = video_dict['id']
            self.channel_id = video_dict['user_id']
        self.title = video_dict['title']
        self.description = video_dict['description']
        self.created_at = parser.parse(video_dict['created_at'])
        self.url = video_dict['url']
        self.thumbnail_url = video_dict['thumbnail_url']
        self.video_type = video_dict['type']
        self.duration = video_dict['duration']
