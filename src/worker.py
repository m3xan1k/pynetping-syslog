from base64 import b64encode
import json
import http.client as client
import logging
import socket
import typing

import psycopg

from common import settings


def fetch_records() -> typing.Optional[typing.List[tuple]]:
    with psycopg.connect(settings.CONN_STRING) as conn:
        with conn.cursor() as cur:
            return cur.execute(
                """
                SELECT uid, details
                FROM events
                WHERE is_syncronized = false
                """
            ).fetchall()


def syncronize_records(records: typing.List[tuple]) -> None:
    uids = [record[0] for record in records]
    with psycopg.connect(settings.CONN_STRING) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE events
                SET is_syncronized = true
                WHERE uid = ANY(%s)
                """,
                [uids]
            )


def basic_auth(user: str, password: str) -> str:
    login_pair_bytes = '{}:{}'.format(user, password).encode('utf-8')
    token = b64encode(login_pair_bytes).decode('ascii')
    return 'Basic {}'.format(token)


def send(
    data: typing.List[dict]
) -> typing.Optional[client.HTTPResponse]:
    headers = {
        'content-type': 'application/json',
        'authorization': basic_auth(
            settings.BASIC_USER,
            settings.BASIC_PASSWORD,
        )
    }
    payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
    try:
        conn = client.HTTPConnection(
            settings.API_HOST,
            settings.API_PORT,
            timeout=10,
        )
    except socket.timeout as err:
        logging.error(err)
    except client.HTTPException as err:
        logging.error(err)
    else:
        conn.request(
            'POST',
            settings.API_URI,
            body=payload,
            headers=headers
        )
        response = conn.getresponse()
        return response


if __name__ == '__main__':
    if records := fetch_records():
        records_dicts: typing.List[dict] = [
            {'uid': str(record[0]), 'details': record[1]}
            for record in records
        ]
        if response := send(records_dicts):
            if response.status in [200, 201]:
                syncronize_records(records)
