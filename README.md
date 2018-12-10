# calendar-schedules

## Installation

This assumes that you have setup a valid Google App with a redirect_uri set to `http://localhost:8080/google_auth` and have a corresponding `client_secret.json` file in the top-level directory of this repo. Assuming you have virtualenv installed and have cloned the repository run the following to bootstrap the db:

```
pip install -r requirements.txt
python -c 'from app.app import init_db; init_db()'
```

Now run the following to run the application:

```
flask run
```

You should be able to visit http://localhost:8080 and to authenticate

## API Requests

This app supports the following API requests

`GET /available_slots` - Displays available appointment slots for given time range

Params:
- start_ms: **int** - Start time for available slots check
- end_ms: **int** - End time for available slots check

Returns:
An object of the form:
```
{
    'date': [
        {
            "start": "date_str",
            "end": "date_str",
        },{
            "start": "date_str",
            "end": "date_str",
        },
        ...
    ]
    'date': [...]
}
```
Where `date` is each calendar day with available office hours in between `start_ms` and `end_ms`. The nested objects contain intervals of time that are available for appointments for that calendar day.

Example:
```
{
  "2018-12-10": [
    {
      "end": "2018-12-10T17:00:00-08:00",
      "start": "2018-12-10T11:15:00-08:00"
    }
  ],
  "2018-12-11": [
    {
      "end": "2018-12-11T09:00:00-08:00",
      "start": "2018-12-11T08:00:00-08:00"
    },
    {
      "end": "2018-12-11T12:00:00-08:00",
      "start": "2018-12-11T10:00:00-08:00"
    },
    {
      "end": "2018-12-11T16:30:00-08:00",
      "start": "2018-12-11T13:00:00-08:00"
    }
  ],
  "2018-12-12": [
    {
      "end": "2018-12-12T10:30:00-08:00",
      "start": "2018-12-12T08:30:00-08:00"
    },
    {
      "end": "2018-12-12T17:00:00-08:00",
      "start": "2018-12-12T11:30:00-08:00"
    }
  ],
  "2018-12-13": [
    {
      "end": "2018-12-13T12:00:00-08:00",
      "start": "2018-12-13T08:00:00-08:00"
    },
    {
      "end": "2018-12-13T17:00:00-08:00",
      "start": "2018-12-13T13:00:00-08:00"
    }
  ],
  ]
}
```


`POST /create_appointment` - Create a new appointment for a given time. This also creates an appointment in the connected calendar

Params:
- start_ms: **int** - Start time of the appointment in epoch seconds
- end_ms: **int** - End time of the appointment in epoch seconds
- name: **str** - Patient's name
- phone_number: **str** - Patient's phone number
- insurance: **str** - Patient's insurance

Returns:
```
{
    'id': integer. The appointment id
}
```

`PUT /confirm_appointment` - Confirm an appointment. This updates the google calendar event to show that the appointment is confirmed

Params:
- appointment_id: **int** - The id of the appointment to confirm

Returns an empty 201 response on success


`PUT /cancel_appointment` - Delete an appointment. This deletes the associated google calendar event

Params:
- appointment_id: **int** - The id of the appointment to cancel

Returns an empty 201 response on success

