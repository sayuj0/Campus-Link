from flask import Flask
from flask_login import current_user
import os

# Set template and static folders to project root
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static'))

app = Flask('Schools Web App', template_folder=template_dir, static_folder=static_dir)
# app.secret_key = os.environ['SECRET_KEY']
app.secret_key = 'you will never know'

# db initialization
from flask_sqlalchemy import SQLAlchemy
# app.config changed to fix path issue on 10/02/2025 AG#
#Absolute path - do not use unless for development
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////workspaces/project-1-schools-404-not-found/instance/schools.db'
# Use Flask's instance_path for portable DB location
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.instance_path}/schools.db"
db = SQLAlchemy(app)

# models initialization
from app import models
with app.app_context(): 
    db.create_all()

# login manager #Modified 10/02/2025 AG#
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # endpoint for login view

from app.models import User

# user_loader callback
@login_manager.user_loader
def load_user(id: str): 
    """
    Given a user ID from the session, return the corresponding User instance.

    Args:
        id: The user identifier stored by Flask-Login. Often a string.

    Returns:
        The User object if found, otherwise None.
    """
    try: 
        return db.session.query(User).filter(User.id==id).one()
    except: 
        return None

