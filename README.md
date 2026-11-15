# The dataset can be found on this link:
https://www.kaggle.com/datasets/clkmuhammed/autoscout24-car-listings-dataset


# automotive-market-intelligence
A data project on second hand car prices. The idea is to get familiar with dbt and Airflow. 

1. We will collect the data and save it in the root directory.

2. Next step is going to be the simulated data ingestion. We are going to have a folder where we will be manually moving one of the files whenever we want. Hopefully we will have a script that goes through it and clones the data into postgres. I will be purposefully deleting something from the files in order to check if the ingestion step handles errors well and what it will raise as an issue.

3. Next is going to be the transformation - here we will use dbt to get the data from its raw values to something we might be able to work with down the line. 

4. We will then create the tests for the dbt models and then run them and the tests

5. We will see what we can do with the analytics ready data that comes after the transformations.

6. We will then send a report at the end based on every step of the way.

7. We will use Airflow to orchestrate the whole pipeline once we are done with the smaller steps.



Chat GPT steps: 

Step
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


## First steps to be done - This is what needs to be done for step number one and step number two to be completed.

#### Added coments after the list are explanations after implementation or for better understanding and more granular information.

1. Create a database called automotive_market_intelligence. ##  done manually - more information in postgres_operations.md
2. Create the four schemas: raw, staging, intermediate, marts.  ##  done manually - more information in postgres_operations.md
3. Import the CSV into raw.autoscout_listings.  ##  done through ingesting_csvs.py
4. Check that we have all the records and if there are any missing values. ## To be implemented together with 6 - the idea is to be sure we are copying everything and we are not missing any inputs.
5. Inspect the column types and identify which fields might need cleaning.  ## change that step to be later done through dbt transformations. Decided to go with raw data loading with only TEXT fields.
6. Create a simple test to check if all rows have been successfully copied into the db. Data quality tests will be done once we start the dbt transformations.  ## For current purposes we are only going to implement 1) file hashing and checking if the file has already been copied, 2) a check of how many rows are in a csv and how many rows have been copied in the table, and 3) if the structure of the file even matches the structure of the table
