# SI 364 - Final Project questions

## Overall

* **What's a one-two sentence description of what your app will do?**
This app will use the Twitter API to gather data about a specific user, and send emails when that user is mentioned in a tweet. 

## The Data

* **What data will your app use? From where will you get it? (e.g. scraping a site? what site? -- careful not to run it too much. An API? Which API?)**
I will be using the Twitter API. 

* **What data will a user need to enter into a form?**
The user will need to enter their twitter username and their own email so that the app can send the updates to them. 

* **How many fields will your form have? What's an example of some data user might enter into it?**
The form will have two fields. 
1. Twitter handle - Ex: demerygijsbers
2. Email for mention updates - Ex: demgijs@umich.edu

* **After a user enters data into the form, what happens? Does that data help a user search for more data? Does that data get saved in a database? Does that determine what already-saved data the user should see?**
This data will be saved in a database, but will also show a page that say the email updates have been set for that user and they will be notified whenever they are mentioned in a tweet.  

* **What models will you have in your application?**
This models in this application will be: 
1. User
2. Mentions
3. Tweet

* **What fields will each model have?**
1. User model fields: id, twitter_username, mentions, email
2. Mentions model: id, twitter_username, mentioner
3. Tweet: id, mentioner, twitter_username, text 

* **What uniqueness constraints will there be on each table? (e.g. can't add a song with the same title as an existing song)**
A person will only be able to sign up once: Can't add twitter handle more than once for mentions updates. 

* **What relationships will exist between the tables? What's a 1:many relationship between? What about a many:many relationship?**
1:many -> user:mentions (1 user might have many people mentioning them in tweets)
many:many -> many tweets might have many users mentioned 

* **How many get_or_create functions will you need? In what order will you invoke them? Which one will need to invoke at least one of the others?**
3 get_or_create functions:
1. user
2. mentions (will need to invoke user)
3. tweet 

## The Pages

* **How many pages (routes) will your application have?**
This application will have 3 pages
1. index (the form)
2. result (confirmation of email set up)
3. Already entered username (results page if the twitter handle has already been entered for mention updates)

* **How many different views will a user be able to see, NOT counting errors?** the user will be able to see all views of the index form page, the results page, and the 'already entered username' page

* **Basically, what will a user see on each page / at each route? Will it change depending on something else -- e.g. they see a form if they haven't submitted anything, but they see a list of things if they have?**

## Extras

* **Why might your application send email?**
The app will send email to update a user on mentioned tweets so they don't have to always be in the app for updates and notifications

* **If you plan to have user accounts, what information will be specific to a user account? What can you only see if you're logged in? What will you see if you're not logged in -- anything?**
There won't necessarily be accounts, but a user does sign up spefically for their own mention updates and will only be able to see those. 

* **What are your biggest concerns about the process of building this application?**

I am worried that I will not be able to get specifically the 'mention' data to email to a user. I also am not entirely sure how simple it will be to get this data without a user having to enter their own twitter API keys and how I will navigate those secret keys. 