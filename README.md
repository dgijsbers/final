README - Documentation for Demery Gijsbers' Final Project -SI364

This project takes JSON data from the Dog CEO API to send emails to a user with a link to a new picture of new dog.

The database used that will need to be created is titled "demgijsfinalapp" and the title of the project is "final" so to run is: python final.py runserver.
Other setup needed is to export your own MAIL_USERNAME and MAIL_PASSWORD in the terminal. It may not accept unsecured emails from this app, so you can either change that security setting, or setup a new dummy email to use for the app. I installed "php" as instructed by the Dog API README, though I believe this would only be used if I were using the photos directly. 

This app will open a form on the localhost for a user to enter a username for "Dog-A-Day" and their email address so that they are emailed the picture. The starting URL is "localhost:5000/" and this should open a login page, with options to log out or register a new account. 

The emails are sent from my ADMIN account, and a user may only set up one account per email address. 