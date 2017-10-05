import os
from flask import Flask, request, render_template, session, redirect, jsonify, flash
from jinja2 import StrictUndefined
from twilio.rest import Client
import schedule
import time
import datetime
import arrow
from threading import Thread
from helper import *
from model import connect_to_db, db, User, CreateHabit, UserHabit, Success

app = Flask(__name__)
app.secret_key = 'ABCSECRETDEF'

# raise errors if there are undefined variables in Jinja2
app.jinja_env.undefined = StrictUndefined

start_time = time.time()

# account_sid = os.environ["TWILIO_ACCOUNT_SID"]
# auth_token = os.environ["TWILIO_AUTH_TOKEN"]
# messaging_service_sid = os.environ["TWILIO_MESSAGING_SERVICE_SID"]
# twilio_from = os.environ["TWILIO_FROM_NUMBER"]
# twilio_to = os.environ["TWILIO_TEST_TO_NUMBER"]
# client = Client(account_sid, auth_token)


@app.route('/', methods=['POST'])
def collect_successes():
    """ process requests from API.AI triggered on success events. Process & 
    store in success table """

    # collect json from request, convert to dictionary:
    success_dict = request.get_json()

    # extract user mobile - ex: +18028253270
    mobile = success_dict['originalRequest']['data']['From']
    
    # extract time (time API.ai agent tracks success) - ex: 2017-10-01T15:40:08.959Z
    time = arrow.get(success_dict['timestamp'])
    time = time.format('YYYY-MM-DD HH:mm:ss ZZ')

    q = User.query.filter(User.mobile == mobile, User.is_partner == False).one()
    user_id = q.user_id

    q = UserHabit.query.filter(UserHabit.user_id == user_id, UserHabit.current == True).one()
    habit_id = q.habit_id

    success = Success(habit_id=habit_id, mobile=mobile, time=time)
    db.session.add(success)
    db.session.commit()
   
    return 'JSON posted'
    
    # TO DO: 
    # add row to success table w/ user_id, time
    # user_id = Users.query.filter(mobile == user_mobile and is_partner == False).one().user_id
    # collect information about user progress: 

    # ENHANCEMENTS:
    # consider factoring in 'MessagingServiceSid' and/or 'To' values to identify agent and protect against tracking a success for a partner
    # return a response that allows agent to customize success message w stats: 
        # total_days = 
        # current_streak = 
        # craft speech / display text
        # speech = 

        # logic to determine response 

        # response = 
        # Headers:
        # Content-type: application/json
        # Body:
        # {
        # "speech" : "response to the request"
        # "displayText": "Text displaye don the user device screen"
        # "data" : {"twilio"} : {<twilio_message>}}
        # "contextOut": [ ...]
        # "source": ""
        # "followupEvent": {"followupEvent" : {"name": "<event_name>", "data": {"<paramater_name>":"<parameter_value"}}}
        # }
        # when a followupEvent parameter is sent from the web service, the system ignores the rest.  
    
        # package into json and return to API.AI
        # create a custom response that's based on user data ... (slot filling)


@app.route('/home')
def show_homepage():
    """Show homepage."""

    return render_template('homepage.html')


@app.route('/verify', methods=['GET', 'POST'])
def verify_user():
    """ ask user for verification code that was sent via sms """

    mobile = request.args.get('mobile')
    session['mobile'] = mobile
    
    send_confirmation_code(mobile)

    return render_template('verification.html')
    # form to collect code and verify


@app.route('/signin', methods=['POST', 'GET'])
def log_in_user():
    """verifies mobile number via twilio then checks where to send user"""

    code = request.args.get('code')
    # verify correct code with Twilio
    session['code'] = code
    mobile = session['mobile']

    # if correct code:
    if code == session['verification_code']:
        
        # query if user is in the db:
        q = User.query.filter(User.mobile == mobile, User.is_partner == False).first()
        
        # if user in db, redirect to /dashboard
        if q:
            session['user_id'] = q.user_id
            return redirect('/dashboard')
        
        else:
            return redirect('/name')
    
    # if incorrect code:
    else:
        flash("The code you entered was incorrect. Please enter the new code sent to you")
        return redirect('/verify?mobile={}'.format(mobile))

    # Later TODO: determine if they've completed onboarding, etc. 

