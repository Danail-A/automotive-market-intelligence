# automotive-market-intelligence
A data project on second hand car prices. The idea is to get familiar with dbt and Airflow. 

1. We will collect the data and save it in the root directory.

2. Next step is going to be the simulated data ingestion. We are going to have a folder where we will be personally moving one of the files whenever we want. Hopefully we will have a script that goes through it and clones the data into postgres. I will be purposefully deleting something from the files in order to check if the ingestion step handles errors well and what it will raise as an issue.

3. Next is going to be the transformation - here we will use dbt to get the data from its raw values to something we might be able to work with down the line. 

4. We will then create the tests for the dbt models and then run them and the tests

5. We will see what we can do with the analytics ready data that comes after the transformations.

6. We will then send a report at the end based on every step of the way.

7. We will use Airflow to orchestrate the whole pipeline once we are done with the smaller steps.
