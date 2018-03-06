# ratestask
Rates Task

# Development section

Learned Python and PostgreSQL in 2 days.

I followed this tutorial to get started:

https://scotch.io/tutorials/build-a-restful-api-with-flask-the-tdd-way

As for Sunday, 4th of March I have done the following:
1. Completed GET API
2. Started POST API
3. Wrote 12 test cases that run successfully

Today, Tuesday, 6th of March completed the *Development Task*

Spent 1/2 a day
1. Refactored the code in accordance with OOP (only exception handling part caused some trouble, couldn't correctly hide the logic inside a class)
2. Used batch insert for adding the records into the table (COPY could be used with storing the rows in memory)
3. 16 unit tests ran successfully

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

# Theoretical section

## How would you design the system?

In my opinion, a table that is used to insert data into should be kept as small as possible,
since we require high performance for our *INSERT* statements.

I would keep only data for the last couple of weeks or even days as business requirements state.

The historical data should be kept in another database with main focus on reads, i.e. *SELECT* statements.
The purpose of this second database is to provide analytical information for our end users.

By having to databases with different purposes would help us to separate logic and allow us to tailor the databases for our needs.
So, the first database is OLTP database it can be SQL relational database or NoSQL database.

I would use a NoSQL as an OLTP database with insert, update, delete queries,
since it is better when you have to regularly insert and delete a lot of records at once.

Also NoSQL database would be better to horizontally scale by sharding.
The database can be partitioned in case of using SQL relational database as well, but it causes more burden and is not so straightforward.
Relational databases usually scale vertically, which is not cost effective.

I would use queues like RabitMQ in order to handle all the incoming data batches,
so that each batch id is stored in a queue, and batches are processed by fetching their ids from the queue.
The queue can provide us kind of fault tolerancy in case of sudden peak load,
and nothing would be lost or dropped when all the batch proccessing instances busy.

To handle the application logic I would use a fleet of instances that can horizontally scale.
I would align the scaling logic with the queue length metric, whenever the number of batch ids in the queue are higher
than a treshold I would launch a new instance to process the batches.

If the data from the OLTP database is read, then I would create read replicas in case of relational databases.
Also I would use in memory caching like Redis for frequent SELECT queries.

## What parts of the system do you expect to become the bottlenecks as the load grows?

As load grows the batch processing instances, database itself, network throughput I expect to become bottlenecks.
I would think about CPU, Memory, Disk I/O and Throughput and Network performance.

## How can those bottlenecks be addressed in the future?

As I mentioned above this issues can be addressed by using horizontally scalable design for batch processing instances,
by splitting the database for historical and operational needs.

Also caching, queues and maintaining small size of the table would help to address these bottlenecks.

## Additional questions

1. The batch updates have started to become very large, but the
   requirements for their processing time are strict.

Being a cloud architect I would definitely build my environment in AWS.
My architecture could handle very large batch updates.
I could change the type of instance, i.e. scale vertically to handle a larger batch.


2. Code updates need to be pushed out frequently. This needs to be
   done without the risk of stopping a data update already being
   processed, nor a data response being lost.

The bottleneck is the batch processing logic, as the instances may be unable to handle new batches properly.
They might drop them and do not process.
As I mentioned above queues can be used for this purpose.
So, the batch can wait or be processed in parallel.

3. For development and staging purposes, you need to start up a number
   of scaled-down versions of the system.

My architecture when I would use horizontally scalable batch processing instances could be scaled down very easily.
There is no problem to scale them down, I could change the instance type to a cheaper one and even one instance
would be enough for DEV and QA environments.