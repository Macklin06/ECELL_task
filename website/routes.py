from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from . import db
from .models import User, Admin, Team, Score, Announcement

views = Blueprint('views', __name__, template_folder='templates')


def login_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('views.login'))
        return func(*args, **kwargs)

    return wrapper


def admin_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin login required.', 'warning')
            return redirect(url_for('views.admin_login'))
        return func(*args, **kwargs)

    return wrapper


@views.route('/')
def home():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()
    # leaderboard: teams ordered by score
    leaderboard = db.session.query(Team).join(Score).order_by(Score.points.desc()).all()
    return render_template('home.html', announcements=announcements, leaderboard=leaderboard)


@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        full_name = request.form['full_name']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('views.register'))

        user = User(email=email, full_name=full_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Account created. Please log in.', 'success')
        return redirect(url_for('views.login'))

    return render_template('register.html')


@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            flash('Logged in successfully.', 'success')
            return redirect(url_for('views.dashboard'))
        flash('Invalid credentials.', 'danger')

    return render_template('login.html')


@views.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('views.home'))


@views.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    # get user's teams and announcements
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('user_dashboard.html', user=user, announcements=announcements)


@views.route('/team/create', methods=['GET', 'POST'])
@login_required
def create_team():
    if request.method == 'POST':
        name = request.form['name']
        if Team.query.filter_by(name=name).first():
            flash('Team name already exists.', 'danger')
            return redirect(url_for('views.create_team'))

        leader = User.query.get(session['user_id'])
        team = Team(name=name, leader_id=leader.id)
        team.members.append(leader)
        db.session.add(team)
        db.session.commit()
        # create score row
        sc = Score(team_id=team.id, points=0)
        db.session.add(sc)
        db.session.commit()
        flash('Team created.', 'success')
        return redirect(url_for('views.team_view', team_id=team.id))

    return render_template('create_team.html')


@views.route('/team/<int:team_id>')
@login_required
def team_view(team_id):
    team = Team.query.get_or_404(team_id)
    return render_template('team.html', team=team)


@views.route('/team/<int:team_id>/add_member', methods=['POST'])
@login_required
def add_member(team_id):
    team = Team.query.get_or_404(team_id)
    if team.leader_id != session['user_id']:
        flash('Only team leader can add members.', 'danger')
        return redirect(url_for('views.team_view', team_id=team_id))

    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('No user with that email.', 'warning')
        return redirect(url_for('views.team_view', team_id=team_id))

    if user in team.members:
        flash('User already in team.', 'info')
    else:
        team.members.append(user)
        db.session.commit()
        flash('Member added.', 'success')

    return redirect(url_for('views.team_view', team_id=team_id))


@views.route('/leaderboard')
def leaderboard():
    teams = db.session.query(Team).join(Score).order_by(Score.points.desc()).all()
    return render_template('leaderboard.html', teams=teams)


@views.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session.clear()
            session['admin_id'] = admin.id
            flash('Admin logged in.', 'success')
            return redirect(url_for('views.admin_dashboard'))
        flash('Invalid admin credentials.', 'danger')

    return render_template('admin_login.html')


@views.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    flash('Admin logged out.', 'info')
    return redirect(url_for('views.home'))


@views.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    teams = Team.query.all()
    users = User.query.all()
    return render_template('admin_dashboard.html', announcements=announcements, teams=teams, users=users)


@views.route('/admin/announce', methods=['POST'])
@admin_required
def admin_announce():
    title = request.form.get('title')
    body = request.form.get('body')
    if not title or not body:
        flash('Title and body required.', 'warning')
        return redirect(url_for('views.admin_dashboard'))

    ann = Announcement(title=title, body=body)
    db.session.add(ann)
    db.session.commit()
    flash('Announcement posted.', 'success')
    return redirect(url_for('views.admin_dashboard'))


@views.route('/admin/update_score', methods=['POST'])
@admin_required
def admin_update_score():
    team_id = request.form.get('team_id')
    points = request.form.get('points')
    try:
        points = int(points)
    except Exception:
        flash('Invalid points value.', 'danger')
        return redirect(url_for('views.admin_dashboard'))

    team = Team.query.get(team_id)
    if not team:
        flash('Team not found.', 'warning')
        return redirect(url_for('views.admin_dashboard'))

    if not team.score:
        sc = Score(team_id=team.id, points=points)
        db.session.add(sc)
    else:
        team.score.points = points

    db.session.commit()
    flash('Score updated.', 'success')
    return redirect(url_for('views.admin_dashboard'))


@views.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)