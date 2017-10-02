""" test file to work out schedule functionality """

import os
from flask import Flask, request, render_template, session, redirect, jsonify, flash
from twilio.rest import Client
import schedule
import time
from threading import Thread

app = Flask(__name__)
app.secret_key = 'ABCSECRETDEF'

start_time = time.time()

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

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)



@app.route('/', methods=['GET'])
def index():
    return '<html>test</html>'


if __name__ == "__main__":
    # set the schedule
    schedule.every(1).minutes.do(test_nudges)
    
    # establish the thread
    t = Thread(target=run_schedule)
    t.start()
    print "Start time: " + str(start_time)

    app.run(host="0.0.0.0", port=5000, debug=True)



    