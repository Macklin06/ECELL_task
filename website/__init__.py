from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # define it here globally

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'thisissecret'
    # use hackathon DB
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hackathon.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .routes import views
    app.register_blueprint(views, url_prefix='/')

    return app