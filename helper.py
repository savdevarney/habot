import os
from twilio.rest import Client
import time
import arrow
import random
from flask import session

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
def process_success(mobile, success_time):
        """ tracks user success in db """

        user = User.query.filter(User.mobile == mobile, User.is_partner == False).one()
        user_id = user.user_id

        user_habit = UserHabit.query.filter(UserHabit.user_id == user_id, UserHabit.current == True).one()
        habit_id = user_habit.habit_id
        tz = q.tz

        # convert success_time object to ISO to store in db. 
        time = success_time.format('YYYY-MM-DD HH:mm:ss ZZ')

        # before we add success, make sure success doesn't already exist for that date (in local time)
        q = Success.query.filter(Success.habit_id == habit_id).all()

        if q:
            successes = []
            for success in q:
                successes.append(success.time)

            sorted_success_times = sorted(successes)

            # most recent success:
            last_success = arrow.get(sorted_success_times[-1])
            # convert to local time:
            last_success_local = last_success.to(tz)

            #convert this success to local time:
            this_success_local = success_time.to(tz)

            #if they're on the same date, don't add data to db
            if last_success_local.date() == this_success_local.date():
                print "success not tracked: success for this day already exists"
                # TODO: ask agent to say that's already been tracked in response JSON

            else: 
                
                # increment total days: 
                user_habit.total_days += 1
                print "total number of days now equals: " + user_habit.total_days
                
                # check if date deltas = -1 (therefore an existing streak)
                if (last_success_local.date() - this_success_local.date()).days == -1):
                    
                    # add success to db
                    success = Success(habit_id=habit_id, mobile=mobile, time=time)

                    # query to find existing streak row
                    existing_streak = Streak.query.filter(Streak.habit_id == habit_id, Streak.end == 'NULL').one()
                    
                    # update existing streak days
                    existing_streak.days += 1
                    print "streak incremented! new streak: " + existing_streak.days

                    # if existing streak days longer than longest_streak, update longest_streak
                    if existing_streak.days > user_habit.longest_streak:
                        
                        # update user_habit object 
                        user_habit.longest_streak = existing_streak.days
                        print "new streak record recorded!"

                    db.session.add(success, existing_streak, user_habit)
                    db.session.commit()

                    print "success tracked!"
        else:
            # add a new success and new_streak to db 
            success = Success(habit_id=habit_id, mobile=mobile, time=time)
            new_streak = Streak(habit_id=habit_id, days=1, start=time, end='NULL')
            db.session.add(success, new_streak)
            db.session.commit() 
            # consider adding something custom in response JSON ... congratulating on it being the first time, etc. 








