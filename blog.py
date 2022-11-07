from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, LoginManager, UserMixin , current_user
from datetime import datetime
import os

base_dir = os.path.dirname(os.path.realpath(__file__))

db = SQLAlchemy()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, 'my_blog.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = '5e0b18fd5de07e49f80cb4f8'

db.init_app(app)
login_manager = LoginManager(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    firstname = db.Column(db.String(240), nullable= False, unique = False)
    lastname = db.Column(db.String(240), nullable= False, unique = False)
    username = db.Column(db.String(240), nullable=False, unique=True)
    email = db.Column(db.String(240), nullable=False, unique=True)
    password_hash = db.Column(db.Text(), nullable=False)


class Blog(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True,unique = True)
    title = db.Column(db.String(240), nullable=False, unique=False)
    content = db.Column(db.Text , nullable=False, unique=False)
    author = db.Column(db.String(50), nullable=False, unique=False)
    date_created = db.Column(db.DateTime)

    def __repr__(self):
        return f"User <{self.username}>"


with app.app_context():
    db.create_all()


@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))


@app.route('/')
def index():
    index = Blog.query.all()
    return render_template('index.html', index = index)


@app.route('/post', methods=['POST', 'GET'])
@login_required
def post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = current_user.username
        date_created = datetime.now()
        new_post = Blog(title=title, content=content, author=author, date_created=date_created)
        with app.app_context():
            db.session.add(new_post)
            db.session.commit()

        return redirect('/')

    return render_template('post.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        flash('login successful', category = 'success')
        return redirect(url_for('index'))



    return render_template('login.html')

        

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out', category='success')
    return redirect(url_for('index'))



@app.route('/protected')
@login_required
def protected():
    return render_template('protected.html')


@app.route('/About')
def About():
    return render_template('About.html')


@app.route('/ContactMe', methods = ['GET','POST'])
def Contact():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            message = request.form.get('message')
            priority = request.form.get('priority')

            flash('Successful', category=success)
            return redirect('/')

        return render_template('Contact.html')



@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already taken', category='error')
            return redirect(url_for('register'))


        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            flash('Email already assigned', category='error')
            return redirect(url_for('register'))



        password_hash = generate_password_hash(password)
        username_validation = User.query.filter_by(password_hash=password_hash)
        if len(password) < 6:
            flash('PASSWORD SHOULD NOT BE LESS THAN 6', category='error')
            return redirect(url_for('register'))

        new_user = User(firstname = firstname, lastname = lastname, username=username, email=email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()


        flash('Signup successful', category='success')


        return redirect(url_for('login'))


    return render_template('signup.html')



if __name__ == '__main__':
    app.run(debug=True)