@app.route('/signup', methods=['POST', 'GET'])
def create_user():
    """creates user"""

    name = request.args.get('name')
    session['name'] = name
    mobile = session['mobile']

    name = name
    user = User(name=name, mobile=mobile, is_partner=False)
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.user_id
    return redirect('/habit')
 

@app.route('/dashboard')
def show_dashboard():
    """ display user progress"""

    # gather data about current habit and display to user

    return render_template('dashboard.html')

    
@app.route('/name')
def onboarding_step1():
    """ onboarding, step 1 - identify name """

    return render_template('name.html')
    # form to collect name --> send user to factors, but for now --> /habit

# @app.route('/factors')
# def onboarding():
#     """ onboarding, step 2 - identify factors """

#     return render_template('factors.html') 
#     # displays list of profile-factors.  User selects and submits.


@app.route('/habit')
def habit_selection_1():
    """ first step of new habit process """

    # choice - break an existing habit? Create a new habit?
    # if break - /habit-break-recs
    # if new - /habit-recs 

    habits = CreateHabit.query.all()
    print habits

    # temporary ... 
    return render_template('browse.html', habits=habits) 
    


# @app.route('/habit-break-recs')
# def display_break_recs():
#     """ display suggested habits to break based on factors """

#     # ajax call to get 4 more recommendations?

#     return render_template('habit-recs.html')


# @app.route('/habit-break-browse')
# def browse_break_habits():
#     """ display library of habits to break """

#     return render_template('habit-break-browse.html')


@app.route('/time', methods=['POST', 'GET'])
def define_habit_time():
    """ collects habit time from user"""

    # # if 'break' in session, display diff text (re: replacement)

    habit_id = request.args.get('habit_id')
    session['habit_id'] = habit_id

    return render_template("time.html")


# @app.route('/habit-recs')

# if 'break' in session, display diff text (re: replacement)

# @app.route('/habit-browse')

@app.route('/confirm', methods=['POST', 'GET'])
def show_confirmation():
    """ confirm information about habit to user """

    hour = int(request.args.get("hour"))
    tz = request.args.get("tz")

    # create an arrow object, replace hour and timezone.
    t = arrow.now()
    time = t.replace(hour=int('{}'.format(hour)), tzinfo='{}'.format(tz))
    
    # convert to UTC and extract hour to store seperately
    utc_time = time.to('UTC')
    utc_hour = utc_time.hour # an integer
    
    # format to store in db
    utc_time = utc_time.format('YYYY-MM-DD HH:mm:ss ZZ')
    time = time.format('YYYY-MM-DD HH:mm:ss ZZ')
   
    create_habit_id = session['habit_id']
    if 'break_habit_id' not in session:
        break_habit_id = None
    else:
        break_habit_id = session['break_habit_id']
    current = True
    if 'partner_id' not in session:
        partner_id = None
    else:
        partner_id = session['partner_id']

    user_id = session['user_id']

    # look up any other habits user has and set current flag to false
    previous_user_habits = UserHabit.query.filter(User.user_id == user_id).all()
    
    if previous_user_habits:
        for habit in previous_user_habits:
            habit.current == False
            db.session.add(habit)

    # store to user-habits table
    user_habit = UserHabit(user_id=user_id, create_habit_id=create_habit_id, 
        break_habit_id=break_habit_id, current=current, tz=tz,
        utc_time=utc_time, utc_hour=utc_hour, partner_id=partner_id)

    db.session.add(user_habit)
    
    db.session.commit()

    return render_template('confirm.html', user_habit=user_habit, hour=hour)


# @app.route('/habit-coach')

# @app.route('/habit-partner')

# @app.route('/habit-ready')

# @app.route('/receive-messages', mehtods=['GET', 'POST'])
# def collect_success():
#     """ webhook for receiving success requests from API.AI """


# @app.route('/get-habit-stats', methods=['GET', 'POST'])
# def collect_habit_stats():
#     """ webhook for API.AI to request info to use in user reesponse
    
#     API.AI lingo: 'webhook for slot-filling on the intent' 

#     for example: "well done, {Sav}! That's {5} days in a row"! """


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)




if __name__ == "__main__":
    # set the schedule for sending daily nudges:
    #schedule.every(1).minutes.do(send_daily_nudge)
    
    # establish the thread:
    #t = Thread(target=run_schedule)
    #t.start()
    #print"Schedule is running. Start time: " + str(start_time)

    # connect to db
    connect_to_db(app)

    app.run(host="0.0.0.0", port=5000, debug=True)
    
    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    