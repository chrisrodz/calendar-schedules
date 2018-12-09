from flask import Flask, redirect, render_template, request, g
from app.services.google_calendar import GoogleCalendarService
from app.database import get_db

app = Flask(__name__)
gcal = GoogleCalendarService()


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/auth')
def auth():
    authorization_url, state = gcal.get_authorization_url()
    return redirect(authorization_url)


@app.route('/google_auth')
def handle_google_auth():
    auth_data = request.args
    code = auth_data['code']
    gcal.exchange_url_for_token(code)
    return 'We did it'
