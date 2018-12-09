from flask import Flask, redirect, render_template, request
from app.services.google_calendar import GoogleCalendarService
app = Flask(__name__)

gcal = GoogleCalendarService()


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
    credentials = gcal.exchange_url_for_token(code)
    print(credentials)
    return 'We did it'
