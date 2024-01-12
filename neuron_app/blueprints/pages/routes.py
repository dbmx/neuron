#blueprints/pages/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from neuron_app import db
from ...models import Page
from ...forms import PageForm

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/p/<page_name>')
def show_page(page_name):
    page = Page.query.filter_by(title=page_name).first()
    pages = Page.query.all()  # Query to get all pages

    return render_template('page.html', page=page, pages=pages)

@pages_bp.route('/add_page', methods=['GET', 'POST'])
def add_page():
    pages = Page.query.all()  # Query to get all pages

    form = PageForm()
    if form.validate_on_submit():
        is_header = form.is_header.data  # Check if the page should be marked as a header
        page = Page(title=form.title.data, content=form.content.data, is_header=is_header)
        db.session.add(page)
        db.session.commit()
        return redirect(url_for('pages.show_page', page_name=page.title))
    return render_template('_addpage.html', form=form, pages=pages)



@pages_bp.route('/edit_page/<page_title>', methods=['GET', 'POST'])
def edit_page(page_title):
    pages = Page.query.all()  # Query to get all pages

    page = Page.query.filter_by(title=page_title).first_or_404()
    form = PageForm(obj=page)

    if form.validate_on_submit():
        page.title = form.title.data
        page.content = form.content.data
        
        # Dodajte sledeći blok koda da označite stranicu kao zaglavlje (header)
        is_header = form.is_header.data
        page.is_header = is_header

        db.session.commit()
        flash('Page updated successfully!', 'success')
        return redirect(url_for('pages.show_page', page_name=page.title))

    return render_template('_editpage.html', form=form, page=page, pages=pages)



@pages_bp.route('/delete_page/<page_title>', methods=['POST', 'GET'])
def delete_page(page_title):
    
    page = Page.query.filter_by(title=page_title).first_or_404()
    db.session.delete(page)
    db.session.commit()
    flash('Page deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))