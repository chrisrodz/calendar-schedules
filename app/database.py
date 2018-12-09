import sqlite3
from flask import g

DATABASE = 'schedules.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, isolation_level=None)

    def make_dicts(cursor, row):
        return dict((cursor.description[idx][0], value)
                    for idx, value in enumerate(row))

    db.row_factory = make_dicts

    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def save_appointment(start_dt, end_dt, name, phone_number, insurance, gcal_event_id):
    query = 'insert into appointments (start_dt, end_dt, name, phone_number, insurance, gcal_event_id, is_confirmed, is_canceled) values (?, ?, ?, ?, ?, ?, 0, 0)'
    values = [start_dt, end_dt, name, phone_number, insurance, gcal_event_id]
    query_db(query, values)
    return True


def get_appointment_by_gcal_event_id(gcal_event_id):
    query = 'select * from appointments where gcal_event_id = ?'
    values = [gcal_event_id]
    return query_db(query, values, one=True)
