""" Utility file to seed habot database with basic static data and test user data """

from sqlalchemy import func
from model import User, UserProfile, ProfileFactor, BreakHabit, CreateHabit, ReplaceHabit, UserHabit, Success, Streak, Coach
from model import connect_to_db, db
from server import app


def load_users():
    """ load test users into database """

    #delete any data that is in the table
    User.query.delete()

    #open and parse users.csv file
    for row in open("data/users.csv"):
        row = row.rstrip()
        user_id, name, mobile, is_partner = row.split(",")
   
        # create user
        user = User(user_id=user_id, name=name, mobile=mobile, is_partner=False)

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
        fields = [field if field != 'null' else None for field in row.split(",")]
        (create_habit_id, create_habit_title, 
        create_habit_description, create_habit_hour) = fields

        #create habit
        habit = CreateHabit(create_habit_id=create_habit_id,
            create_habit_title=create_habit_title,
            create_habit_description=create_habit_description, 
            create_habit_hour=create_habit_hour)

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
        current, tz, utc_time, utc_hour, partner_id, longest_streak, 
        total_days) = fields

        #create user-habit
        user_habit = UserHabit(habit_id=habit_id, user_id=user_id,
            create_habit_id=create_habit_id, break_habit_id=break_habit_id,
            current=current, tz=tz, utc_time=utc_time, utc_hour=utc_hour,
            partner_id=partner_id, longest_streak=longest_streak, total_days=total_days)

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

    #open and parase streaks file
    for row in open("data/streaks.csv"):
        row = row.rstrip()
        fields = [field if field !='NULL' else None for field in row.split(",")]
        streak_id, habit_id, days, start, end = fields

        #create streak
        streak = Streak(streak_id=streak_id, habit_id=habit_id, days=days, start=start, end=end)

        #add straek
        db.session.add(streak)

    #submit streaks
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
    load_users()
    load_create_habits()
    load_user_habits()
    load_successes()
    load_streaks()
    set_val_user_id()
    set_val_success_id()
    set_val_habit_id()