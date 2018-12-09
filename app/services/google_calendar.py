from datetime import datetime, date
from typing import Tuple, Dict, Any
import json
from pytz import timezone, utc

from google.oauth2.credentials import Credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from app.database import query_db

# TODO: We'll make this the timezone of the calendar
TZ = timezone('America/Los_Angeles')

class GoogleCalendarService():
    def __init__(self):
        scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/plus.me',
            'https://www.googleapis.com/auth/userinfo.email',
        ]
        self.flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=scopes)

        # TODO: This url should be generated
        self.flow.redirect_uri = 'http://localhost:8080/google_auth'

    def get_authorization_url(self) -> Tuple[str, str]:
        authorization_url, state = self.flow.authorization_url(access_type='offline', include_granted_scopes='true')
        return authorization_url, state

    def exchange_url_for_token(self, code):
        self.flow.fetch_token(code=code)
        credentials = self.flow.credentials
        query = 'insert into google_credentials (token,refresh_token,token_uri,client_id,client_secret,scopes) values (?, ?, ?, ?, ?, ?)'
        values = [
            credentials.token,
            credentials.refresh_token,
            credentials.token_uri,
            credentials.client_id,
            credentials.client_secret,
            json.dumps(credentials.scopes)
        ]
        query_db(query, values)
        return credentials

    def get_user_creds(self, user_id: int):
        query = 'select * from google_credentials where id=?'
        credentials = query_db(query, [user_id], one=True)
        return credentials

    def get_busy_slots_for_range(self, start_ms, end_ms):
        ret = {}
        # Get credentials for query
        db_creds = self.get_user_creds(3)
        credentials = Credentials(
            token=db_creds['token'],
            refresh_token=db_creds['refresh_token'],
            token_uri=db_creds['token_uri'],
            client_id=db_creds['client_id'],
            client_secret=db_creds['client_secret'],
            scopes=json.loads(db_creds['scopes']),
        )

        # Query params
        start = datetime.utcfromtimestamp(start_ms).isoformat() + 'Z'
        end = datetime.utcfromtimestamp(end_ms).isoformat() + 'Z'
        service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

        body = {
            'timeMin': start,
            'timeMax': end,
            'items': [{'id': 'primary'}],
        }
        freebusy = service.freebusy().query(body=body).execute()
        print(freebusy)
        busy_slots = freebusy['calendars']['primary']['busy']

        # parse busy slots into dt objects
        for slot in busy_slots:
            slot_start = utc.localize(datetime.fromisoformat(slot['start'][:-1])).astimezone(TZ)
            slot_end = utc.localize(datetime.fromisoformat(slot['end'][:-1])).astimezone(TZ)
            slot_date = slot_start.date()

            # TODO: Make sure these are sorted
            data = {
                'start': slot_start,
                'end': slot_end,
            }

            if slot_date in ret:
                ret[slot_date].append(data)
            else:
                ret[slot_date] = [data]

        return ret

    def is_time_in_busy_slots(self, start_dt, end_dt) -> bool:
        pass
