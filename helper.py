import os
from twilio.rest import Client
import time
import arrow
import random
from flask import session
from model import (connect_to_db, db, User, CreateHabit, UserHabit, Success,
    Streak, Partner, Coach, UserProfile, FactorScore, Factor,
    FactorHabitRating)
import pycountry
import phonenumbers
import pytz


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

    utc_hour = get_utc_hour()

    habits = UserHabit.query.filter(UserHabit.time.hour == utc_hour).all()
    #TODO - make sure ^ works

    for habit in habits:
        habit = habit.habit.title
        to = habit.user.mobile
        name = habit.user.name

        message = client.messages.create(
            messaging_service_sid=messaging_service_sid,
            to=to,
            from_=twilio_from,
            body="Ready to {}, {}".format(habit, name))

    print "the scheduling script ran @ {}".format(time.time())
    print(message.sid)


# helper functions for createing a new user

def create_user_return_id(name, mobile, tz):
    """ creates a new user and returns the assigned user_id"""

    user = User(name=name, mobile=mobile, tz=tz)
    db.session.add(user)
    db.session.commit()
    user = User.query.filter(User.mobile == mobile).first()
    user_id = user.user_id

    return user_id

# helper functions for creating a new profile of factor ratings. 

def create_profile_return_id(user_id, date):
    """ creates a new facor profile and returns user_factor_profile_id"""

    new_profile = UserProfile(user_id=user_id, date=date)
    db.session.add(new_profile)
    db.session.commit()
    new_profile = UserProfile.query.filter(UserProfile.user_id == user_id).first()
    profile_id = new_profile.profile_id
    
    return profile_id


def create_factor_scores(profile_id, factor_scores):
    """ creates a new record for every factor scored by user (passed through 
        in factor_scores dictionary """

    for factor, score in factor_scores.items():
        new_rating = FactorScore(profile_id=profile_id, factor_id=factor, score=score)
        db.session.add(new_rating)
        db.session.commit()


def get_last_factor_profile(user_id):
    """ returns the last profile (list of factor ratings as FactorRating objects) 
    for a given user_id """

    last_profile = UserProfile.query.filter(UserProfile.user_id == user_id).order_by(UserProfile.date.desc()).first()
    if last_profile:
        # a list of FactorScore objects
        last_factor_scores = last_profile.factor_scores
        return last_factor_scores
    else:
        return None


# helper functions for making recommendations

def get_recommendations(user_id):
    """ returns a ranked list of recommended habits for the user as CreateHabit 
    objects. """

    # create a dictionary of the latest factor scores from the most recent profile.
    last_factor_scores = get_last_factor_profile(user_id) 
    factor_scores = {}

    for score in last_factor_scores:
        factor_scores[score.factor_id] = score.score

    # grab all habits
    habits = CreateHabit.query.all()
    
    # create a dictionary of all habits to hold rankings after they're calculated
    habit_fits = {}
    
    for habit in habits: 
        habit_fits[habit.create_habit_id] = 0

    # recommend habits by determining 'fit' of each habit for user (higher = better)
    for habit in habits:
        habit_fit = 0
        # get the habit_id
        create_habit_id = habit.create_habit_id
        # get all ratings for that habit (how well it supports a given factor)
        habit_ratings = FactorHabitRating.query.filter(
            FactorHabitRating.create_habit_id == create_habit_id).all()
        # for each rating, for each habit, calculate 'fit' for user
        for rating in habit_ratings:
            factor_id = rating.factor_id
            rating = rating.rating
            score = factor_scores[factor_id]
            # calculate fit for a single factor
            factor_habit_fit = rating * score
            # calculate overall fit by summing habit ratings across all factors
            habit_fit += factor_habit_fit
        # populate habit_fits dictionary: { id : # }
        habit_fits[create_habit_id] = habit_fit

    recommended_habits = []
    
    for habit in habit_fits:
        if habit_fits[habit] > 0:
            ranked_habit = (habit_fits[habit], habit)
            recommended_habits.append(ranked_habit)

    recommended_habits.sort(reverse=True)
    # format: [(#, id), (#, id), (#, id)]

    if recommended_habits:
        print "recommending personalized habits"
        ranked_habits = []

        for habit in recommended_habits:
            habit_id = habit[1]
            habit_obj = CreateHabit.query.filter(CreateHabit.create_habit_id == habit_id).first()
            ranked_habits.append(habit_obj)
    
        return ranked_habits # a list of CreateHabit objects

    else:
        print "recommending deafult habits"
        return habits


