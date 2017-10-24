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
import emoji

### TWILIO HELPERS ###

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
messaging_service_sid = os.environ["TWILIO_MESSAGING_SERVICE_SID"]
twilio_from = os.environ["TWILIO_FROM_NUMBER"]
twilio_to = os.environ["TWILIO_TEST_TO_NUMBER"]
client = Client(account_sid, auth_token)

### EMOJIS ###

thumbs_up = emoji.emojize(":thumbsup:", use_aliases=True)
folded_hands = emoji.emojize(":folded_hands:", use_aliases=True)
wave = emoji.emojize(":wave:", use_aliases=True)
robot = emoji.emojize(":robot_face:", use_aliases=True)
purple_heart = emoji.emojize(":purple_heart:", use_aliases=True)
party_popper = emoji.emojize(":party_popper:", use_aliases=True)
trophy = emoji.emojize(":trophy:", use_aliases=True)
reminder_ribbon = emoji.emojize(":reminder_ribbon:", use_aliases=True)
alarm_clock = emoji.emojize(":alarm_clock:", use_aliases=True)
chart_increasing = emoji.emojize(":chart_increasing:", use_aliases=True)
oncoming_fist = emoji.emojize(":oncoming_fist:", use_aliases=True)


### VERIFICATION CODE HELPERS ###

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


### SENDING MESSAGES HELPERS ###

def send_welcome_msg(user_id):
    """ sends very first message after user registers """

    user = User.query.filter(User.user_id == user_id).first()
    mobile = user.mobile
    name = user.name

    message = client.messages.create(
        messaging_service_sid=messaging_service_sid,
        to=mobile,
        from_=twilio_from,
        body="Hello, {}! ".format(name) + "Habot here." + robot + purple_heart \
        + " I feel honored you've choosen me to help you form new habits." 
    + folded_hands + "You can create a new habit with ~ 21 days of consistent effort.\
    That's why I help you track 'streaks' (consecutive days of success).\
    21 days may feel like a lot but just think of it as 7 three-day-streaks" + thumbs_up +
    " I can't wait to see what you habituate!")

    print "welcome message sent!"
    print(message.sid)


def send_instruction_msg(user_id):
    """ sends very first message after user registers """

    user = User.query.filter(User.user_id == user_id).first()

    mobile = user.mobile
    name = user.name

    message = client.messages.create(
        messaging_service_sid=messaging_service_sid,
        to=mobile,
        from_=twilio_from,
        body="Here is some helpful information on how to interact with me:")

    print "instruction message sent"
    print(message.sid)


def send_habit_intro_msg(user_id):
    """ sends first habit intro message """

    user = User.query.filter(User.user_id == user_id).first()
    mobile = user.mobile
    name = user.name
    habit = UserHabit.query.filter(UserHabit.user_id == user_id, UserHabit.current == True).first()
    habits = UserHabit.query.filter(UserHabit.user_id == user_id).all()
    habit_title = habit.habit.title #TODO: change relationship to be create_habit
    habit_hour = get_local_habit_hour(habit.habit_id)

    reminder = None
    if len(habits) == 1:
        reminder = "Let me know when you're successful and I'll track your \
    progress." + chart_increasing + "To help me recognize your success, put a #\
    in front of your msg like this: '#I did it, Habot!'' or '#yes!'" + oncoming_fist
    
    else: 
        reminder = "You know the drill, don't forget the #!"

    message = client.messages.create(
        messaging_service_sid=messaging_service_sid,
        to=mobile,
        from_=twilio_from,
        body="I see you've committed to {}. What a wonderful thing to habituate in your life, {}!\
    Every day at {} I'll send you a reminder. ".format(habit_title, name, habit_hour) + alarm_clock + reminder)

    print "habit_intro_msg sent"
    print(message.sid)


