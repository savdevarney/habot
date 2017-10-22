""" Utility file to seed habot database with basic static data and test user data """

from sqlalchemy import func
from model import (connect_to_db, db, User, CreateHabit, UserHabit, Success,
    Streak, Partner, Coach, UserProfile, FactorScore, Factor,
    FactorHabitRating)
from server import app


def load_users():
    """ load test users into database """

    #delete any data that is in the table
    User.query.delete()

    #open and parse users.csv file
    for row in open("data/users.csv"):
        row = row.rstrip()
        user_id, name, mobile, tz = row.split(",")
   
        # create user
        user = User(user_id=user_id, name=name, mobile=mobile, tz=tz)

        # add to session
        db.session.add(user)

    # submit users
    db.session.commit()


def load_create_habits():
    """ load habit library into database """

    #delete any data that is in the table
    CreateHabit.query.delete()

    #open and parse habit file
    for row in open("data/create-habits.csv"):
        row = row.rstrip()
        fields = [field if field != 'null' else None for field in row.split(',')]
        create_habit_id, title, description, hour = fields

        #create habit
        habit = CreateHabit(create_habit_id=create_habit_id,
            title=title,
            description=description,
            hour=hour)

        #add to session
        db.session.add(habit)

    #submit habits
    db.session.commit()


def load_user_habits():
    """ load habits test users have committed to """

    #delete any data that is in the table
    UserHabit.query.delete()

    #open and parse user-habits file
    for row in open("data/user-habits.csv"):
        row = row.rstrip()
        fields = [field if field != 'null' else None for field in row.split(",")]
        (habit_id, user_id, create_habit_id, break_habit_id,
        current, active, utc_time, partner_id) = fields

        #create user-habit
        user_habit = UserHabit(habit_id=habit_id, user_id=user_id,
            create_habit_id=create_habit_id, break_habit_id=break_habit_id,
            current=current, active=active, utc_time=utc_time, partner_id=partner_id)

        #add user_habit
        db.session.add(user_habit)

    #submit user_habits
    db.session.commit()



def load_successes():
    """ load test user success data into database """

    #delete any data that is in the table:
    Success.query.delete()

    #open and parse successes file
    for row in open("data/successes.csv"):
        row = row.rstrip()
        success_id, habit_id, mobile, time = row.split(",")

        #create success
        success = Success(success_id=success_id, habit_id=habit_id, mobile=mobile, time=time)

        #add success
        db.session.add(success)

    #submit successes
    db.session.commit()

def load_streaks():
    """ load test user streaks data into database """

    #delete any data that is in the table:
    Streak.query.delete()

    #open and parse streaks file
    for row in open("data/streaks.csv"):
        row = row.rstrip()
        fields = [field if field !='NULL' else None for field in row.split(",")]
        streak_id, habit_id, start_id, end_id = fields

        #create streak
        streak = Streak(streak_id=streak_id, habit_id=habit_id, start_id=start_id, end_id=end_id)

        #add streak
        db.session.add(streak)

    #submit streaks
    db.session.commit()

def load_factors():
    """ load the set of factors for users to rate """

    Factor.query.delete()

    #open and parse factors file
    for row in open("data/factors.csv"):
        row = row.rstrip()
        fields = row.split(",")
        factor_id, title, description = fields

        #create factor
        factor = Factor(factor_id=factor_id, title=title, description=description)

        #add factor
        db.session.add(factor)

    #submit factors
    db.session.commit()


def load_ratings():
    """ load the set ratings for each habit (how well they help a factor) """

    FactorHabitRating.query.delete()

    #open and parse factors file
    for row in open("data/factor-habit-ratings.csv"):
        row = row.rstrip()
        fields = row.split(",")
        create_habit_id, rating_1, rating_2, rating_3, rating_4, rating_5, rating_6 = fields

        #create ratings
        rating_1 = FactorHabitRating(create_habit_id=create_habit_id, factor_id=1, rating=rating_1)
        rating_2 = FactorHabitRating(create_habit_id=create_habit_id, factor_id=2, rating=rating_2)
        rating_3 = FactorHabitRating(create_habit_id=create_habit_id, factor_id=3, rating=rating_3)
        rating_4 = FactorHabitRating(create_habit_id=create_habit_id, factor_id=4, rating=rating_4)
        rating_5 = FactorHabitRating(create_habit_id=create_habit_id, factor_id=5, rating=rating_5)
        rating_6 = FactorHabitRating(create_habit_id=create_habit_id, factor_id=6, rating=rating_6)

        #add ratings
        db.session.add(rating_1)
        db.session.add(rating_2)
        db.session.add(rating_3)
        db.session.add(rating_4)
        db.session.add(rating_5)
        db.session.add(rating_6)

    #submit factors
    db.session.commit()



def set_val_user_id():
    """Set value for the next user_id after seeding database with test users"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

def set_val_success_id():
    """Set value for the next success_id after seeding database with test users"""

    # Get the Max success_id in the database
    result = db.session.query(func.max(Success.success_id)).one()
    max_id = int(result[0])

    # Set the value for the next success_id to be max_id + 1
    query = "SELECT setval('successes_success_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


def set_val_habit_id():
    """Set value for the next habit_id after seeding database with test users"""

    # Get the Max success_id in the database
    result = db.session.query(func.max(UserHabit.habit_id)).one()
    max_id = int(result[0])

    # Set the value for the next success_id to be max_id + 1
    query = "SELECT setval('user_habits_habit_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

def set_val_streak_id():
    """Set value for the next streak_id after seeding database with test users"""

    # Get the Max success_id in the database
    result = db.session.query(func.max(Streak.streak_id)).one()
    max_id = int(result[0])

    # Set the value for the next success_id to be max_id + 1
    query = "SELECT setval('streaks_streak_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # in case tables haven't been created, create them:
    db.create_all()

    # populate data into tables:
    load_create_habits()
    load_factors()
    load_ratings()
    # load_users()
    # load_user_habits()
    # load_successes()
    # load_streaks()

    # set_val_user_id()
    # set_val_success_id()
    # set_val_habit_id()
    # set_val_streak_id()