def add_new_habit_return_id(user_id, create_habit_id, break_habit_id, utc_time, partner_id):
    """ sets any previous habits to current=False and adds new habit for user """

    # look up any other habits user has and set current flag to false
    previous_user_habits = UserHabit.query.filter(User.user_id == user_id).all()
    
    if previous_user_habits:
        for habit in previous_user_habits:
            habit.current == False
            db.session.add(habit)

    # store to new habit to user-habits table
    user_habit = UserHabit(user_id=user_id, create_habit_id=create_habit_id, 
        break_habit_id=break_habit_id, current=True, active=True,
        utc_time=utc_time, partner_id=partner_id)

    db.session.add(user_habit)
    
    db.session.commit()

    habit = UserHabit.query.filter(UserHabit.user_id == user_id).order_by(UserHabit.habit_id.desc()).first()

    habit_id = habit.habit_id

    return habit_id


# helper functions for datetime

def get_local_hour(tz):
    """ returns the curernt local hour in a time zone"""
    
    time_utc = arrow.utcnow()
    time_local = time_utc.to(tz)
    local_hour = time_local.hour
    return local_hour


def get_utc_hour():
    """ returns the utc hour of the current time"""

    time_utc = arrow.utcnow()
    utc_hour = time_utc.hour
    return utc_hour

# helper functions for country and timezone information

def sort_countries():
    """ creates a dictionary of country names(keys) and 2-digit country codes 
    (values) and then returns a sorted list of key, value pairs as tuples in
    alphabetical order """ 

    country_info = {}
    for country in pycountry.countries:
        country_info[country.name] = country.alpha_2

    sorted_countries = sorted(country_info.items())
    return sorted_countries

