# habot

Habot is a coach for creating daily healthy habits through a conversational interface.

As you’re onboarded with Habot, you rate how well you’re doing in certain life areas. Habot then recommends a set of habits that would be best to work on. After committing to a habit, you track progress with Habot every day through delightful text message exchanges. You earn a new streak every 3 consecutive successful days and are encouraged to collect at least 7 streaks to create the new habit (21 days in total).

Habits included are built off of BJ Fogg's Tiny Habit principles (http://tinyhabits.com/) - that is they are:
- incredibly specific
- can be done in 30 seconds or less

During onboarding, users provide: 
- mobile phone number + country
- timezone
- name
- ratings for 'profiles' (health categories: mind, sleep, relationships, performance, movement, nutrition)
- habit selection
- time to be reminded

Other features: 
- 'passwordless' sign up and sign in via a 6 digit randomly generated pin sent to verify mobile number
- data visualization to track progress toward 3 day streaks and number of 3-day streaks

Habot conversation features:
- daily reminders
- success tracking via reply with '#yes'
- 'pausing' of habit tracking if inactive for > 7 days.  Reactivation with 'unpause'
- small talk :)

API integrations:
- Twilio
- DialogFlow

Tech stack:
- PostgreSQL
- SQL Alchemy
- Python
- Flask
- Jinja
- JQuery
- Bootstrap
- CSS
- HTML
- JavaScript

Libraries utilized:
- schedule
- arrow
- phonenumbers
- pycountry
- pytz
- emoji
- D3
- TypeIt

Currently working on:
- handling all errors during sign up flow
- fixes with the scheduling utility
- preparations for deployment to habot.me

If you have examples of Tiny Habits you would like added to Habot, please email me!

Video of current local build: 

https://drive.google.com/open?id=0BxzJpyba64UfX2pHd2NpUk5wMm8

Habot data model: 

https://github.com/savdevarney/habot/blob/master/Habot%20Data%20Model.png



