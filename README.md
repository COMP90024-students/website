## Dash Web App Template

This dash app is built as a template for the final version web.

All the data used here came from AURIN and used for **demonstration purpose only**.

The relevant data will be updated later when the harvester script has collected enough data from Twitter.

You can see live version of this app on nectar at http://115.146.92.235 *(as long as the instance hasn't been removed)*

To run this app locally, first clone repository and then open a terminal to the flask folder.

Create and activate a new virtual environment (recommended) by running
the following:
*
On Windows

```
virtualenv venv 
\venv\scripts\activate
```

Or if using linux

```bash
python3 -m venv myvenv
source myvenv/bin/activate
```

Install the requirements:

```
pip install -r requirements.txt
```
Run the app:

```
export FLASK_APP=run.py
export FLASK_ENV=development
flask run
```
You can run the app on your browser at http://127.0.0.1:5000

To run the container locally:

```sh
docker-compose up --build
```

Go to - http://127.0.0.1/

## Screenshot

![screen.png](screen.png)


## Resources

To learn more about Dash, please visit [documentation](https://plot.ly/dash).
