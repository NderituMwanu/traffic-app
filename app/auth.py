import os
from flask import Flask, Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from flask_wtf import FlaskForm
from .forms import PostForm
from .models import User, Post
from . import db
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask_login import login_required, current_user
from datetime import datetime


auth = Blueprint('auth', __name__)

app = Flask(__name__)

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL= True,
    MAIL_USERNAME = 'jisnderi@gmail.com',
    MAIL_PASSWORD = 'Kenyatta100@#',
))
mail = Mail(app)
mail.init_app(app)

s = URLSafeTimedSerializer('thisisasecret!')

@auth.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@auth.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.filter_by(id=post_id).one()
    return render_template('post.html', post=post)  


@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(username=username).first()

    if not user and not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)

    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['GET','POST'])
def signup_post():
    email = request.form.get('email')

    msg = Message('Welcome To Road Traffic Update!', sender="jisnderi@gmail.com", recipients=[email])
    msg.body = 'Thankyou For Signing up with Road Traffic Update, regards ~ RTF'

    mail.send(msg)

    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email address already exists.')
        return redirect(url_for('auth.signup'))

    new_user = User(email=email, username=username, password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()
    
    return redirect(url_for('auth.login'))



@auth.route("/new_post", methods=['GET', 'POST'])
@login_required
def new_post():
    
    form = PostForm()

    if form.validate_on_submit():
        post = Post(title=form.title.data,author=current_user)
        flash('Your post has been created')

        return redirect(url_for('auth.new_post'))

        db.session.add(post)
        db.session.commit()
        
    return render_template('create_post.html', title='New Post', form=form)



@auth.route("/addpost", methods=['POST'])
@login_required
def addpost():
    title = request.form['title']
    username = request.form['username']
    
    

    post = Post(title=title, username=username, date=datetime.now())
    db.session.add(post)
    db.session.commit()

    return redirect(url_for('main.index'))



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/profile')
@login_required
def profile():
    image_file = url_for('static', filename='profile_picture/' + current_user.image_file)
    return render_template('profile.html', title=profile, image_file=image_file)
