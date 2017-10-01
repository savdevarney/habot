""" test file to work out schedule functionality """

import os
from flask import Flask, request, render_template, session, redirect, jsonify, flash
from twilio.rest import Client
import schedule
import time

app = Flask(__name__)
app.secret_key = 'ABCSECRETDEF'

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
messaging_service_sid = os.environ["TWILIO_MESSAGING_SERVICE_SID"]
twilio_from = os.environ["TWILIO_FROM_NUMBER"]
client = Client(account_sid, auth_token)

def job():
    """ send reminders sms messages to every user that should receive at that hour 
    to test: sending 1 test message every minute while running flask app """

    message = client.messages.create(
        messaging_service_sid=messaging_service_sid,
        to="+18028253270",
        from_=twilio_from,
        body="if you receive this text - then the scheduling task works!")

    print "the scheduling script ran"
    print(message.sid)


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")
    schedule.every(1).minutes.do(job)
    while True: 
        schedule.run_pending()
        time.sleep(1)


    