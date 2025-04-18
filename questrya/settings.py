import logging
import logging.config

from decouple import config

from questrya.common.utils import get_app_version

IS_DEV_APP = config('IS_DEV_APP', cast=bool)  # Queues

# Logging configuration
LOG_LEVEL = config('LOG_LEVEL', default='INFO', cast=str)
LOG_VARS = config('LOG_VARS', cast=str).replace("'", '').replace('"', '')
JSON_LOGS = config('JSON_LOGS', default=False, cast=bool)
if JSON_LOGS:
    log_format = ' '.join(
        ['%({0:s})'.format(variable) for variable in LOG_VARS.split()]
    )
else:
    log_format = ''
    for index, variable in enumerate(LOG_VARS.split()):
        if variable != 'asctime':
            log_format += ' '
        log_format += f'%({variable})s'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {'level': LOG_LEVEL, 'handlers': ['console']},
    'formatters': {'default': {'format': log_format, 'datefmt': '%Y%m%d.%H%M%S'}},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
            'formatter': 'default',
        }
    },
    'loggers': {
        # default for all undefined Python modules
        '': {'level': 'WARNING', 'handlers': ['console']},
        'rose': {
            'level': LOG_LEVEL,
            'handlers': ['console'],
            'propagate': False,
        },
        'celery': {
            'level': LOG_LEVEL,
            'handlers': ['console'],
            'propagate': True,
        },
    },
}
if JSON_LOGS:
    LOGGING['formatters']['default']['class'] = (
        'pythonjsonlogger.jsonlogger.JsonFormatter'
    )

logging.config.dictConfig(LOGGING)

VERSION = get_app_version()

SWAGGER_TEMPLATE = {
    'swagger': '2.0',
    'uiversion': 2,
    'info': {
        'title': 'questrya',
        'description': 'A template for flask projects using celery and  sqlalchemy.',
        'contact': {
            'responsibleOrganization': 'TDS',
            'responsibleDeveloper': 'Tiago',
            'email': 'tdvservices@proton.me',
            'url': 'https://writeloop.dev',
        },
        'version': VERSION,
    },
    'schemes': ['http', 'https'],
}

DATABASE_USER = config('DATABASE_USER')
DATABASE_PASSWORD = config('DATABASE_PASSWORD')
DATABASE_HOST = config('DATABASE_HOST')
DATABASE_NAME = config('DATABASE_NAME')
DATABASE_URI = (
    f'postgresql+psycopg2://{DATABASE_USER}'
    f':{DATABASE_PASSWORD}'
    f'@{DATABASE_HOST}'
    f'/{DATABASE_NAME}'
)
SQLALCHEMY_DATABASE_URI = DATABASE_URI

QUEUE_HOST = config('QUEUE_HOST', cast=str)
QUEUE_PORT = config('QUEUE_PORT', cast=int, default=5672)
QUEUE_USER = config('QUEUE_USER', cast=str)
QUEUE_PASSWORD = config('QUEUE_PASSWORD', cast=str)
DEFAULT_QUEUE_NAME = config('DEFAULT_QUEUE_NAME', cast=str)
TASKS_QUEUES = {
    'questrya.tasks.compute': {'queue': 'compute'},
    'questrya.tasks.generate_random_string': {'queue': 'generate_random_string'},
}

JWT_SECRET_KEY = config('JWT_SECRET_KEY', cast=str)
