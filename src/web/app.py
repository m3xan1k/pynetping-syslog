import uuid

from flask import Flask
from flask.wrappers import Response
import psycopg
from psycopg.types.json import Json
from psycopg import errors

from common import settings


app = Flask(__name__)


def get_or_create_server(
    conn: psycopg.Connection, server_data: dict) -> uuid.UUID:
    with psycopg.connect(settings.CONN_STRING) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO
                    trassir_servers(name, guid)
                    VALUES (%s, %s)
                    """,
                    params=(
                        server_data['name'],
                        server_data['guid'],
                    )
                )
            except errors.UniqueViolation:
                pass
            finally:
                cursor.execute(
                    """
                    SELECT uid
                    FROM trassir_servers
                    WHERE name = %s
                    AND guid = %s
                    """,
                    params=(
                        server_data['name'],
                        server_data['guid'],
                    )
                )
                server_row = cursor.fetchone()
                return server_row[0]


@app.route('/api/barrier_events/', methods=['POST'])
def create_barrier_event():
    """
    Example input
    {
        'server': {
            'name': server_obj.name.decode('utf-8'),
            'guid': event.server,
        },
        'channel': {
            'name': channel_obj.name.decode('utf-8'),
            'guid': event.channel,
        },
        'plate_number': plate_number,
        'event_type': event_type,
        'created_at': dt.isoformat(),
        'screenshot': screenshot,
    }
    """
    return Response('hello', status=201)
