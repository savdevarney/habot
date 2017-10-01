from twilio.rest import Client
import os


account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]

client = Client(account_sid, auth_token)

messages = client.messages.list()
    

# client.messages.list(to='+18028253270')
