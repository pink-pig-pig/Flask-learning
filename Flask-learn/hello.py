from flask import Flask, render_template, url_for, session, redirect, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
import os


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hard to guess string!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com>'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

bootstrap = Bootstrap(app)
moment    = Moment(app)
db        = SQLAlchemy(app)
migrate   = Migrate(app, db)
mail      = Mail(app)

class Role(db.Model):
    __tablename__ = 'roles'
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>'%(self.name)

class User(db.Model):
    __tablename__ = 'users'
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    role_id  = db.Column(db.Integer, db.ForeignKey('roles.id'))
    def __repr__(self):
        return '<user %r>'%(self.username)


class NameForm(FlaskForm):
    name   = StringField('what is your name', validators=[DataRequired()])
    submit = SubmitField('Submit')



@app.route('/', methods=['GET', 'POST'])
def formtest():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_mail(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True

        session['name'] = form.name.data
        form.name.data = ''

        return redirect(url_for('formtest'))
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))

@app.route('/user/<name>')
def index(name):
    return render_template('user.html', name=name)

@app.route('/showtime')
def showtime():
    return render_template('time.html', current_time=datetime.utcnow())

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
                                               
#添加一个集成Python shell

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, mail=mail, Message=Message)

def send_mail(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    mail.send(msg)

