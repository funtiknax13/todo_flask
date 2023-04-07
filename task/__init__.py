from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.secret_key = "jfhsadifh843rig3428u2u4hf9842t8528tht8h49th945ti90j53945jvj3596"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = LoginManager(app)
manager.login_view = 'login'


from task import models, routes

with app.app_context():
    db.create_all()
