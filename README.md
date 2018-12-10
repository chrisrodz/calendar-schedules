# calendar-schedules

## TODOs

- [ ] Authentication flow is tied to a single user and is not production-ready
- [ ] Should get user's timezone after authentication and use it instead of defaulting to PST
- [ ] Should have error handling around db operations
- [ ] Need to clean up code a bit (function names, some methods could be broken down)
- [ ] Unit tests

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

You should be able to visit http://localhost:8080 and to authenticate. After successfully authenticating you should be able to make API requests.

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


### Example requests

```
Request to see available slots for 12/10/2018 8AM to 12/15/2018 8AM
curl -X GET 'http://localhost:8080/available_slots?start_ms=1544428800&end_ms=1544860800'

Request to create an appointment from 12/13/2018 2PM to 12/13/2018 3PM
curl -d '{"start_ms": 1544738400, "end_ms": 1544742000,"name": "Christian Rodriguez","phone_number": "787-566-3317","insurance": "Triple SSS"}' -H "Content-Type: application/json" -X POST http://localhost:8080/create_appointment

Confirm the appointment we just created
curl -d '{"appointment_id": 1}' -H "Content-Type: application/json" -X PUT http://localhost:8080/confirm_appointment

Cancel the appointment we just created
curl -d '{"appointment_id": 1}' -H "Content-Type: application/json" -X PUT http://localhost:8080/cancel_appointment

Create a second appointment with the same time slot
curl -d '{"start_ms": 1544738400, "end_ms": 1544742000,"name": "Christian Rodriguez","phone_number": "787-566-3317","insurance": "Triple SSS"}' -H "Content-Type: application/json" -X POST http://localhost:8080/create_appointment


Cancel the second appointment
curl -d '{"appointment_id": 2}' -H "Content-Type: application/json" -X PUT http://localhost:8080/cancel_appointment

Confirm the second appointment. This will fail because the appointment has been canceled
curl -d '{"appointment_id": 2}' -H "Content-Type: application/json" -X PUT http://localhost:8080/confirm_appointment
```
