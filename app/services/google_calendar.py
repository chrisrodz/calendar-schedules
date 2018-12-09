from typing import Tuple

import google.oauth2.credentials
import google_auth_oauthlib.flow


class GoogleCalendarService():
    def __init__(self):
        self.flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=['https://www.googleapis.com/auth/calendar.events'])

        # TODO: This url should be generated
        self.flow.redirect_uri = 'http://localhost:8080/google_auth'

    def get_authorization_url(self) -> Tuple[str, str]:
        authorization_url, state = self.flow.authorization_url(access_type='offline', include_granted_scopes='true')
        return authorization_url, state

    def exchange_url_for_token(self, code):
        self.flow.fetch_token(code=code)
        credentials = self.flow.credentials
        return credentials
