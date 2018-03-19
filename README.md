# Description

App Engine App that can capture phone numbers and broadcast messages

# Setup

1. Clone repo
2. `pip install -r requirements.txt -t libs/`
3. `touch env_variables.py`

Add your env_variables.py file with the details filled from twilio

    ```
    ACCOUNT_SID=""
    AUTH_TOKEN=""
    NUMBER_SID=""
    SERVICE_NUMBER=""
    ```

4. run `dev_appserver.py app.yaml` and go to http://localhost:8080/ to see the app running.
5. If you deploy it to Google App Engine, you can have people text your SERVICE_NUMBER and it'll write it to the database. Any messages then sent via `/broadcast` will be sent to all people in the database.


