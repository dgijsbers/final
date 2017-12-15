import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, IntegerField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from threading import Thread
from werkzeug import secure_filename
import requests
import json

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364thisisnotsupersecure'

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/demgijsfinal"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SUBJECT_PREFIX'] = '[A Dog-a-Day App]'
app.config['MAIL_SENDER'] = 'demgijs364@gmail.com'
app.config['ADMIN'] = os.environ.get('ADMIN')

manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
mail = Mail(app)

def make_shell_context():
    return dict(app=app, db=db, User=User, Dogs=Dogs, Breed=Breed) 

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

#Tweet_Mention = db.Table('Tweet_Mention', db.Column('tweet_id', db.Integer, db.ForeignKey('tweet.id')), db.Column('mention_id', db.Integer, db.ForeignKey('mention.id')))


class User(db.Model): 
	__tablename__ = "user"
	id = db.Column(db.Integer, primary_key = True)
	dod_username = db.Column(db.String(64), unique = True) 
	email_address = db.Column(db.String(64), unique = True)

class Dogs(db.Model):
	__tablename__ = "dogs"
	id = db.Column(db.Integer, primary_key=True)
	pic_id = db.Column(db.Integer)

class Breed(db.Model):
	__tablename__ = "breed"
	id = db.Column(db.Integer, primary_key = True)
	dog_type = db.Column(db.String(64))
	pic_id = db.Column(db.Integer)
	#user = db.relationship('User', backref = "Mention")

class ProfileForm(FlaskForm):
	username = StringField("Enter your Dog-A-Day username (example 'iheartdogs33'):", validators = [Required()])
	choice = RadioField('Are you looking for pictures of all dogs or a certain breed?', choices=[('All Dogs!','All Dogs!'), ('A Breed!', 'A Breed!')])
	email = StringField("Enter the email address to which you would like your mention updates to be sent:", validators = [Required()])
	submit = SubmitField('Sign me up!')


##Put get_or_create functions here
def get_or_create_user(db_session, username, email):
	user = db.session.query(User).filter_by(dod_username = username).first()
	if user:
		return user
	else:
		user = User(dod_username = username, email_address = email)
		db_session.add(user)
		db_session.commit()
		return user

def get_or_create_dogs(db_session, picture_num):
	dogs = db.session.query(Tweet).filter_by(pic_id = picture_num).first()
	if dogs:
		return dogs
	else:
		dogs = Dogs(pic_id = picture_num)
		db.session.add(dogs)
		db.session.commit()
		return dogs

def get_or_create_breed(db_session, choose_breed, picture_num):
	breed = db.session.query(Breed).filter_by(choose_breed = dog_type).first()
	if breed:
		return breed
	else:
		breed = Breed(dog_type = choose_breed, pic_id = picture_num)
		db_session.add(breed)
		db_session.commit()
		return breed


@app.route('/', methods = ['GET', 'POST'])
def profile_form():
	simpleForm = ProfileForm()
	return render_template('profile-form.html', form=simpleForm)


@app.route('/result/alldogs', methods = ['GET', 'POST'])
def index():
	#generate = Dogs.query.all()
	#dogs = []
	form = ProfileForm(request.form)
	if request.method == "POST" and form.validate_on_submit():
		#username = form.username.data
		#choice = form.choice.data
		#email = form.email.data
		result = request.args
		#base_url = "https://dog.ceo/api/breeds/image/random"
		base_url = "https://dog.ceo/dog-api/"
		params = {}
		params['message'] = result.get(str)
		response = requests.get(base_url, params)
		data = json.loads(response.text)
		if choice == "All Dogs!":
			return render_template('all_dogs.html', result = data["result"], username = username)
		flash('All fields are required!')
		#base_url = 'https://dog.ceo/dog-api/breeds-image-random.php'
		#if choice == "A Breed!":
		#	return render_template('breeds.html', results = data["results"], username = username, dog_type = dog_type)
	
		#if db.session.query(User).filter_by(username = form.username.data).first():
		#	flash("That user already has emails set up...")
		#get_or_create_dogs(db.session, form.pic_id.data)
		#if app.config['ADMIN']:
	#		send_email(form.email.data, 'New Dog Pic', 'mail/new_dog', dog = form.choice.data)
	#	return redirect(url_for('see_my_dogs'))
	#return render_template('index.html', form=form,dogs=dogs)
	#flash('All fields are required!')

@app.route('/my_dogs')
def see_my_dogs():
	my_dogs = []
	dogs = Dogs.query.all()
	for d in dogs:
		user = Dogs.query.filter_by(picture_num = d.pic_id).first()
		my_dogs.append('my_dogs.html', my_dogs = my_dogs)


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
	return render_template('500.htm'), 500

if __name__ == '__main__':
    db.create_all()
    manager.run()




