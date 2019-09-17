from flask import render_template, redirect, url_for, request
from flask_login import current_user

from app.main import bp


@bp.route('/index', methods=['GET', 'POST'])
@bp.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        return render_template('welcome.html')

    page = request.args.get('page', 1, type=int)
    videos = current_user.followed_videos().paginate(
        page, 20, False
    )

    if page > videos.pages or page < 1:
        return redirect(url_for('main.index', page=max(1, min(page, videos.pages))))

    next_url = url_for('main.index', page=videos.next_num) \
        if videos.has_next else None
    prev_url = url_for('main.index', page=videos.prev_num) \
        if videos.has_prev else None
    return render_template('index.html', videos=videos.items, next_url=next_url, prev_url=prev_url, pages=videos,
                           title=f'Page {page}')
