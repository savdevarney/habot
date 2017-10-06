import os
from twilio.rest import Client
import time
import arrow
import random
from flask import session
from model import connect_to_db, db, User, CreateHabit, UserHabit, Success, Streak

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
messaging_service_sid = os.environ["TWILIO_MESSAGING_SERVICE_SID"]
twilio_from = os.environ["TWILIO_FROM_NUMBER"]
twilio_to = os.environ["TWILIO_TEST_TO_NUMBER"]
client = Client(account_sid, auth_token)

# helper functions for verifiction code:

def send_confirmation_code(mobile):
        verification_code = generate_code()
        send_code(mobile, verification_code)
        session['verification_code'] = verification_code
        print verification_code
        return verification_code


def generate_code():
        return str(random.randrange(10000, 999999))


def send_code(mobile, verification_code):
    message = client.messages.create(
        messaging_service_sid=messaging_service_sid,
        to=mobile,
        from_=twilio_from,
        body="your code: {}".format(verification_code))


# helper functions for sending welcome messages (TBD)

# helper functions for sending reminders:

def send_daily_nudge():
    """ send reminders sms messages to every user that should receive at that hour """

    utc_now = arrow.utcnow()
    utc_hour = utc_now.hour

    habits = UserHabit.query.filter(UserHabit.time.hour == utc_hour).all()

    for habit in habits:
        habit = habit.habit.create_habit_title
        to = habit.user.mobile
        name = habit.user.name

        message = client.messages.create(
            messaging_service_sid=messaging_service_sid,
            to=to,
            from_=twilio_from,
            body="Ready to {}, {}".format(habit, name))

    print "the scheduling script ran @ {}".format(time.time())
    print(message.sid)


# helper functions for datetime

def get_local_hour(time, tz):
""" returns the hour in the local time zone given a datetime string in utc"""
    time_utc = arrow.utcnow()
    local_time = arrow_utc.to(tz)
    local_hour = local_time.hour
    return local_hour


def get_utc_hour(time):
    """ returns the utc hour of a datetime string in utc """

    time_utc = arrow.utcnow()
    utc_hour = time_utc.hour
    return utc_hour


# helper functions for tracking success

def get_stats(habit_id):
    """ given a habit_id produce stats for that habit at the current date/time
    returns a dictionary of format:

        {
        'total_days':6,
        'current_streak':6,
        'potential_streak': 7
        'longest_streak': 6
        }

        example message from bot:
        (check if potential > current):
            "You ready, Sav? Suceeding today will put you on a 7 day streak!
        
        (upon success and if current == longest):
            "Awesome job, Sav! You hit a new record streak: 6 days!"

        """
 
    stats = {}

    # TODO: have one single joined query and leverage relationships. 
    habit = UserHabit.query.filter(UserHabit.habit_id == habit_id).one()
    tz = habit.user.tz

    current_time = arrow.utcnow()
    
    stats['total_days'] = Success.query.filter(Success.habit_id == habit_id).count() 
    # works but provides 7L? 

    # find most recent success to identify current streak
    last_success = find_last_success(habit_id)
    last_success_time = last_success.time
    last_success_id = last_success.success_id

    # iterate through all streaks to find longest_streak and current_streak (if day qualifies)
    
    streaks = Streak.query.filter(Streak.habit_id == habit_id).all()
    longest_streak = 0
    for streak in streaks:

        # calculate lengths of all streaks
        streak_start = (arrow.get(streak.start_success.time)).to(tz)
        streak_end = (arrow.get(streak.end_success.time)).to(tz)
        streak_length = streak_start.date() - streak_end.date()
        
        # find longest streak
        if streak_length > longest_streak:
            longest_streak = streak_length
            stats['longest_streak'] = streak_length
        
        if streak.end_success == last_success_id:
            if dates_same_or_consecutive(last_success_time, current_time, tz):
                stats['current_streak'] = streak_length
                stats['potential_streak'] = streak_length

                if dates_consecutive(last_success_time, current_time, tz):
                    stats['potential_streak'] = streak_length + 1

    return stats

def process_success(mobile, time):

    # get User
    user = User.query.filter(User.mobile == mobile).one()
    user_id = user.user_id

    # get user's current habit id
    habit = UserHabit.query.filter(UserHabit.current == True, UserHabit.user_id == user_id).one()
    habit_id = habit.habit_id

    last_time = (find_last_success(habit_id)).time

    if dates_same(time, last_time, tz)
        print "user has already succeeded on this day"

    else:
        # determine if streak
        streak_id = get_streak_id(habit_id, success_time)

        if streak_id == None:
            # create success and create sterak
            success_id = add_success_get_id(habit_id, mobile, time)
            streak_update(habit_id, streak_id, success_id)
        else:
            # create success and update streak
            success_id = add_success_get_id(habit_id, mobile, time)
            streak_update(habit_id, streak_id, success_id)
    
        
def add_success_get_id(habit_id, mobile, time):

    success = Success(habit_id=habit_id, mobile=mobile, time=time)
    db.session.add(success)
    db.session.commit
    # TO DO: is it possible to immediately return the success_id after insertion? 
    return success_id

