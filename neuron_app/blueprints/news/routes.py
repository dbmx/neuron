import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from werkzeug.utils import secure_filename
from neuron_app import db
from ...models import News, Page, Comment
from ...forms import NewsForm, CommentForm
from slugify import slugify
from neuron_app import uploaded_images
from itertools import groupby
from flask_login import current_user

news_bp = Blueprint('news', __name__)


#URL /news/
@news_bp.route('/news/')
def show_news():
    pages = Page.query.all()
    page = request.args.get('page', 1, type=int)
    news_items = News.query.order_by(News.created_at.desc()).paginate(page=page, per_page=25)

    # Grupisanje novosti po mesecu i godini
    grouped_news = {}
    for item in news_items.items:
        if item.created_at:
            year_month = item.created_at.strftime('%Y-%m')
            if year_month not in grouped_news:
                grouped_news[year_month] = []
            grouped_news[year_month].append(item)

    return render_template('news.html', grouped_news=grouped_news, news_items=news_items, pages=pages)



#URL /news/add_news/
@news_bp.route('/add_news', methods=['GET', 'POST'])
def add_news():
    pages = Page.query.all()
    form = NewsForm()
    if form.validate_on_submit():
        news = News(title=form.title.data, content=form.content.data)
        news.slug = slugify(form.title.data)
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            image_path = os.path.join(current_app.root_path, 'static/images', filename)
            form.image.data.save(image_path)
            news.featured_image = filename
        db.session.add(news)
        db.session.commit()
        flash('News added successfully!')
        return redirect(url_for('main.home'))
    return render_template('_addnews.html', form=form, pages=pages)


@news_bp.route('/n/<string:news_slug>')
def news_detail(news_slug):
    pages = Page.query.all()
    news_item = News.query.filter_by(slug=news_slug).first_or_404()
    
    # Inkrementiranje broja klikova
    news_item.click_count = news_item.click_count + 1 if news_item.click_count else 1
    db.session.commit()
    
    return render_template('single_news.html', news_item=news_item, pages=pages)



@news_bp.route('/edit_news/<string:news_slug>', methods=['GET', 'POST'])
def edit_news(news_slug):
    news = News.query.filter_by(slug=news_slug).first_or_404()
    form = NewsForm(obj=news)
    pages = Page.query.all()
    if form.validate_on_submit():
        news.title = form.title.data
        news.content = form.content.data

        # Ažuriranje slike
        if form.image.data:
            if news.featured_image:
                os.remove(os.path.join(current_app.root_path, 'static/images', news.featured_image))
            
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(current_app.root_path, 'static/images', filename))
            news.featured_image = filename

        db.session.commit()
        flash('News Updated Successfully!', 'success')
        # Preusmeravanje ili renderovanje stranice
        return redirect(url_for('news.news_detail', news_slug=news_slug))

    return render_template('_editnews.html', form=form, news=news, pages=pages)



#URL /news/delete_news/<int:news_id>
@news_bp.route('/delete_news/<int:news_id>', methods=['POST'])
def delete_news(news_id):
    news = News.query.get_or_404(news_id)
    Comment.query.filter_by(news_id=news.id).delete()
    db.session.delete(news)
    db.session.commit()
    flash('News Deleted Successfully!', 'success')
    return redirect(url_for('main.home'))


@news_bp.route('/increment_click/<int:news_id>', methods=['POST'])
def increment_click(news_id):
    news_item = News.query.get_or_404(news_id)
    news_item.click_count += 1
    db.session.commit()
    return jsonify({'click_count': news_item.click_count})





#KOMENTARI
@news_bp.route('/add_comment/<int:news_id>', methods=['POST'])
def add_comment(news_id):
    form = CommentForm()
    news_item = News.query.get_or_404(news_id)
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, news_id=news_id, user_id=current_user.id)
        db.session.add(comment)
        db.session.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'status': 'success',
                'message': 'Komentar je uspešno dodat.',
                'comment_html': render_template('_comment.html', comment=comment)
            })
        else:
            flash('Komentar je uspešno dodat.')
            return redirect(url_for('main.home'))  # Ili neka druga odgovarajuća ruta

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'error', 'message': 'Greška u formi.'})
    return render_template('_addcomment.html', form=form, news_item=news_item)




@news_bp.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user.id != comment.author.id and not current_user.is_admin:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Nemate dozvolu za brisanje ovog komentara.'})
        else:
            flash('Nemate dozvolu za brisanje ovog komentara.')
            return redirect(url_for('main.home'))
    
    db.session.delete(comment)
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'success', 'message': 'Komentar je uspešno obrisan.'})
    else:
        flash('Komentar je uspešno obrisan.')
        return redirect(url_for('main.home'))  # Preusmerite na odgovarajuću stranicu
