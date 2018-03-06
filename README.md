# ratestask
Rates Task

Learned Python and PostgreSQL in 2 days.

I followed this tutorial to get started:

https://scotch.io/tutorials/build-a-restful-api-with-flask-the-tdd-way

As for Sunday, 4th of March I have done the following:
1. Completed GET API
2. Started POST API
3. Wrote 12 test cases that run successfully

Instructions to setup environment:
1. Install Python3 (I installed Anaconda for MasOS)
2. Install Flask
3. Run this: export FLASK_APP="run.py" (I used Virtualenv from the tutorial)
4. Install PostgreSQL
5. Install Psycopg2

In order to run the tests run the following command:

python test_rates.py

To run the application:

flask run

To test GET request run:

curl http://127.0.0.1:5000/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main