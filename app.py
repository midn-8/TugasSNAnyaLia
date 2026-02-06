import os
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b8777df836d909090510c5509a3634ef'
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'site.db')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    
    def __repr__(self):
        return f"User ('{self.username}', '{self.email}', '{self.image_file}')"
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"Post ('{self.title}', '{self.date_posted}')"
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
posts = [
    {
        'author': 'Aulia Eunike',
        'title': 'WHAT IS CYBER LAW',
        'content': 'cyber law adalah hukum yang mengatur...',
        'date_posted': 'April 20, 2026'
    },
    {
        'author': 'Daniel Pratama',
        'title': 'Kenapa Mahasiswa Cyber Security Perlu Mempelajari Cyber Law',
        'content': 'karena dipaksa',
        'date_posted': 'April 21, 2025'
    },
    {
        'author': 'Brillianto',
        'title': 'Menang Lomba Silat 2025',
        'content': 'My experience ikut World Martial Arts Cup',
        'date_posted': 'September 9, 2025'
    },
    {
        'author': 'Unknown',
        'title': '[LINK BOCORAN UTS SNA]',
        'content': 'diem diem aja yaaa',
        'date_posted': 'April 21, 2025'
    }
     
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {e}', 'danger')
            print(e)
    else:
        if request.method == "POST":
            print("Form did not validate. Errors:", form.errors)  # <-- Debug line
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Check email and password.', 'danger')
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route("/dashboard")
@login_required
def dashboard():
    return f"<h1>Dashboard</h1><p>Hello, {current_user.username}!</p>"

@app.route("/about")
def about():
    return render_template('about.html', title='About')

if __name__ == '__main__':
    with app.app_context():
    
        db.create_all()
        print("Database and tables are ready!")

        if not User.query.first():
            user = User(username='admin', email='admin@example.com',
                        password=generate_password_hash('password123', method='pbkdf2:sha256'))
            db.session.add(user)
            db.session.commit()
            print("Sample user created!")

        if not Post.query.first():
            post = Post(title='Hello World', content='This is the first post!', user_id=1)
            db.session.add(post)
            db.session.commit()
            print("Sample post created!")

    app.run(debug=True)
