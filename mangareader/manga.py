import json
import math
from pathlib import Path
from typing import Optional, Dict, List, Any

from flask import Blueprint, Flask, send_from_directory, url_for, request, render_template, flash, send_file
from werkzeug.security import safe_join
from werkzeug.utils import secure_filename, redirect


# to consider later: https://github.com/un33k/python-slugify


bp = Blueprint('manga', __name__, url_prefix='/manga')


instance_path: Optional[Path] = None
media_dir_path: Optional[Path] = None


def init(app: Flask):
    global instance_path, media_dir_path
    instance_path = Path(app.instance_path)
    media_dir_path = Path(app.instance_path, 'media')


# Root
@bp.get('/')
def root():
    return "This is not the URL you're looking for", 404


# Favicon
@bp.get('/favicon.png')
def favicon():
    favicon_path = Path(instance_path, 'favicon.png')
    if favicon_path.is_file():
        return send_file(path_or_file=favicon_path, mimetype='image/png')
    return '', 404


# CSS
@bp.get('/style.css')
def main_css():
    return send_file(path_or_file=Path(instance_path, 'style.css'), mimetype='text/css')


# Media endpoint for serving static files
@bp.get('/media/<path:filename>', endpoint='media')
def manga_media(filename: str):
    return send_from_directory(directory=media_dir_path, path=filename)


# Rules just for building URLs to media files, the actual routing goes to the media endpoint
bp.add_url_rule('/media/<string:series>/<path:filename>', endpoint='media_series', build_only=True)
bp.add_url_rule('/media/<string:series><string:chapter>/<path:filename>', endpoint='media_chapter', build_only=True)


def load_manga_json(series_slug: str) -> Optional[Dict[str, Any]]:
    json_path = Path(media_dir_path, f'{series_slug}.json')
    if not json_path.is_file():
        return None
    with json_path.open(mode='rt', encoding='utf-8') as f:
        return json.load(f)


# Series page
@bp.get('/<string:series_slug>')
def view_series(series_slug: str):
    series_slug = secure_filename(series_slug)
    page = request.args.get('page', default=1, type=int)

    manga_json = load_manga_json(series_slug=series_slug)
    if manga_json is None:
        return redirect(url_for('.root'))

    title = manga_json['title']
    chapters: List[Dict[str, Any]] = manga_json['chapters']

    # Slice chapters for pagination
    page_size = 20      # constant for now
    page_count = max(1, math.ceil(len(chapters) / page_size))
    page = max(1, min(page_count, page))
    chapters = chapters[page_size * (page - 1):page_size * page]

    return render_template('series_view.html', series_slug=series_slug, series_title=title, page=page,
                           last_page=page_count, chapters=chapters)


# Chapter page
@bp.get('/<string:series_slug>/<string:chapter_slug>')
def view_chapter(series_slug: str, chapter_slug: str):
    series_slug = secure_filename(series_slug)
    chapter_slug = secure_filename(chapter_slug)

    manga_json = load_manga_json(series_slug=series_slug)
    if manga_json is None:
        return redirect(url_for('.root'))

    chapters = manga_json['chapters']
    chapter, ci = next(((c, i) for i, c in enumerate(chapters) if c['slug'] == chapter_slug), (None, None))
    if chapter is None:
        flash('chapter not found', category='error')
        return redirect(url_for('.view_series', series_slug=series_slug))

    prev_chapter_slug = chapters[ci - 1]['slug'] if ci > 0 else None
    next_chapter_slug = chapters[ci + 1]['slug'] if ci < len(chapters) - 1 else None

    return render_template('chapter_view.html', series=manga_json, chapter=chapter, contents=chapter['contents'],
                           prev_slug=prev_chapter_slug, next_slug=next_chapter_slug)
