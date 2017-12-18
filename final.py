import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, IntegerField, PasswordField, BooleanField, SelectMultipleField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from threading import Thread
from werkzeug import secure_filename
import requests
import json
import unittest
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364thisisnotsupersecure'

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/demgijsfinalproject"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SUBJECT_PREFIX'] = '[A Dog-a-Day App]'
app.config['MAIL_SENDER'] = 'Admin demgijs364@gmail.com'
app.config['ADMIN'] = os.environ.get('ADMIN') or 'demgijsi364@gmail.com'

manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
mail = Mail(app)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app) # set up login manager

def make_shell_context():
    return dict(app=app, db=db) 

manager.add_command("shell", Shell(make_context=make_shell_context))

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg]) 
    thr.start()
    return thr

user_collection = db.Table('user_collection',db.Column('user_id', db.Integer, db.ForeignKey('dogs.id')),db.Column('collection_id',db.Integer, db.ForeignKey('personalCollections.id')))
#Tweet_Mention = db.Table('Tweet_Mention', db.Column('tweet_id', db.Integer, db.ForeignKey('tweet.id')), db.Column('mention_id', db.Integer, db.ForeignKey('mention.id')))

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)#, index=True)
    email = db.Column(db.String(64), unique=True)#, index=True)
    #collection = db.relationship('PersonalCollection', backref='User')
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

class PersonalCollection(db.Model):
    __tablename__ = "personalCollections"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    dogs = db.relationship('Dogs',secondary=user_collection,backref=db.backref('personalCollections',lazy='dynamic'),lazy='dynamic')

#class User(db.Model): 
#	__tablename__ = "user"
#	id = db.Column(db.Integer, primary_key = True)
#	dod_username = db.Column(db.String(64), unique = True) 
#	email_address = db.Column(db.String(64), unique = True)

class Dogs(db.Model):
	__tablename__ = "dogs"
	id = db.Column(db.Integer, primary_key=True)
	pic_id = db.Column(db.Integer)
	breed = db.Column(db.String(64))

class Breed(db.Model):
	__tablename__ = "breed"
	id = db.Column(db.Integer, primary_key = True)
	dog_type = db.Column(db.String(64)) ##many to many - many breeds have many dogs
	pic_id = db.Column(db.Integer)
	#user = db.relationship('User', backref = "Mention")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class ProfileForm(FlaskForm):
	username = StringField("Enter your Dog-A-Day username (example 'iheartdogs33'):", validators = [Required()])
	email = StringField("Enter the email address to which you would like your dogs to be sent:", validators = [Required()])
	password = PasswordField('Enter a secure password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
	password2 = PasswordField("Confirm that password - typos happen:",validators=[Required()])
	submit = SubmitField('Sign me up!')

	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('That email is already registered for dog emails!')

	def validate_username(self,field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('Sorry - that username is already taken')

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[Required(), Length(1,64), Email()])
	username = StringField('Username', validators=[Required()])
	password = PasswordField('Password', validators=[Required()])
	remember_me = BooleanField('Keep me logged in')
	submit = SubmitField('Log In')

##Put get_or_create functions here
def get_or_create_users(db_session, username, email):
	users = db.session.query(User).filter_by(username = username).first()
	if users:
		return users
	else:
		users = User(username = username, email = email)
		db_session.add(users)
		db_session.commit()
		return users

def get_or_create_dogs(db_session, picture_num, breed):
	dogs = db.session.query(Tweet).filter_by(pic_id = picture_num).first()
	if dogs:
		return dogs
	else:
		dogs = Dogs(pic_id = picture_num, breed = breed)
		db.session.add(dogs)
		db.session.commit()
		return dogs

#def get_or_create_breed(db_session, choose_breed, picture_num):
#	breed = db.session.query(Breed).filter_by(choose_breed = dog_type).first()
#	if breed:
#		return breed
#	else:
#		breed = Breed(dog_type = choose_breed, pic_id = picture_num)
#		db_session.add(breed)
#		db_session.commit()
#		return breed

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
	return render_template('500.htm'), 500

# ROUTES FOR LOGGING IN/OUT
@app.route('/login',methods=["GET","POST"])
def login():
	form = LoginForm()
	#return "OK"
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		#return "OK"
		#if user is not None and user.verify_password(form.password.data):
			#login_user(user, form.remember_me.data)

		return redirect(request.args.get('next') or url_for('profile_form'))
			#flash('Invalid username or password.')
		return render_template('all_dogs.html',form=form, username = username)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('We logged you out.')
	return redirect(url_for('login'))

@app.route('/register',methods=["GET","POST"])
def register():
	form = ProfileForm()
	if form.validate_on_submit():
		user = User(email=form.email.data,username=form.username.data,password_hash=form.password.data)
		db.session.add(user)
		db.session.commit()
		flash("You've got a Dog-A-Day login account now!")
		return redirect(url_for('login'))
	return render_template('register.html',form=form)

@app.route('/secret')
@login_required
def secret():
	return "Only registered users can do this! Try to register or contact the site admin at demgijs364@gmail.com."


@app.route('/', methods = ['GET', 'POST'])
def profile_form():
	simpleForm = LoginForm()
	return render_template('index.html', form=simpleForm)
	#flash('All fields are required!')
	#return render_template('profile-form.html', form=simpleForm)


@app.route('/result/alldogs', methods = ['GET', 'POST'])
def index():
	#generate = Dogs.query.all()
	#dogs = []
	form = ProfileForm(request.form)
	#if request.method == "POST" and form.validate_on_submit():
	username = form.username.data
	email = form.email.data
	#	password = form.password.data
	result = request.args
	base_url = "https://dog.ceo/api/breeds"
	response = requests.get(base_url + '/image/random')
	print(response.text)
	data = json.loads(response.text)
	send_email(form.email.data, 'New Dog Pic', 'mail/new_dog', item = data['message'], username = username)
		
	return render_template('all_dogs.html', result = data["message"], username = username)
	return redirect(url_for('see_my_dogs'))
	#	return redirect(url_for(('index')))
	flash('All fields are required!')
		#base_url = 'https://dog.ceo/dog-api/breeds-image-random.php'
#to, subject, template, **kwargs		

@app.route('/my_dogs')
@login_required
def see_my_dogs():
	my_dogs = []
	dogs = Dogs.query.all()
	for d in dogs:
		user = Dogs.query.filter_by(my_dogs = my_dogs).first()
		my_dogs.append(d.my_dogs, user.username)
		return render_template('my_dogs.html', my_dogs = my_dogs)


class CodeTests(unittest.TestCase):
	def test1(self):
		self.assertEqual(type(my_dogs),type([]))

	def test2(self):
		self.assertEqual()


if __name__ == '__main__':
    db.create_all()
    manager.run()




