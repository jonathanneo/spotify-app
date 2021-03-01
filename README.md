# SpotiML

A pet project, playing around with spotify API features and ML.


# Running locally
1. Open terminal and `cd` into root of directory 
2. Run `flask run` or `python app.py` to run the app 

# Deploying 

1. Freeze pip / conda requirements 
    ```
    python -m pip list --format=freeze > requirements.txt
    ```

2. Update Procfile to use gunicorn to run the web server and set app.py as the application to run: `web: gunicorn app:app`

3. 