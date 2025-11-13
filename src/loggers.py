from os.path import join
from logging import getLogger, FileHandler, DEBUG, Formatter, LogRecord
from model.corpus import PROCESSED_FILE_LOGGER_NAME, SKIPPED_FILE_LOGGER_NAME
logger_names = [PROCESSED_FILE_LOGGER_NAME, SKIPPED_FILE_LOGGER_NAME, '__main__', 'model.corpus', 'model.text']

for logger_name in logger_names:
  handler = FileHandler(join('logs', f'{logger_name}.log'), 'w', encoding='utf-8')
  handler.setLevel(DEBUG)
  formatter = Formatter('%(message)s')
  handler.setFormatter(formatter)
  logger = getLogger(logger_name)
  logger.setLevel(DEBUG)
  logger.addHandler(handler)
