import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager, Shell
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from threading import Thread
from werkzeug import secure_filename
import requests
import json
import re
import tweepy
import twitter_info


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364thisisnotsupersecure'

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/demgijsfinal"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587 #default
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') # TODO export to your environs -- may want a new account just for this. It's expecting gmail, not umich
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SUBJECT_PREFIX'] = '[Tweets App]'
app.config['MAIL_SENDER'] = 'demgijs364@gmail.com' # TODO fill in email
app.config['ADMIN'] = os.environ.get('ADMIN')

manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
mail = Mail(app)


#twitter authentication information 
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, parser = tweepy.parsers.JSONParser())

def make_shell_context():
    return dict(app=app, db=db, Tweet=Tweet, User=User, Mention=Mention) 

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

Tweet_Mention = db.Table('Tweet_Mention', db.Column('tweet_id', db.Integer, db.ForeignKey('tweet.id')), db.Column('mention_id', db.Integer, db.ForeignKey('mention.id')))

class Tweet(db.Model):
	__tablename__ = "tweet"
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(285))
	user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
	twitter_username = db.Column(db.String(64), unique = True)
	mentions = db.relationship('Mention', secondary = Tweet_Mention, backref = db.backref('tweet', lazy = 'dynamic'), lazy = 'dynamic')

class User(db.Model): 
	__tablename__ = "user"
	id = db.Column(db.Integer, primary_key = True)
	twitter_username = db.Column(db.String(64), unique = True)
	#in_tweets = db.relationship('Tweet', backref = "User") #the tweets the user is mentioned in 
	in_tweets = db.Column(db.String(64)) 
	email_address = db.Column(db.String(64), unique = True)

class Mention(db.Model):
	__tablename__ = "mention"
	id = db.Column(db.Integer, primary_key = True)
	mentioned = db.Column(db.String)
	#user = db.relationship('User', backref = "Mention")

class TweetForm(FlaskForm):
	username = StringField("Enter your Twitter handle (example '@my_username'):", validators = [Required()])
	email = StringField("Enter the email address to which you would like your mention updates to be sent:", validators = [Required()])
	submit = SubmitField('Sign me up!')


##Put get_or_create functions here 
def get_or_create_tweet(db_session, tweet_text, my_handle, tweets_im_in):
	tweet = db.session.query(Tweet).filterby(my_handle=user_id).first()
	if tweet:
		return tweet
	else:
		tweet = Tweet(tweet_text = text, my_handle = user_id, tweets_im_in = mentions)
		db.session.add(tweet)
		db.session.commit()
		return tweet

def get_or_create_user(db_session, username, tweets, email):
	user = db.session.query(User).filter_by(twitter_username = username).first()
	if user:
		return user
	else:
		user = User(twitter_username = username, tweets = in_tweets, email_address = email)
		db_session.add(user)
		db_session.commit()
		return user

def get_or_create_mention(db_session, my_handle, other_user):
	mention = db.session.query(Mention).filter_by(other_user = user).first()
	if mention:
		return mention
	else:
		mention = Mention(my_handle = mentioned, other_user = user)
		db_session.add(mention)
		db_session.commit()
		return mention




#Error routes
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
	return render_template('500.htm'), 500

@app.route('/', methods = ['GET', 'POST'])
def index():
	tweeter = Tweet.query.all()
	mentions = []
	form = TweetForm()
	if form.validate_on_submit():
		if db.session.query(Tweet).filter_by(username = form.username.data).first():
			flash("That user already has notifications set up...")
		get_or_create_tweet(db.session, form.username.data, form.mention.data)
		if app.config['ADMIN']:
			send_email(form.email.data, 'New Mention', 'mail/new_mention', tweet = form.text.data)
		return redirect(url_for('see_all_mentions'))
	return render_template('index.html', form=form,mentions=mentions)

@app.route('/all_mentions')
def see_all_mentions():
	all_mentions = []
	mentions = Mention.query.all()
	for m in mentions:
		user = Mention.query.filter_by(mentioned = m.mentioned).first()
		all_mentions.append('all_mentions.html', all_mentions = all_mentions)

if __name__ == '__main__':
    db.create_all()
    manager.run()




