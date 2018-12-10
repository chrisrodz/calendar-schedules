import sqlite3
from flask import g
from typing import Dict, Any

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


def save_appointment(start_ms, end_ms, name, phone_number, insurance, gcal_event_id):
    query = 'insert into appointments (start_ms, end_ms, name, phone_number, insurance, gcal_event_id, is_confirmed, is_canceled) values (?, ?, ?, ?, ?, ?, 0, 0)'
    values = [start_ms, end_ms, name, phone_number, insurance, gcal_event_id]
    query_db(query, values)
    return True


def get_appointment_by_gcal_event_id(gcal_event_id: str) -> Dict[str, Any]:
    query = 'select * from appointments where gcal_event_id = ?'
    values = [gcal_event_id]
    return query_db(query, values, one=True)


def get_appointment_by_id(appointment_id: int) -> Dict[str, Any]:
    query = 'select * from appointments where id = ?'
    values = [appointment_id]
    return query_db(query, values, one=True)


def confirm_appointment(appointment_id: int) -> bool:
    query = 'update appointments set is_confirmed = 1 where id = ?'
    values = [appointment_id]
    query_db(query, values)
    return True


def cancel_appointment(appointment_id: int) -> bool:
    query = 'update appointments set is_canceled = 1 where id = ?'
    values = [appointment_id]
    query_db(query, values)
    return True
