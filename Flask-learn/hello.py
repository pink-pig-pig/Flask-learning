from flask import Flask, render_template, url_for, session, redirect, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hard to guess string!'

bootstrap = Bootstrap(app)
moment    = Moment(app)

class NameForm(FlaskForm):
    name   = StringField('what is your name', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def formtest():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash("Looks like you have change your name!")
        session['name'] = form.name.data

        return redirect(url_for('formtest'))
    return render_template('index.html', form=form, name=session.get('name'))
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
                                               