def send_daily_msg():
    """ sends daily msg from Habot - either daily reminder or deactivation"""

    # current_utc_date = arrow.utcnow()
    ### for testing: 
    current_utc_hour = 18
    current_utc_date = (arrow.utcnow()).replace(hour=18)
  

    # if user has been inactive for 7 days, send deactivation instead of reminder:
    send_pause_msgs() 

    habits = UserHabit.query.filter(UserHabit.current == True, UserHabit.active == True).all()
    # TODO ... optimize so you're only querying for exact hour, not all active habits.

    for habit in habits:
        habit_id = habit.habit_id
        habit_title = habit.habit.title
        to = habit.user.mobile
        name = habit.user.name
        last_success = find_last_success(habit_id)
        tz = habit.user.tz
        if habit.utc_time.hour == 18:
            msg = stats_msg(habit_id)

            # don't send the message if the user already tracked a success today
            if not (last_success != None and (dates_same(last_success.time, current_utc_date, tz))):

                message = client.messages.create(
                messaging_service_sid=messaging_service_sid,
                to=to,
                from_=twilio_from,
                body=  wave + ",{}! Habot here. You're working on {}. {}\
            Let me know when you're successful & remember the #.\
            I believe in you!".format(name, habit_title, msg))

                print "message was: {}".format(message)
                print(message.sid)

    print "the scheduling script ran @ {}".format(time.time())


def stats_msg(habit_id):
    """ analyzes a user's stats for a given habit and returns the most
    motivating message to include in the daily msg from Habot"""

    stats = get_stats(habit_id)
    three_day_streaks = stats['three_day_streaks']
    current_three_day = stats['current_three_day_streak']

    if three_day_streaks > 1:
        streak_msg = "You have {} three-day-streaks".format(three_day_streaks)
    elif three_day_streaks == 1:
        streak_msg = "Way to go! You've alredy collected your first three-day-streak!"
    else:
        streak_msg = "Let's help you earn your first three-day-streak with a success today."

    if current_three_day == 0:
        streak_prompt = "Start a new three-day-streak with a success today!"
    elif current_three_day == 1:
        streak_prompt = "Let's keep your streak going with a success today!"
    elif current_three_day == 2:
        streak_prompt = "You're one success away from a new three day streak!"
    else:
        streak_prompt = " "

    msg = streak_msg + streak_prompt

    return msg


def congrats_msg(user_id):
    """ analyzes a user's stats after a success to customize the msg from 
    Habot """

    habit_id = get_current_habit_id(user_id)
    name = (get_user(habit_id)).name
    stats = get_stats(habit_id)

    three_day_streaks = stats['three_day_streaks']
    current_three_day = stats['current_three_day_streak']

    confirm_msg = "I've tracked that for you, {}. ".format(name)

    if current_three_day == 0:
        if three_day_streaks == 1:
            stats_msg = "Way to go! You've collected your first three-day-streak!"
        elif three_day_streaks == 7:
            stats_msg = party_popper + "Congrats! You now have 7 total 3-day-streaks!\
    I'm in awe of you, {}. Most people that reach this point start feeling their new habit stick.\
    But I'll keep tracking your successes for as long as you'd like. See how far you can get!".format(name) + trophy

        else:
            stats_msg = "That's a new three-day-streak! {} in total now!".format(three_day_streaks)
    elif current_three_day == 1:
        if three_day_streaks == 0:
            stats_msg = "Great job! You're on your way to your first three-day-streak! I'll check back in tomorrow."
        else:
            stats_msg = "You're now on day 1 of your next three-day-streak! I believe in you!".format(three_day_streaks)
    elif current_three_day == 2:
        if three_day_streaks == 0:
            stats_msg = "You're one success away from a new three-day-streak!"
        else:
            stats_msg = "You're one success away from your next three-day-streak.\
            Make it {} in total!".format(three_day_streaks + 1)

    msg = confirm_msg + stats_msg

    return msg


def send_pause_msgs():
    """ send deactivations to any user who hasn't been active in 7 days """

    # current_utc_date = arrow.utcnow()
    #for testing:
    current_utc_hour = 18
    current_utc_date = (arrow.utcnow()).replace(hour=18)

    # find users who would receive a daily_msg at the given hour
    habits = UserHabit.query.filter(UserHabit.current == True,
                                    UserHabit.active == True).all()

    for habit in habits:

        tz = habit.user.tz

        last_success = find_last_success(habit.habit_id) #Success object

        # if it's been more than 7 days since last_success or habit creation date:
        if (
            (last_success and (dates_week_apart(last_success.time, current_utc_date, tz)))
                or ((not last_success) and dates_week_apart(habit.utc_time, current_utc_date, tz))
                ):

            pause_habit(habit.habit_id)

            to = habit.user.mobile
            name = habit.user.name

            message = client.messages.create(
                messaging_service_sid=messaging_service_sid,
                to=to,
                from_=twilio_from,
                body="{}, I noticed you haven't responded in a while.\
            I've gone ahead and paused this habit for you.\
            If/when you're ready to start working on this again just say 'unpause'".format(name))