def format_mobile(mobile, country_code):
    """ returns an internatinally formatted mobile number as a string given a 
    mobile number (string) in any format and a 2-digit country code for that
    mobile number """

    mobile_object = phonenumbers.parse(mobile, country_code)
    mobile = phonenumbers.format_number(mobile_object, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    return mobile

def get_country_timezones(country_code):
    """ returns a list of timezones (in strings) for a country given the 2-digit
    country code for that country"""

    # create a dictionary of timezones for every country from pytz
    # format: {country_code: ['timezone_1', 'timezone_2']}
    all_country_timezones = pytz.country_timezones
    # extract the list of all timezones for country
    country_timezones = all_country_timezones[country_code]
    timezones = [] # a list to collect only common times for that country
    # only display zone if in the list of common_timezones
    for zone in country_timezones:
        if zone in pytz.common_timezones:
            timezones.append(zone)
    return timezones


# helper functions for tracking success

def get_stats(habit_id):
    """ given a habit_id produce stats for that habit at the current date/time
    returns a dictionary of format:

        {
        'total_days': 10,
        'current_streak': 6,
        'potential_streak': 7,
        'current_three_day_streak': 2
        'three_day_streaks': 2,
        'longest_streak': 6,
        }

        example message from bot:
        (check if potential > 3 and longest < potential):
            "You ready, Sav? Suceeding today will give you a 7 day streak
            overall and a new record!"
        
        (upon success check if current == longest):
            "Awesome job, Sav! You hit a new record streak: 7 days!"

        (check if potential < 3 and total < 21)
            "You ready, Sav? 

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
    if last_success:
        last_success_time = last_success.time
        last_success_id = last_success.success_id

        # iterate through all streaks to get streak stats:
        streaks = Streak.query.filter(Streak.habit_id == habit_id).all()
        
        stats['longest_streak'] = 0
        stats['three_day_streaks'] = 0

        for streak in streaks:

            # calculate lengths of streak
            streak_start = (arrow.get(streak.start_success.time)).to(tz)
            streak_end = (arrow.get(streak.end_success.time)).to(tz)
            streak_length = -((streak_start.date() - streak_end.date()).days)
            
            # determine if it's the longest streak
            if streak_length > stats['longest_streak']:
                stats['longest_streak'] = streak_length

            # determine if it classifies as a three_day streak
            if streak_length / 3 > 0:
                stats['three_day_streaks'] += (streak_length / 3)
            
            # find the last streak
            if streak.end_id == last_success_id:
                # if end of last streak == today or yesterday:
                if dates_same_or_consecutive(last_success_time, current_time, tz):
                    stats['current_streak'] = streak_length
                    stats['potential_streak'] = streak_length
                    # if end of last streak == yesterday:
                    if dates_consecutive(last_success_time, current_time, tz):
                        stats['potential_streak'] = streak_length + 1
                # if end of last streak != today or yesterday:
                else:
                    stats['current_streak'] = 0
                    stats['potential_streak'] = 1

        # find the current_three_day streak
        if stats['current_streak'] >= 3:
            stats['current_three_day_streak'] = stats['current_streak'] - (3 * stats['three_day_streaks'])
        else:
            stats['current_three_day_streak'] = stats ['current_streak']
    
    else:
        # if no successes ... 
        stats['longest_streak'] = 0
        stats['current_streak'] = 0
        stats['three_day_streaks'] = 0
        stats['potential_streak'] = 1
        stats['current_three_day_streak'] = 0

    return stats

def graph_stats(stats):
    """ provides a json ready dictionary to send to d3 dashboard graph """

    graph_stats = {}
    num_streaks = stats['three_day_streaks']
    num_days = stats['current_three_day_streak']

    graph_stats['num_streaks'] = []
    graph_stats['num_days'] = []

    for i in range(1,num_streaks + 1):
        new = {}
        new['label'] = '{}x3-day'.format(i)
        new['count'] = 1
        graph_stats['num_streaks'].append(new)

    for i in range(1,num_days + 1):
        new = {}
        new['label'] = '{}-day'.format(i)
        new['count'] = 1
        graph_stats['num_days'].append(new)

    return graph_stats


def process_success(mobile, time):

    # get User
    user = User.query.filter(User.mobile == mobile).one()
    user_id = user.user_id

    # get user's current habit id
    habit = UserHabit.query.filter(UserHabit.current == True, UserHabit.user_id == user_id).one()
    habit_id = habit.habit_id

    last_time = (find_last_success(habit_id)).time

    if dates_same(time, last_time, tz):
        print "user has already succeeded on this day"

    else:
        # determine if streak
        streak_id = get_streak_id(habit_id, success_time)

        if streak_id == None:
            # create success and create sterak
            success_id = add_success_get_id(habit_id, mobile, time)
            streak_update(habit_id, streak_id, success_id)
            print "new streak added"
        else:
            # create success and update streak
            success_id = add_success_get_id(habit_id, mobile, time)
            streak_update(habit_id, streak_id, success_id)
            print "existing streak updated"

        print "user success processed"
    
        
def add_success_get_id(habit_id, mobile, success_time):

    time = success_time.format('YYYY-MM-DD HH:mm:ss ZZ')
    success = Success(habit_id=habit_id, mobile=mobile, time=time)
    db.session.add(success)
    db.session.commit
    last_success = find_last_success(habit_id)
    return last_success.success_id

def find_last_success(habit_id):
    # can also do this by user_id ... order_by success_id

    last_success = Success.query.filter(Success.habit_id == habit_id).order_by(Success.time.desc()).first()

    return last_success


def get_streak_id(habit_id, success_time):
    """ determines if a new success is part of an existing streak or not.
    returns streak_id or none if success is not part of a streak """

    user_habit = UserHabit.query.filter(UserHabit.habit_id == habit_id).one()
    tz = user_habit.user.tz

    last_success = find_last_success(habit_id)

    if last_success:
        last_sucess_id = last_success.success_id
        last_success_time = arrow.get(last_success.time)
        last_success_local = last_success_time.to(tz)
                
        # if existing streak
        if dates_consecutive(last_success_time, success_time, tz):
            streak = Streak.query.filter(Streak.end_id == last_success_id).one()
            return streak.streak_id
        else:
            return None
    else:
        return None

def streak_update(habit_id, streak_id, success_id):
    """ creates or updates a streak """

    if streak_id is None:
        # create new streak
        streak = Streak(habit_id=habit_id, start_id=success_id, end_id=success_id)
    
    else:
        # update existing streak
        streak = Streak.query.filter(Streak.streak_id == streak_id).one()
        streak.end_success = success_id

    db.session.add(streak)
    db.session.commit()


def dates_same(first_datetime, second_datetime, tz):
    """ checks if two date are the same.  Returns True if so and False if not """

    first_datetime = arrow.get(first_datetime)
    second_datetime = arrow.get(second_datetime)

    if (first_datetime.to(tz)).date() == (second_datetime.to(tz)).date():
        return True
    else:
        return False

def dates_consecutive(first_datetime, second_datetime, tz):
    """ checks if two date are consecutive.  Returns True if so and False if not """

    first_datetime = arrow.get(first_datetime)
    second_datetime = arrow.get(second_datetime)

    diff = (first_datetime.to(tz)).date() - (second_datetime.to(tz)).date()
    
    if diff.days == -1:
        return True
    else:
        return False

def dates_same_or_consecutive(first_datetime, second_datetime, tz):
    """ checks if two dates are the same or consecutive"""

    first_datetime = arrow.get(first_datetime)
    second_datetime = arrow.get(second_datetime)

    if (dates_same(first_datetime, second_datetime, tz) 
        or dates_consecutive(first_datetime, second_datetime, tz)):
        return True
    else:
        return False









