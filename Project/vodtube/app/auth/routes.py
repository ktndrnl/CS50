from flask import redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required

from app import db
from app.auth import bp
from app.models import User
from app.auth.oauth import TwitchSignIn
from app.twitch.api import TwitchAPI


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    oauth = TwitchSignIn()
    return oauth.authorize()


@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/callback')
def oauth_callback():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))

    oauth = TwitchSignIn()
    user_response, token_response = oauth.callback()

    if token_response is None:
        flash('You did not authorize the login request.')
        return redirect(url_for('main.index'))

    user = User.query.filter_by(twitch_id=user_response['id']).first()
    if not user:
        user = User()
        user.update_user(token_response, user_response, new_user=True)
        db.session.add(user)
        db.session.commit()
        api = TwitchAPI(user)
        api.update_user_follows()
        api.update_followed_videos()
    else:
        user.update_user(token_response, user_response)
    db.session.commit()

    login_user(user, True)
    return redirect(url_for('main.index'))
