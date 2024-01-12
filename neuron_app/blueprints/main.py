from flask import Blueprint, render_template, request, redirect, url_for, flash
from neuron_app import db # Import from main directory
from ..models import News, Page
from ..forms import NewsForm, CommentForm 
import requests
from bs4 import BeautifulSoup
from flask_login import current_user




main_bp = Blueprint('main', __name__)


@main_bp.route('/home/load')
def load_news():
    news_items = News.query.all()
    return render_template('news_list.html', news_items=news_items)

@main_bp.route('/')
@main_bp.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    news_items = News.query.order_by(News.created_at.desc()).paginate(page=page, per_page=2)
    pages = Page.query.all()  # Query to get all pages
    forms = {news_item.id: CommentForm() for news_item in news_items.items}
    return render_template('home.html', news_items=news_items, pages=pages, forms=forms)



def get_latest_videos(channel_url):
    response = requests.get(channel_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    videos = []
    for video in soup.find_all('a', id='thumbnail'):
        video_link = video.get('href')
        if video_link and '/watch?v=' in video_link:
            video_id = video_link.split('/watch?v=')[1].split('&')[0]  # Izdvajanje video ID-a
            title = video.get('title')
            if title:
                videos.append({
                    'title': title,
                    'video_id': video_id
                })
    return videos


@main_bp.route('/videos')
def show_videos():
    channel_url = 'https://www.youtube.com/channel/UC1kGH2CKT0s2Xn2HlkT7HtQ/videos'  # Ispravite URL

    videos = get_latest_videos(channel_url)
    return render_template('videos.html', videos=videos)