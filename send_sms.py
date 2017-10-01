import os
from twilio.rest import Client
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

    message = client.messages.create(
        messaging_service_sid=messaging_service_sid,
        to=twilio_to,
        from_=twilio_from,
        body="if you receive this text - then the scheduling task works!")

    print "the scheduling script ran"
    print(message.sid)

    # utc_now = arrow.utcnow()
    # hour = utc_now.hour


    # users = # database query for anyone with time.hour == hour in USER-HABITS time variable joined with user-habit table

    # for user in users: 
    #     name = user.name
    #     mobile = user.mobile
    #     habit = Create_habit_description
    #     message = client.messages.create(
    #         messaging_service_sid=messaging_service_sid,
    #         to="{}".format(,
    #         from_="+14158539047",
    #         body="It's that time, {}.  Did you {}?".format(name, habit)
    #media_url=['https://demo.twilio.com/owl.png', 'https://demo.twilio.com/logo.png']
    # )

    # print(message.sid)



    ##########################

    # attributes available on message objects ... likely ones I'll use: 
    #     message.date_created
    #     message.sid
    #     message.to
    #     message.from_
    #     message.body
    #     message.direction
    #     message.status
    #     message.error_message

    # also available, 

    # message.num_segments
    # message.subresource_uris
    # message.date_updated
    # message.price
    # message.subresource_uri
    # message.account_sid
    # message.num_media
    # message.messaging_service_sid
    # message.date_sent <-- none for my message ... ?
    # message.price_unit
    # message.api_version








