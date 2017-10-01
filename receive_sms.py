import os
from flash import FLASK, request, redirect
from twilio.twiml.messaging_response import messaging_response


app=Flask(__name__)



@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    resp = MessagingResponse()

    resp.message("The reply we want to automatically send")

    return str(resp) #string representation of messaging_response

if __name__ == "__main__":
    app.run(debug=True)


#starts a webserver on localhost 5000 but we're going to use
# Ngrok to create an http tunnel to localhost 5000 so twilio
# can reach our server. 

#ngrok http 5000 ... will give us a URL that's publicly addressable 
# (the Forwarding URL) that we can take back over to the twilio
# phone numbers concsole and paste into 'a message comes in' webhook
