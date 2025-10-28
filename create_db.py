from website import create_app, db
from website.models import User, Admin, Team, Score, Announcement

app = create_app()

with app.app_context():
    db.create_all()

    # create default admin if not exists
    if not Admin.query.first():
        admin = Admin(username="admin")
        admin.set_password("admin123")
        db.session.add(admin)

    # sample users
    if not User.query.filter_by(email='alice@example.com').first():
        u1 = User(email='alice@example.com', full_name='Alice')
        u1.set_password('password')
        db.session.add(u1)

    if not User.query.filter_by(email='bob@example.com').first():
        u2 = User(email='bob@example.com', full_name='Bob')
        u2.set_password('password')
        db.session.add(u2)

    db.session.commit()

    # sample team
    if not Team.query.filter_by(name='Team Alpha').first():
        leader = User.query.filter_by(email='alice@example.com').first()
        team = Team(name='Team Alpha', leader_id=leader.id)
        team.members.append(leader)
        db.session.add(team)
        db.session.commit()

        sc = Score(team_id=team.id, points=50)
        db.session.add(sc)

    # sample announcement
    if not Announcement.query.first():
        ann = Announcement(title='Welcome', body='Welcome to the Hackathon!')
        db.session.add(ann)

    db.session.commit()

    print('Database created/seeded.')