### HABIT MANAGEMENT HELPERS ###


def pause_habit(habit_id):
    """ deactivates a user_habit so they don't receive messages from Habot anymore """

    habit = UserHabit.query.filter(UserHabit.habit_id == habit_id).first()
    habit.active = False
    db.session.add(habit)
    db.session.commit()
    print "habit paused (active == False)"


def pause_msg(user_id):
    """ returns a puase message for Habot to send"""


def unpause_habit(user_id):
    """ unpauses a habit that has been paused after user reponds to habit they want to unpause"""

    #TODO: pull out message return to a seperate function.

    habit_id = get_current_habit_id(user_id)
    habit = UserHabit.query.filter(UserHabit.habit_id == habit_id).first()
    title = habit.habit.title
    name = habit.user.name
    habit.active = True

    db.session.add(habit)
    db.session.commit()

    msg = "Ok, great {}, I'm glad to hear you want to keep working on {}.\
    I've unpaused it for you and will continue sending reminders.".format(name, title)

    print "habit unpaused (active == True)"
    return msg


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


### USER MANAGEMENT HELPERS ###


def create_user_return_id(name, mobile, tz):
    """ creates a new user and returns the assigned user_id"""

    user = User(name=name, mobile=mobile, tz=tz)
    db.session.add(user)
    db.session.commit()
    user = User.query.filter(User.mobile == mobile).first()
    user_id = user.user_id

    return user_id


def get_user_id(mobile):
    """ returns the user_id for a user given a phone number"""

    user = User.query.filter(User.mobile == mobile).first()
    user_id = user.user_id
    return user_id


def get_current_habit_id(user_id):
    """ finds the current habit for a user """

    habit = UserHabit.query.filter(UserHabit.current == True, UserHabit.user_id == user_id).one()
    habit_id = habit.habit_id
    return habit_id


def get_user(habit_id):
    """ returns the User object for any habit_id """

    habit = UserHabit.query.filter(UserHabit.habit_id == habit_id).one()
    user = habit.user
    return user


### PROFILE MANAGEMENT HELPERS ###


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


### RECOMMENDATION HELPERS ###


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

        return ranked_habits
        # a list of CreateHabit objects

    else:
        print "recommending deafult habits"
        return habits


### DATETIME HELPERS ####


def get_local_hour(tz):
    """ returns the curernt local hour in a time zone"""

    time_utc = arrow.utcnow()
    time_local = time_utc.to(tz)
    local_hour = time_local.hour
    return local_hour


def get_local_habit_hour(habit_id):
    """ returns the habit hour in the user's local time
    in a string with format '7 am' """

    habit = UserHabit.query.filter(UserHabit.habit_id == habit_id).first()
    habit_time = arrow.get(habit.utc_time)
    tz = habit.user.tz
    habit_time_local = habit_time.to(tz)
    local_habit_hour = habit_time_local.format('h a')
    return local_habit_hour


def get_utc_hour():
    """ returns the utc hour of the current time"""

    time_utc = arrow.utcnow()
    utc_hour = time_utc.hour
    return utc_hour


def dates_same(first_datetime, second_datetime, tz):
    """ checks if two date are the same.  Returns True if so and False if not """

    first = arrow.get(first_datetime)
    second = arrow.get(second_datetime)
    # second == most recent

    if (first.to(tz)).date() == (second.to(tz)).date():
        return True
    else:
        return False


def dates_consecutive(first_datetime, second_datetime, tz):
    """ checks if two date are consecutive.  Returns True if so and False if not """

    first = arrow.get(first_datetime)
    second = arrow.get(second_datetime) 
    # second == most recent

    diff = (first.to(tz)).date() - (second.to(tz)).date()

    if diff.days == -1:
        return True
    else:
        return False


