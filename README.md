# SpotiML

A pet project, playing around with spotify API features and ML.


# Running locally
1. Open terminal and `cd` into root of directory 
2. Run `flask run` or `python app.py` to run the app 
3. Set config vars
    Windows: 
    ```
    SET SPOTIPY_CLIENT_ID=xxxxxxxxxx
    SET SPOTIPY_CLIENT_SECRET=xxxxxxxxxx
    SET SPOTIPY_REDIRECT_URI=http://127.0.0.1:5000
    ```

    Linux/Mac:
    ```
    export SPOTIPY_CLIENT_ID=xxxxxxxxxx
    export SPOTIPY_CLIENT_SECRET=xxxxxxxxxx
    export SPOTIPY_REDIRECT_URI=http://127.0.0.1:5000
    ```

# Deploying 

1. Freeze pip / conda requirements 
    ```
    python -m pip list --format=freeze > requirements.txt
    ```

2. Update `Procfile` to use gunicorn to run the web server and set app.py as the application to run: 
    ```
    web: gunicorn app:app
    ```

3. Set config vars in Heroku `Settings` > `Config vars`

    ![img](docs/img/heroku_config_vars.png)


4. Connect app via GitHub and then press `Deploy`

    ![img](docs/img/connect_app_github.png)