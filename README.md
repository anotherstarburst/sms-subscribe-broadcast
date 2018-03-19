# Description

App Engine App that can capture phone numbers and broadcast messages. Written in a short space of 
time in aid of a hackathon. Ultimately was not used in said hackathon - but still works as designed.

# Requirements

- Python 2.7
- pip
- git
- Twilio Account
- SMS-capable twilio number

# Setup

1. Clone repo
2. `mkdir libs`
2. `pip install -r requirements.txt -t libs/`
3. `touch env_variables.py`

Add your env_variables.py file with the details filled from twilio

    ```
    ACCOUNT_SID="" # from your twilio account
    AUTH_TOKEN=""  # from your twilio account
    NUMBER_SID="" # SID of the twilio number you're using
    SERVICE_NUMBER="" # twilio number you want to use to send from
    ```

4. run `dev_appserver.py app.yaml` and go to http://localhost:8080/ to see the app running.
5. Go to http://localhost:8080/broadcast (you'll need to sign in as an admin user) to see broadcast screen with prefilled text boxes that send the messages.
5. If you deploy it to Google App Engine, you can have people text your SERVICE_NUMBER and it'll write it to the database. Any messages then sent via `/broadcast` will be sent to all people in the database.

