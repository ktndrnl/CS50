from datetime import datetime, timedelta

from flask import redirect, url_for, flash
from flask_login import current_user, login_required

from app import db
from app.twitch import bp
from app.twitch.api import TwitchAPI


@login_required
@bp.route('/update')
def update():
    if current_user.last_api_update is not None and \
            datetime.utcnow() - current_user.last_api_update < timedelta(minutes=5):
        flash(
            'Please wait'
            f' {(timedelta(minutes=5) - (datetime.utcnow() - current_user.last_api_update)).seconds}'
            ' seconds before refreshing again.')
    else:
        current_user.last_api_update = datetime.utcnow()
        api = TwitchAPI(current_user)
        if api.check_auth():
            api.update_user_follows()
            api.update_followed_videos()
            db.session.commit()
            flash('VODs updated')
        else:
            flash('OAuth Token invalid. Did you disconnect from Twitch?')
            return redirect(url_for('auth.logout'))
    return redirect(url_for('main.index'))
