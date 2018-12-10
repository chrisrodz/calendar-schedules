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

    def exchange_url_for_token(self, code: str) -> bool:
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
        return True

    def get_user_creds(self):
        query = 'select * from google_credentials where id=1'
        db_creds = query_db(query, one=True)
        credentials = Credentials(
            token=db_creds['token'],
            refresh_token=db_creds['refresh_token'],
            token_uri=db_creds['token_uri'],
            client_id=db_creds['client_id'],
            client_secret=db_creds['client_secret'],
            scopes=json.loads(db_creds['scopes']),
        )
        return credentials

    def create_calendar_event(self, start_ms: int, end_ms: int, title: str, description: str) -> str:
        start_dt = utc.localize(datetime.utcfromtimestamp(start_ms)).astimezone(TZ)
        end_dt = utc.localize(datetime.utcfromtimestamp(end_ms)).astimezone(TZ)
        service = googleapiclient.discovery.build('calendar', 'v3', credentials=self.get_user_creds())
        body = {
            'start': {
                'dateTime': start_dt.isoformat(),
            },
            'end': {
                'dateTime': end_dt.isoformat(),
            },
            'summary': title,
            'description': description
        }
        ret = service.events().insert(calendarId='primary', body=body).execute()
        return ret['id']

    def confirm_calendar_event(self, event_id: str, title: str) -> bool:
        body = {'summary': title}
        service = googleapiclient.discovery.build('calendar', 'v3', credentials=self.get_user_creds())
        service.events().patch(calendarId='primary', eventId=event_id, body=body).execute()
        return True

    def remove_calendar_event(self, event_id: str) -> bool:
        service = googleapiclient.discovery.build('calendar', 'v3', credentials=self.get_user_creds())
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return True

    def get_busy_slots_for_range(self, start_ms: int, end_ms: int) -> Dict[date, Any]:
        ret = {}

        # Query params
        start = datetime.utcfromtimestamp(start_ms).isoformat() + 'Z'
        end = datetime.utcfromtimestamp(end_ms).isoformat() + 'Z'
        service = googleapiclient.discovery.build('calendar', 'v3', credentials=self.get_user_creds())

        body = {
            'timeMin': start,
            'timeMax': end,
            'items': [{'id': 'primary'}],
        }
        freebusy = service.freebusy().query(body=body).execute()
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

    def is_time_in_busy_slots(self, start_ms: int, end_ms: int) -> bool:
        busy_slots = self.get_busy_slots_for_range(start_ms, end_ms)

        start_dt = utc.localize(datetime.utcfromtimestamp(start_ms)).astimezone(TZ)
        end_dt = utc.localize(datetime.utcfromtimestamp(end_ms)).astimezone(TZ)

        for _, slots in busy_slots.items():
            for slot in slots:
                if dates_overlap(slot['start'], slot['end'], start_dt, end_dt):
                    return True

        return False


def dates_overlap(start_dt1, end_dt1, start_dt2, end_dt2):
    if start_dt2 <= start_dt1 <= end_dt2:
        return True
    elif start_dt2 <= end_dt1 <= end_dt2:
        return True

    return False
