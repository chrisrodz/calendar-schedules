from datetime import datetime, timedelta, date, time
from flask import Flask, redirect, render_template, request, g, jsonify
from app.services.google_calendar import GoogleCalendarService
from app.database import get_db
from pytz import timezone, utc
from collections import defaultdict

app = Flask(__name__)
gcal = GoogleCalendarService()

TZ = timezone('America/Los_Angeles')
WEEK_START_DAY = 0
WEEK_END_DAY = 4
DAY_START_HOUR = time(hour=8, tzinfo=TZ)
DAY_END_HOUR = time(hour=17, tzinfo=TZ)


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


@app.route('/available_slots')
def available_slots():
    ret = defaultdict(list)

    # Validate input
    start_ms = int(request.args.get('start_ms', 0))
    end_ms = int(request.args.get('end_ms', 0))
    if not start_ms or not end_ms:
        return '', 400

    start_dt = datetime.utcfromtimestamp(start_ms).date()
    end_dt = datetime.utcfromtimestamp(end_ms).date()

    # Get busy slots for all days in time range
    busy_slots = gcal.get_busy_slots_for_range(start_ms, end_ms)

    # We will return available slots per day
    current_dt = start_dt
    while current_dt <= end_dt:
        # Skip days that are not in office hours
        weekday = current_dt.weekday()
        if weekday < WEEK_START_DAY or weekday > WEEK_END_DAY:
            current_dt += timedelta(days=1)
            continue

        # Get start and end time for appointments this day
        start_time = datetime.combine(current_dt, DAY_START_HOUR)
        end_time = datetime.combine(current_dt, DAY_END_HOUR)

        # Go through busy slots per day and find buckets of time within our range
        # where there are no busy slots. This makes the assumption that busy slots
        # are sorted by (start, end)
        busy_slots_for_day = busy_slots.get(current_dt)
        if busy_slots_for_day is not None:
            for busy_slot in busy_slots_for_day:
                # We've update start_time past our office hours. Done for this date
                if start_time > end_time:
                    break
                busy_start, busy_end = busy_slot['start'], busy_slot['end']

                # Busy slot before office hours start
                if busy_end < start_time:
                    continue

                # Busy slot overlaps with current time. Update current start
                elif busy_start <= start_time and busy_end > start_time:
                    start_time = busy_end
                    continue

                # Busy slot start after current time
                # Add open slot to output and update current time
                elif busy_start > start_time:
                    ret[current_dt.isoformat()].append({
                        'start': start_time.isoformat(),
                        'end': busy_start.isoformat(),
                    })
                    start_time = busy_end
                    continue

        # Add last open slot to output if it exists
        if start_time < end_time:
            ret[current_dt.isoformat()].append({
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
            })

        # Process next date
        current_dt += timedelta(days=1)

    return jsonify(ret)
