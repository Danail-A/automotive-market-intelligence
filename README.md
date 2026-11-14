### The dataset can be found on this link:
https://www.kaggle.com/datasets/clkmuhammed/autoscout24-car-listings-dataset


# automotive-market-intelligence
A data project on second hand car prices. The idea is to get familiar with dbt and Airflow. 

1. We will collect the data and save it in the root directory.

2. Next step is going to be the simulated data ingestion. We are going to have a folder where we will be personally moving one of the files whenever we want. Hopefully we will have a script that goes through it and clones the data into postgres. I will be purposefully deleting something from the files in order to check if the ingestion step handles errors well and what it will raise as an issue.

3. Next is going to be the transformation - here we will use dbt to get the data from its raw values to something we might be able to work with down the line. 

4. We will then create the tests for the dbt models and then run them and the tests

5. We will see what we can do with the analytics ready data that comes after the transformations.

6. We will then send a report at the end based on every step of the way.

7. We will use Airflow to orchestrate the whole pipeline once we are done with the smaller steps.



Chat GPT steps: 

Step	Task	Result
1	Create PostgreSQL database and schemas
2	Import CSV into raw schema
3	Inspect and profile the data	
4	Install dbt
5	Initialize dbt project
6	Build first staging model
7	Add tests
8	Build intermediate models
9	Build marts
10	Answer business questions
11	Introduce Airflow


First steps to be done:

1. Create a database called car_intelligence.
2. Create the four schemas: raw, staging, intermediate, marts.
3. Import the CSV into raw.vehicle_listings.
4. Check that we have all the records and if there are any missing values.
5. Inspect the column types and identify which fields might need cleaning.
6. Create a simple test to check if all rows have been successfully copied into the db. Data quality tests will be done once we start the dbt transformations.  
