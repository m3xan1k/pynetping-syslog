from datetime import datetime
import os
import socketserver
import typing

import psycopg
from psycopg.types.json import Json


HOST = '0.0.0.0'
# fail fast
SERVER_PORT = int(os.environ.get('SERVER_PORT', 514))

PGHOST = os.environ.get('PGHOST', 'localhost')
PGPORT = os.environ.get('PGPORT', 5432)
PGBASE = os.environ.get('PGBASE', 'syslog_events')
# fail fast
PGUSER = os.environ['PGUSER']
PGPASSWORD = os.environ['PGPASSWORD']


class ThreadingUDPServer(
    socketserver.ThreadingMixIn,
    socketserver.UDPServer
):
    pass


class SyslogHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        datagram: str = self.request[0].strip().decode('utf-8')
        splitted_datagram = datagram.split(' ')
        details = self.parse_details(splitted_datagram)
        self.write_details(details)

    def parse_details(self, splitted_datagram: typing.List[str]) -> dict:
        """
        input: Nov 29 18:58:34.089 OST10-NP1 NetPing: IO4=0 some message
        output: {
            "sensor": {
                "name": "OST10-NP1"
            },
            "io_port": {
                "name": "IO4"
                "value": "0"
            },
            "verbose_message": "some message",
            "dt": "2022-11-29T18:58:34.089000"
        }
        """
        dt = self.parse_dt(splitted_datagram[:3])
        sensor_name = splitted_datagram[3]
        io_port_name, io_port_value = splitted_datagram[5].split('=')
        verbose_message = ' '.join(splitted_datagram[6:])
        return {
            'sensor': {'name': sensor_name},
            'io_port': {'name': io_port_name, 'value': io_port_value},
            'verbose_message': verbose_message,
            'dt': dt,
        }

    @staticmethod
    def write_details(details: dict) -> None:
        connection_string = 'postgresql://{}:{}@{}:{}/{}?sslmode=disable'.format(  # noqa
            PGUSER,
            PGPASSWORD,
            PGHOST,
            PGPORT,
            PGBASE,
        )
        with psycopg.connect(connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO events(details) VALUES (%s)
                    """,
                    [Json(details)]
                )

    @staticmethod
    def parse_dt(data: typing.List[str]) -> str:
        """
        input: ['Nov', '29', '18:58:34.089']
        output: ISO8601
        """
        dt_format = '%Y %b %d %H:%M:%S.%f'
        year = datetime.now().year
        date_string = '{} {}'.format(year, ' '.join(data))
        return datetime.strptime(date_string, dt_format).isoformat()


if __name__ == '__main__':
    with ThreadingUDPServer((HOST, SERVER_PORT), SyslogHandler) as server:
        server.serve_forever()
