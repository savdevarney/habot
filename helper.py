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
    hour_now = utc_now.hour

    # users = # database query for user with time.hour == hour in USER-HABITS time variable joined with user-habit table

    # for user in users: 
    #     name = user.name
    #     mobile = user.mobile
    #     habit = Create_habit_description

    message = client.messages.create(
        messaging_service_sid=messaging_service_sid,
        to=twilio_to,
        from_=twilio_from,
        body="if you receive this text - then the scheduling task works!")

    print "the scheduling script ran @ {}".format(time.time())
    print(message.sid)


# helper functions for datetime

    def get_local_hour(utc_time, tz):
        """ returns the hour in the local time zone given a datetime string"""
        arrow_utc = arrow.get(utc_time)
        local_time = arrow_utc.to(tz)
        local_hour = local_time.hour
        return local_hour


# helper functions for tracking success

def get_stats(habit_id):
    """ given a habit_id produce stats for that habit
    returns a dictionary of format:

    {'total_days':6,
        'current_streak':6, 
        'longest_streak': 6} 

        """
    # consider making this a method of either User or HabitUser
    # written with assumption I'll move to optimized db structure
    # (Streak.start and Streak.end are foreign keys of Success.success_id)
    
    stats = {}

    habit = UserHabit.query.filter(UserHabit.habit_id == habit_id).one()
    tz = habit.tz

    successes = Success.query.filter(Success.habit_id == habit_id).all()

    stats['total_days'] = len(successes)
    ordered_successes = sorted(successes)
    last_success = ordered_successes[-1]
    last_success_id = last_success.success_id

    streaks = Streak.query.filter(Streak.habit_id == habit_id).all()

    longest_streak = 0

    for streak in streaks:

        streak_start = (arrow.get(streak.start.time)).to(tz)
        streak_end = (arrow.get(streak.end.time)).to(tz)
        streak_length = streak_start.date() - streak_end.date()
        if streak_length > longest_streak:
            longest_streak = streak_length
            stats['longest_streak'] = streak_length
        if streak.end == last_success_id:
            stats['current_streak'] = streak_length

    return stats
    

# a working monolith function that needs to be broken out!
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








