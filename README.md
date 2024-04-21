# Decription
This is a basic text summarizer system written in python using fastapi. The purpose of the system is to showcase rudimentary feature tracking, enforcing susbcription validation, and throttling the usage when feature limits are exceeded.

# Setup

- This project utilizes pipenv for python virtual environment and dependency tracking. So we first need to install pipenv, you can find the instructions [here](https://pipenv.pypa.io/en/latest/installation.html).

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




