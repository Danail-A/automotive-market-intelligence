1. Connect to postgres using the command line and writing "sudo -u postgres psql".
2. Create a database - for our purposes we are going to use automotive_market_intellignce as the db name (CREATE DATABASE automotive_market_intelligence;).
3. Connect to the newly created db (\c automotive_market_intelligence)
4. Create 4 different schemas that we are going to use for different purposes
a. A Schema for the raw data - CREATE SCHEMA raw;
b. A schema for semi-transformed data - CREATE SCHEMA staging;
c. CREATE SCHEMA intermediate;
d. CREATE SCHEMA marts;
5. Create a user and password in order to connect to python (dbt) later as python needs permission to write into postgres.
