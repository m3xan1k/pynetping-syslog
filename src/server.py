from datetime import datetime
import socketserver
import typing

import psycopg
from psycopg.types.json import Json

import settings


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
        with psycopg.connect(settings.CONN_STRING) as conn:
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
    with ThreadingUDPServer(
        (settings.HOST, settings.SERVER_PORT),
        SyslogHandler,
    ) as server:
        server.serve_forever()
