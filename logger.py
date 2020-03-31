import datetime

INFO_TEMPLATE = '{} - INFO => Address: {} | Message: {}'
ERROR_TEMPLATE = '{} - ERROR => Address: {} | Message: {} | Cause: {}'


def info(address, message):
    print(INFO_TEMPLATE.format(datetime.datetime.today().isoformat(), address, message))


def error(address, message, cause):
    print(ERROR_TEMPLATE.format(datetime.datetime.today().isoformat(), address, message, cause))
