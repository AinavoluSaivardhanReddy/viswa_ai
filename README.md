# Decription
This is a basic text summarizer system written in python using fastapi. The purpose of the system is to showcase rudimentary feature tracking, enforcing susbcription validation, and throttling the usage when feature limits are exceeded.

# Setup

- This project utilizes pipenv for python virtual environment and dependency tracking. So we first need to install pipenv, you can find the instructions [here](https://pipenv.pypa.io/en/latest/installation.html).

- In order to track features and cache validation for users we use redis. Follow this [link](https://redis.io/docs/latest/operate/oss_and_stack/install/) to setup redis locally and start the service.

- After installing pipenv instatiate the virtual environment using the following command:
    ```
    pipenv shell
    ```
- Install dependencies with the following command:
    ```
    pipenv install
    ```
- To run the application we use the following command:
    ```
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```




