# File: your_project/logs.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',  # Logs will be written to this file
        },
    },
    'loggers': {
        'userauth.middleware': {  # Logger for your middleware
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}