def dates_same_or_consecutive(first_datetime, second_datetime, tz):
    """ checks if two dates are the same or consecutive"""

    first = arrow.get(first_datetime)
    second = arrow.get(second_datetime)
    # second == most recent

    if (dates_same(first, second, tz) 
        or dates_consecutive(first, second, tz)):
        return True
    else:
        return False


def dates_week_apart(first_datetime, second_datetime, tz):
    """ checks if two dates are more than a week apart"""

    first = arrow.get(first_datetime)
    second = arrow.get(second_datetime)
    # second == most recent

    diff = (first.to(tz)).date() - (second.to(tz)).date()

    if diff.days < -7:
        return True
    else:
        return False


### COUNTRY & TIMEZONE HELPERS ###


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


### SUCCESS & STREAK MANAGEMENT HELPERS ####

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
            if dates_same(streak_start, streak_end, tz):
                streak_length = 1
            else: 
                streak_length = -((streak_start.date() - streak_end.date()).days)
            
            # determine if it's the longest streak
            if streak_length > stats['longest_streak']:
                stats['longest_streak'] = streak_length

            # determine if it classifies as a three_day streak
            if streak_length / 3 > 0:
                stats['three_day_streaks'] += (streak_length / 3)
      
            # find the last streak
            if streak.end_id == last_success_id:
                # if end of last streak == today or yesterday
                # OR if end of last streak AND habit creation date are the same
                if ((dates_same_or_consecutive(last_success_time, current_time, tz)) or (dates_same(habit.utc_time, last_success_time, tz))):
                    stats['current_streak'] = streak_length
                    stats['potential_streak'] = streak_length
                    # if end of last streak == yesterday:
                    if dates_consecutive(last_success_time, current_time, tz):
                        stats['potential_streak'] = streak_length + 1
                # if end of last streak != today or yesterday:
                else:
                    stats['current_streak'] = 0
                    stats['potential_streak'] = 1

        # find the current_three_day streak (should only be 0, 1 or 2) ...
        if stats['current_streak'] >= 3:
            stats['current_three_day_streak'] = stats['current_streak'] - (3 * stats['three_day_streaks'])
        else:
            stats['current_three_day_streak'] = stats['current_streak']
    
    else:
        # if no successes ... 
        stats['longest_streak'] = 0
        stats['current_streak'] = 0
        stats['three_day_streaks'] = 0
        stats['potential_streak'] = 1
        stats['current_three_day_streak'] = 0

    return stats


def get_graph_stats(stats):
    """ provides a dictionary to jsonify in flask route that supports
     d3 dashboard graph dynamic configuration """

    graph_stats = {}
    num_streaks = stats['three_day_streaks']
    num_days = stats['current_three_day_streak']

    graph_stats['num_streaks'] = []
    graph_stats['num_streaks_colors_domain'] = []
    graph_stats['num_streaks_colors_range'] = []
    graph_stats['num_day_colors'] = []
    graph_stats['num_day_strokes'] = []
    graph_stats['num_streaks_stroke'] = []


    # dictionary of color progression to reference. 
    # outter circle (num_days) segments fill to color of the 'next' 3-day streak value
    colors = {  0 : 'white',     
                1 : '#DFF2B4',
                2 : '#AEDFB6',
                3 : '#79CBBC',
                4 : '#41B2C2',
                5 : '#228BBC',
                6 : '#2258A5',
                7 : '#20388F',
                8 : '#182C78',
                9 : '#081D57'
            }
    color = colors[num_streaks + 1]

    # configure num segments and colors for inner circle (num_streaks)

    if num_streaks == 0:
    # scenario of 0x3-day streaks:
        new = {}
        new['label'] = '0x3-day'
        new['count'] = 1
        graph_stats['num_streaks'].append(new)
        graph_stats['num_streaks_colors_domain'].extend(['0x3-day'])
        graph_stats['num_streaks_colors_range'].extend(['#FCFCFC'])
        graph_stats['num_streaks_stroke'].extend(['#D8D8D8'])

    else:

        for i in range(1, num_streaks + 1):
            new = {}
            new['label'] = '{}x3-day'.format(i)
            new['count'] = 1
            graph_stats['num_streaks'].append(new)

        graph_stats['num_streaks_colors_domain'].extend(['1x3-day', '2x3-day', '3x3-day', '4x3-day', '5x3-day', '6x3-day', '7x3-day', '8x3-day', '9x3-da7'])
        graph_stats['num_streaks_colors_range'].extend(['#DFF2B4', '#AEDFB6', '#79CBBC', '#41B2C2', '#228BBC', '#2258A5', '#20388F','#182C78','#081D57'])
        graph_stats['num_streaks_stroke'].extend(['transparent'])

    # configure color and stroke for outter circle (num_days / 3 in 3-day streak)
    if num_days == 1:
        graph_stats['num_day_colors'].extend(
            ["{}".format(color), 'transparent', 'transparent'])
        graph_stats['num_day_strokes'].extend(
            ['transparent', '#FCFCFC', '#FCFCFC'])

    elif num_days == 2:
        graph_stats['num_day_colors'].extend(
            ["{}".format(color), "{}".format(color), 'transparent'])
        graph_stats['num_day_strokes'].extend(
            ['transparent', 'transparent', '#FCFCFC'])

    elif (num_days == 0) and (num_streaks == 0):
    # scenario of no data:
        graph_stats['num_day_colors'].extend(
            ['#FCFCFC', '#FCFCFC', '#FCFCFC'])
        graph_stats['num_day_strokes'].extend(
            ['#D8D8D8', '#D8D8D8', '#D8D8D8'])

    elif num_days == 0:
        graph_stats['num_day_colors'].extend(
            ['transparent', 'transparent', 'transparent'])
        graph_stats['num_day_strokes'].extend(
            ['#FCFCFC', 'transparent', 'transparent'])

    print stats['current_three_day_streak']
    return graph_stats


