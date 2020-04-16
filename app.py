import csv

import bcrypt
from flask import Flask, url_for, render_template, redirect, flash, session, request
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = 'allo'
login_manager = LoginManager()
login_manager.init_app(app)
# without setting the login_view, attempting to access @login_required endpoints will result in an error
# this way, it will redirect to the login page
login_manager.login_view = 'login'
app.config['USE_SESSION_FOR_NEXT'] = True


class User(UserMixin):
    def __init__(self, email, password=None):
        self.id = email
        self.email = email
        self.password = password


# this is used by flask_login to get a user object for the current user
@login_manager.user_loader
def load_user(user_id):
    user = find_user(user_id)
    # user could be None
    if user:
        # if not None, hide the password by setting it to None
        user.password = None
    return user


def find_user(email):
    with open('data/passwords.csv') as f:
        for user in csv.reader(f):
            if email == user[0]:
                return User(*user)
    return None


class ContactForm(FlaskForm):
    song = StringField('song', validators=[DataRequired("no one sang then?")])
    artist = StringField('artist', validators=[DataRequired("no one sang then?")])
    playlist = SelectField('playlist', validators=[DataRequired()])
    comment = TextAreaField('comment', validators=[DataRequired()])
    submit = SubmitField('Send')


class LoginForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    submit = SubmitField('Send')


class CommentForm(FlaskForm):
    comment = TextAreaField('comment', validators=[DataRequired])

class SongForm(FlaskForm):
    song = TextAreaField('song', validators=[DataRequired])
    artist = TextAreaField('artist', validators=[DataRequired])
    playlist = TextAreaField('playlist', validators=[DataRequired])


def check_password(email, password):
    with open('data/passwords.csv') as f:
        for user in csv.reader(f):
            if email == user[0] and password == user[1]:
                flash(user[0], user[1])
                return True
    return False


@app.route('/')
def index():
    form = LoginForm()
    return render_template('index.html',
                           index=url_for('index'),
                           songs=url_for('songs'),
                           blog=url_for('blog'),
                           about=url_for('about'),
                           suggest=url_for('suggest'),
                           form=form)


@app.route('/songs')
def songs():
    form = LoginForm()
    form1 = SongForm
    doclists = []
    with open('data/play.csv') as f:
        doclists = list(csv.reader(f))
    return render_template('songs.html',
                           index=url_for('index'),
                           songs=url_for('songs'),
                           blog=url_for('blog'),
                           about=url_for('about'),
                           suggest=url_for('suggest'),
                           form=form,
                           form1=form1,
                           doclists=doclists)


@app.route('/add_song', methods=['GET', 'POST'])
def add_song():
    form = SongForm()
    error = ''
    if request.method == 'POST':
        # Form being submitted; grab data from form.
        song = form.song.data
        artist = form.artist.data
        playlist = form.playlist.data

        # Validate form data
        if len(song) == 0:
            # Form data failed validation; try again
            error = "please add a song!"
            return redirect(url_for('songs'))
        else:
            with open('data/play.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(["message from blog: " + song])
        return render_template('songs.html',
                               index=url_for('index'),
                               songs=url_for('songs'),
                               blog=url_for('blog'),
                               about=url_for('about'),
                               suggest=url_for('suggest'),
                               form=form,
                               message=error)


@app.route('/blog')
def blog():
    form = LoginForm()
    form1 = CommentForm()
    form2 = CommentForm()
    return render_template('blog.html',
                           index=url_for('index'),
                           songs=url_for('songs'),
                           blog=url_for('blog'),
                           about=url_for('about'),
                           suggest=url_for('suggest'),
                           form=form,
                           form1=form1,
                           form2=form2)


@app.route('/blog_comment', methods=['GET', 'POST'])
def blog_comment():
    form = CommentForm()
    error = ''
    if request.method == 'POST':
        # Form being submitted; grab data from form.
        comment = form.comment.data

        # Validate form data
        if len(comment) == 0:
            # Form data failed validation; try again
            error = "please leave a comment!"
            return redirect(url_for('blog'))
        else:
            with open('data/messages.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(["message from blog: " + comment])
        return render_template('blog.html',
                               index=url_for('index'),
                               songs=url_for('songs'),
                               blog=url_for('blog'),
                               about=url_for('about'),
                               suggest=url_for('suggest'),
                               form=form,
                               message=error)


@app.route('/about')
def about():
    form = LoginForm()
    return render_template('about.html',
                           index=url_for('index'),
                           songs=url_for('songs'),
                           blog=url_for('blog'),
                           about=url_for('about'),
                           suggest=url_for('suggest'),
                           form=form)


@app.route('/suggest')
def suggest():
    form = ContactForm()
    return render_template('suggest.html',
                           index=url_for('index'),
                           songs=url_for('songs'),
                           blog=url_for('blog'),
                           about=url_for('about'),
                           suggest=url_for('suggest'),
                           form=form)


@app.route('/suggestform', methods=['GET', 'POST'])
def suggestform():
    # form = ContactForm()
    # if request.method == 'POST':
    #     if form.validate_on_submit():
    #         with open('data/messages.csv', 'a') as f:
    #             writer = csv.writer(f)
    #             writer.writerow([form.song.data, form.artist.data, form.playlist.data,
    #                              form.comment.data])
    #         return redirect(url_for('suggest'))
    # return render_template('suggest.html',
    #                        index=url_for('index'),
    #                        songs=url_for('songs'),
    #                        blog=url_for('blog'),
    #                        about=url_for('about'),
    #                        suggest=url_for('suggest'),
    #                        form=form)
    form = ContactForm()
    if request.method == 'POST':
        # Form being submitted; grab data from form.
        song = form.song.data
        artist = form.artist.data
        playlist = form.playlist.data
        comment = form.comment.data
        if len(comment) != 0 and len(artist) != 0 and len(playlist) != 0 and len(song) != 0:
            with open('data/messages.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["song recommendation: " + song + " by " + artist + ". put it in the playlist: " + playlist +
                     ". message: " + comment])
        return render_template('suggest.html',
                               index=url_for('index'),
                               songs=url_for('songs'),
                               blog=url_for('blog'),
                               about=url_for('about'),
                               suggest=url_for('suggest'),
                               form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    form = LoginForm()

    if form.validate_on_submit():
        user = find_user(form.email.data)
        # user could be None
        # passwords are kept in hashed form, using the bcrypt algorithm
        salt = bcrypt.gensalt()
        userpass = bcrypt.hashpw(user.password.encode(), salt)
        if user and bcrypt.checkpw(form.password.data.encode(), userpass):
            login_user(user)
            flash('Logged in successfully.')
            next_page = session.get('next', '/')
            session['next'] = '/'
            return redirect(next_page)
        else:
            flash('Incorrect email/password!')
            return redirect(url_for('index'))
        # Render the sign-up page
    return render_template('index.html',
                           index=url_for('index'),
                           songs=url_for('songs'),
                           blog=url_for('blog'),
                           about=url_for('about'),
                           suggest=url_for('suggest'),
                           form=form,
                           message=error)

# logout button
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run()
