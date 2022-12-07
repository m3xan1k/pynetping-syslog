import os


HOST = '0.0.0.0'
# fail fast
SERVER_PORT = int(os.environ.get('SERVER_PORT', 514))

PGHOST = os.environ.get('PGHOST', 'localhost')
PGPORT = os.environ.get('PGPORT', 5432)
PGBASE = os.environ.get('PGBASE', 'syslog_events')
# fail fast
PGUSER = os.environ['PGUSER']
PGPASSWORD = os.environ['PGPASSWORD']

CONN_STRING = 'postgresql://{}:{}@{}:{}/{}?sslmode=disable'.format(
    PGUSER,
    PGPASSWORD,
    PGHOST,
    PGPORT,
    PGBASE,
)

API_HOST = os.environ['API_HOST']
API_PORT = int(os.environ.get('API_PORT', 443))
API_URI = os.environ['API_URI']
BASIC_USER = os.environ['BASIC_USER']
BASIC_PASSWORD = os.environ['BASIC_PASSWORD']
