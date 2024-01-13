from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from ...models import User, News, Page, Visit
from ...forms import EditUserForm
from ... import db
from sqlalchemy import func
from datetime import datetime, timedelta



admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def dashboard():
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", 'danger')
        return redirect(url_for('main.home'))  # Preusmerite na neki drugi odgovarajući endpoint

    users = User.query.all()
    news_items = News.query.all()
    pages = Page.query.all()
    return render_template('/admin/dashboard.html', users=users, news_items=news_items, pages=pages)


@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required  # Optional: if you want to make this route accessible only by logged-in users
def edit_user(user_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", 'danger')
        return redirect(url_for('main.home'))  # Preusmerite na neki drugi odgovarajući endpoint
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data  # Update the is_admin field
        db.session.commit()
        flash('User details updated successfully.', 'success')
        return redirect(url_for('admin.dashboard'))  # Ensure this is the correct endpoint
    return render_template('_edituser.html', form=form, title='Edit User')



@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", 'danger')
        return redirect(url_for('main.home'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User and their comments deleted Successfully.', 'success')
    return redirect(url_for('admin.dashboard'))



# VISITS Data - RECORD
def record_visit():
    # Proveri da li postoji pregled za trenutni datum i IP adresu
    today = datetime.utcnow().date()
    user_ip = request.remote_addr  # Dobijanje IP adrese korisnika
    visit = Visit.query.filter_by(date=today, ip_address=user_ip).first()

    # Proveri da li je prošlo više od 5 minuta od poslednjeg pregleda
    if visit and (datetime.utcnow() - visit.last_updated).total_seconds() < 300:
        # Ako nije prošlo dovoljno vremena, nemoj dodavati pregled
        return

    # Ako ne postoji pregled za trenutni datum ili IP adresu ili je prošlo dovoljno vremena,
    # dodaj ili ažuriraj pregled
    if visit:
        visit.visits += 1
        visit.last_updated = datetime.utcnow()
    else:
        visit = Visit(visits=1, date=today, last_updated=datetime.utcnow(), ip_address=user_ip)
        db.session.add(visit)

    try:
        db.session.commit()
    except IntegrityError:
        # U slučaju da se dogodi IntegrityError (duplikat IP adrese za isti datum),
        # možete dodati logiku za rukovanje ovim slučajem ili jednostavno ignorisati grešku.
        db.session.rollback()


#VISITS DATA
@admin_bp.route('/admin/visits-data')
@login_required  # Assuming you want this route to be accessible only to logged-in users
def visits_data():
    today = datetime.utcnow().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    # Aggregate daily visits
    daily_visits_data = Visit.query.with_entities(
        func.date(Visit.date).label('date'),
        func.sum(Visit.visits).label('visits')
    ).filter(func.date(Visit.date) == today).group_by(func.date(Visit.date)).all()

    # Aggregate weekly visits
    weekly_visits_data = Visit.query.with_entities(
        func.date(Visit.date).label('date'),
        func.sum(Visit.visits).label('visits')
    ).filter(func.date(Visit.date) >= start_of_week).group_by(func.date(Visit.date)).all()

    # Aggregate monthly visits
    monthly_visits_data = Visit.query.with_entities(
        func.date(Visit.date).label('date'),
        func.sum(Visit.visits).label('visits')
    ).filter(func.date(Visit.date) >= start_of_month).group_by(func.date(Visit.date)).all()

    # Assuming daily_visits_data, weekly_visits_data, and monthly_visits_data are already defined
    daily_visits = [{'date': visit.date, 'visits': visit.visits} for visit in daily_visits_data]
    weekly_visits = [{'date': visit.date, 'visits': visit.visits} for visit in weekly_visits_data]
    monthly_visits = [{'date': visit.date, 'visits': visit.visits} for visit in monthly_visits_data]

    return jsonify({
        'daily_visits': daily_visits,
        'weekly_visits': weekly_visits,
        'monthly_visits': monthly_visits
    })