def process_success(user_id, success_time):

    # get User and user's timezone
    user = User.query.filter(User.user_id == user_id).first()
    tz = user.tz
    mobile = user.mobile

    # get user's current habit id
    # habit = UserHabit.query.filter(UserHabit.current == True, UserHabit.user_id == user_id).one()
    habit_id = get_current_habit_id(user_id)

    last_success = find_last_success(habit_id)

    # determine if streak
    streak_id = get_streak_id(habit_id, success_time)
    
    if last_success:
        last_time = last_success.time

        if dates_same(success_time, last_time, tz):
            print "date same as last time - no success processed"
            return None

    if streak_id == None or last_success == None: 
        # create success and create sterak
        success_id = add_success_get_id(habit_id, mobile, success_time)
        streak_update(habit_id, streak_id, success_id)
        print "new streak added"
        return success_id

    if streak_id:
        # create success and update streak
        success_id = add_success_get_id(habit_id, mobile, success_time)
        streak_update(habit_id, streak_id, success_id)
        print "existing streak updated"
        return success_id

   
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

    if last_success:
        return last_success
    else:
        return None


def get_streak_id(habit_id, success_time):
    """ determines if a new success is part of an existing streak or not.
    returns streak_id or none if success is not part of a streak """

    user_habit = UserHabit.query.filter(UserHabit.habit_id == habit_id).first()

    tz = user_habit.user.tz

    last_success = find_last_success(habit_id)
    # alt to find tz = last_success.habit.user.tz

    if last_success:
        last_success_id = last_success.success_id
        last_success_time = arrow.get(last_success.time)
        last_success_local = last_success_time.to(tz)
                
        # if existing streak
        if dates_consecutive(last_success_time, success_time, tz):
            streak = Streak.query.filter(Streak.end_id == last_success_id).first()
            return streak.streak_id
        else:
            return None
    else:
        return None


def streak_update(habit_id, streak_id, success_id):
    """ creates or updates a streak """

    print "trying to update streak"
    print "values: habit_id: {}, streak_id: {}, success_id: {}".format(habit_id,
        streak_id, success_id)

    if streak_id is None:
        # create new streak
        streak = Streak(habit_id=habit_id, start_id=success_id, end_id=success_id)

    else:
        # update existing streak
        streak = Streak.query.filter(Streak.streak_id == streak_id).one()
        streak.end_id = success_id

    db.session.add(streak)
    db.session.commit()


def connect_to_db(app):
    """Connect the database to the Flask app."""

    # Configure to use the PstgreSQL database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///Habot'
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."









