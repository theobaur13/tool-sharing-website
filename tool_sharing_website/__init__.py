import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_redmail import RedMail
from keys import stripe_api_key, stripe_public_key, config_secret_key, email_host, email_port, email_user, email_password
import stripe

#App
app = Flask(__name__)
app.config['SECRET_KEY'] = config_secret_key
app.config['STRIPE_PUBLIC_KEY'] = stripe_public_key
stripe.api_key = stripe_api_key

#Database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
db = SQLAlchemy(app)

#Login
login_manager = LoginManager()
login_manager.init_app(app)

#Image upload
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/img')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

#Emailer
app.config["EMAIL_HOST"] = email_host
app.config["EMAIL_PORT"] = email_port
app.config['EMAIL_USER'] = email_user
app.config['EMAIL_PASSWORD'] = email_password
class Mailer():
    def __init__(self):
        self.sender = RedMail(app)

    
    def send_html(self, to, html, subject):
        self.sender.send(
            subject=subject,
            receivers=[to],
            html=html
        )

mailer = Mailer()

from tool_sharing_website import routes