""" Utility file to seed habot database with basic static data and test user data """

from sqlalchemy import func
from model import User, UserProfile, ProfileFactor, BreakHabit, CreateHabit, ReplaceHabit, UserHabit, Success, Coach
from model import connect_to_db, db
from server import app


def load_users():
    """ load test users into database """

    #delete any data that is in the table
    User.query.delete()

    #open and parse users.csv file
    for row in open("users.csv"):
        row = row.rstrip()
        user_id, name, mobile, is_partner = row.split(",")
   
        # create user
        user = User(name=name, mobile=mobile, is_partner=False)

        # add to session
        db.session.add(user)

    # submit users
    db.session.commit()


def load_create_habits():
    """ load habit library into database """

    #delete any data that is in the table
    CreateHabit.query.delete()

    #open and parse habit file
    for row in open("create-habits.csv"):
        row = row.rstrip()
        create_habit_id, create_habit_title, 
        create_habit_description, create_habit_hour = row.split(",")

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
    for row in open("user-habits.csv"):
        row = row.rstrip()
        habit_id, user_id, create_habit_id, break_habit_id,
        current, tz, time, utc_time, utc_hour, partner_id = row.split(",")

        #create user-habit
        user_habit = UserHabit(habit_id=habit_id, user_id=user_id,
            create_habit_id=create_habit_id, break_habit_id=break_habit_id,
            current=current, tz=tz, time=time, utc_time=utc_time, utc_hour=utc_hour,
            partner_id=partner_id)

        #add user_habit
        db.session.add(user_habit)

    #submit user_habits
    db.session.commit()



def load_successes():
    """ load test user success data into database """

    #delete any data that is in the table:
    Success.query.delete()

    #open and parse successes file
    for row in open("successes.csv"):
        row = row.rstrip()
        success_id, habit_id, mobile, time = row.split(",")

        #create success
        success = Success(success_id=success_id, habit_id=habit_id, time=time)

        #add success
        db.session.add(success)

    #submit success
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
    query = "SELECT setval('user-habits_habit_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # in case tables haven't been created, create them:
    db.create_all()

    # populate data into tables:
    load_users()
    load_habits()
    load_successes()
    set_val_user_id()
    set_val_success_id()
    set_val_habit_id()