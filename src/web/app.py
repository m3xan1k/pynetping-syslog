import logging
import uuid
import os
import typing

from flask import Flask, request
from flask.wrappers import Response
import psycopg
from psycopg.types.json import Json
from psycopg import errors


logger = logging.getLogger(__name__)
app = Flask(__name__)


CONN_STRING = os.environ['CONN_STRING']


def get_or_create_server(
    server_data: dict,
) -> typing.Optional[uuid.UUID]:
    with psycopg.connect(CONN_STRING, autocommit=True) as conn:
        cursor = conn.cursor()
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
        except errors.UniqueViolation as e:
            logger.error(e)
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
            if server_row := cursor.fetchone():
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
    data = request.json
    if not data:
        return Response('Data required', status=400)
    server = get_or_create_server(data['server'])
    print(server)
    return Response('hello', status=201)
