""" test file to work out schedule functionality """

import os
from twilio.rest import Client
import schedule
import time

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
messaging_service_sid = os.environ["TWILIO_MESSAGING_SERVICE_SID"]
twilio_from = os.environ["TWILIO_FROM_NUMBER"]
twilio_to = os.environ["TWILIO_TEST_TO_NUMBER"]
client = Client(account_sid, auth_token)


def test_nudges():
    """ send reminders sms messages to every user that should receive at that hour 
    to test: sending 1 test message every minute while running flask app """

    message = client.messages.create(
        messaging_service_sid=messaging_service_sid,
        to=twilio_to,
        from_=twilio_from,
        body="if you receive this text - then the scheduling task works!")

    print "the scheduling task test_nudges ran!"
    print "time run:" + str(time.time() - start_time)
    print(message.sid)

schedule.every(1).minutes.do(job)


while True:
    schedule.run_pending()
    time.sleep(1)
