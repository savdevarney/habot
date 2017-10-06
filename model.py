"""Models and database functions for Habitify db."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


##############################################################################
#ORM

class User(db.Model):
    """primary attributes about a user."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    is_partner = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        """ shows information about user """

        return "< user_id={} mobile={} name={}>".format(
            self.user_id, self.mobile, self.name)


class UserProfile(db.Model):
    """profile of user factors selected at onboarding"""

    __tablename__ = "user_profiles"

    user_profile_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile_factors.profile_id'), nullable=False)

    def __repr__(self):
        """ shows information about association """

        return "< association: user_id={} profile_id={}>".format(
            self.user_id, self.profile_id)


class ProfileFactor(db.Model):
    """ profile attributes a user selects as true during onboarding """

    __tablename__ = "profile_factors"

    profile_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        """ shows information about profile factor """

        return "< factor: profile_id={} description={}>".format(
            self.profile_id, self.factor_description)


class BreakHabit(db.Model):
    """ habits a user can select to break """

    __tablename__ = "break_habits"

    break_habit_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    break_habit_title = db.Column(db.String(50), nullable=False)
    break_habit_description = db.Column(db.String(100), nullable=False)
    break_habit_hour = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        """ shows information about the habit """

        return "< BreakHabit: break_habit_id={} description={}>".format(
            self.break_habit_id, self.break_habit_title)


class CreateHabit(db.Model):
    """ habits a user can select to create """

    __tablename__ = "create_habits"

    create_habit_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_habit_title = db.Column(db.String(50), nullable=False)
    create_habit_description = db.Column(db.String(100), nullable=False)
    create_habit_hour = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        """ shows information about the habit """

        return "< CreateHabit: create_habit_id={} description={}>".format(
            self.create_habit_id, self.create_habit_title)


class ReplaceHabit(db.Model):
    """Tracks associations between break habits and the create habits that can replace them"""

    __tablename__ = "replace_habits"

    association_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    break_habit_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    create_habit_id = db.Column(db.Integer, db.ForeignKey('profile_factors.profile_id'), nullable=False)

    def __repr__(self):
        """ shows information about association """

        return "< association: break_habit_id={} create_habit_id={}>".format(
            self.break_habit_id, self.create_habit_id)


class UserHabit(db.Model):
    """ information about the habit a user selected and is working on tracking """

    __tablename__ = "user_habits"

    habit_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    create_habit_id = db.Column(db.Integer, db.ForeignKey('create_habits.create_habit_id'), nullable=False)
    break_habit_id = db.Column(db.Integer, db.ForeignKey('break_habits.break_habit_id'), nullable=True)
    current = db.Column(db.Boolean, nullable=False)
    tz = db.Column(db.String(15), nullable=False)
    utc_time = db.Column(db.DateTime(timezone=True), nullable=False)
    utc_hour = db.Column(db.Integer, nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    longest_streak = db.Column(db.Integer, nullable=False, default=0)
    total_days = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        """ shows information about a user habit """

        return "<habit: habit_id={}, user_id={}, current={}".format(
            self.habit_id, self.user_id, self.current)

    user = db.relationship('User', foreign_keys="UserHabit.user_id", backref='habit')

    habit = db.relationship('CreateHabit', foreign_keys="UserHabit.create_habit_id", backref='userhabits')


class Success(db.Model):
    """ tracks successes (successes in working toward habit) """

    __tablename__ = "successes"

    success_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('user_habits.habit_id'), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    time = db.Column(db.DateTime(timezone=True), nullable=False)

    def __repr__(self):
        """ shows information about a success"""

        return "<success: habit_id={}, time={}>".format(
            self.habit_id, self.time)

    habit = db.relationship('UserHabit', backref='successes')


class Streak(db.Model):
    """stores information about streaks"""

    ___tablename___ = "streaks"

    streak_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('user_habits.habit_id'), nullable=False)
    days = db.Column(db.Integer, nullable=False)
    start = db.Column(db.DateTime(timezone=True), nullable=False)
    end = db.Column(db.DateTime(timezone=True), nullable=True)

    def __repr__(self):
        """ shows information about a streak"""

        return "<streak: habit_id={}, days={}>".format(
            self.habit_id, self.days)

    habit = db.relationship('UserHabit', backref='streaks')


class Coach(db.Model):
    """ stores information about coach personalities """

    __tablename__ = "coaches"

    coach_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    coach_name = db.Column(db.String, nullable=False)
    coach_description = db.Column(db.String, nullable=False)

    def __repr__(self):
        """ shows information about a coach"""

        return "<coach: coach_id={}, description={}".format(
            self.coach_id, self.coach_description)





##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to the Flask app."""

    # Configure to use the PstgreSQL database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///habot'
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

    # create tables
    # db.create_all()
