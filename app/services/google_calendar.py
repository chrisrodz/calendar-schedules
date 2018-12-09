from typing import Tuple
import json

import google.oauth2.credentials
import google_auth_oauthlib.flow
from app.database import query_db


class GoogleCalendarService():
    def __init__(self):
        scopes = [
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