def find_last_success(habit_id):

    last_success = Success.query.filter(Success.habit_id == habit_id).order_by(Success.time.desc()).first()

    return last_success


def get_streak_id(habit_id, success_time):
    """ determines if a new success is part of an existing streak or not.
    if not, returns False.  If streak is True, returns streak_id of current streak """

    user_habit = UserHabit.query.filter(UserHabit.habit_id == habit_id).one()
    tz = user_habit.user.tz

    success_time = arrow.get(success_time)

    last_success = find_last_success(habit_id)

    if last_success:
        last_sucess_id = last_success.success_id
        last_success_time = arrow.get(last_success.time)
        last_success_local = last_success_time.to(tz)

        # TO DO ... use are_dates_consecutive function
        # TO DO ... user update_or_create_streak function
                
        # if existing streak
        if dates_consecutive(last_success_time, success_time, tz)
            streak = Streak.query.filter(Streak.end == last_success_id).one()
            return streak.streak_id
        else:
            return None
    else:
        return None

def streak_update(habit_id, streak_id, success_id):
    """ creates or updates a streak """

    if streak_id is None:
        # create new streak
        streak = Streak(habit_id=habit_id, start_success=success_id, end_success=success_id)
    
    else:
        # update existing streak
        streak = Streak.query.filter(Streak.streak_id == streak_id).one()
        streak.end_success = success_id

    db.session.add(streak)
    db.session.commit()


def dates_same(first_datetime, second_datetime, tz):
    """ checks if two date are the same.  Returns True if so and False if not """

    if (first_datetime.to(tz)).date() == (second_datetime.to(tz)).date():
        return True
    else:
        return False

def dates_consecutive(first_datetime, second_datetime, tz):
    """ checks if two date are consecutive.  Returns True if so and False if not """

    diff = (first_datetime.to(tz)).date() - (second_datetime.to(tz)).date()
    if diff.days == -1:
        return True
    else:
        return False

def dates_same_or_consecutive(first_datetime, second_datetime, tz):
    """ checks if two dates are the same or consecutive"""

    if (dates_same(last_success_time, current_time, tz) 
        or dates_consecutive(last_success_time, current_time, tz):
        return True
    else: 
        return False






# a working monolith function (with old db) ... needs to be broken out and work with revised db model. 
def process_success(mobile, success_time):
        """ tracks user success in db """

        # get user_id
        user = User.query.filter(User.mobile == mobile, User.is_partner == False).one()
        user_id = user.user_id

        # get habit_id and tz
        user_habit = UserHabit.query.filter(UserHabit.user_id == user_id, UserHabit.current == True).one()
        habit_id = user_habit.habit_id
        tz = user_habit.tz

        # convert success_time object to string to store in db if necessary. 
        time = success_time.format('YYYY-MM-DD HH:mm:ss ZZ')

        # before we add success, make sure success doesn't already exist for that date (in local time)
        previous_successes = Success.query.filter(Success.habit_id == habit_id).all()

        if previous_successes:
            print "there were previous successes!"
            print previous_successes
            successes = []
            for success in previous_successes:
                successes.append(success.time)

            sorted_success_times = sorted(successes)

            # most recent success:
            last_success = arrow.get(sorted_success_times[-1])

            # convert to local time:
            last_success_local = last_success.to(tz)
            print last_success_local

            #convert current success to local time:
            this_success_local = success_time.to(tz)
            print this_success_local

            #if they're on the same date, don't add data to db
            if last_success_local.date() == this_success_local.date():
                print "success not tracked: success for this day already exists"
                # TODO: ask agent to say that's already been tracked in response JSON

            else: 

                # add success to db
                success = Success(habit_id=habit_id, mobile=mobile, time=time)
                
                # increment total days in user_habit: 
                user_habit.total_days += 1
                print "total number of days now equals: "
                print user_habit.total_days
                
                # check if date deltas = -1 (therefore an existing streak)
                diff = last_success_local.date() - this_success_local.date()
                
                # if existing streak
                if diff.days == -1:

                    # query to find existing streak
                    existing_streak = Streak.query.filter(Streak.habit_id == habit_id, Streak.end == None).one()
                    print "existing streak found!"
                    
                    # update existing streak days
                    existing_streak.days += 1
                    db.session.add(existing_streak)
                    print "streak incremented! new streak: "
                    print existing_streak.days

                    # updated longest_streak if new record
                    if existing_streak.days > user_habit.longest_streak:
                        
                        user_habit.longest_streak = existing_streak.days
                        print "new streak record recorded!"
                # if no existing streak, create one
                else:
                    # create a new streak
                    new_streak = Streak(habit_id=habit_id, days=1, start=time, end=None)
                    db.session.add(new_streak)

                db.session.add(success, user_habit)
                db.session.commit()

                print "success tracked!"
        else:
            # add a new success and new_streak to db 
            success = Success(habit_id=habit_id, mobile=mobile, time=time)
            new_streak = Streak(habit_id=habit_id, days=1, start=time, end=None)
            db.session.add(success, new_streak)
            db.session.commit() 
            # consider adding something custom in response JSON ... congratulating on it being the first time, etc. 








