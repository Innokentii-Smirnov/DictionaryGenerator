from os import makedirs
from os.path import join
from logging import getLogger, FileHandler, DEBUG, ERROR, Formatter, LogRecord
from contextvars import ContextVar

ctx_text_path: ContextVar[str] = ContextVar('text_path')
ctx_text_path.set('Unknown directory')

ctx_text_id: ContextVar[str] = ContextVar('text_id')
ctx_text_id.set('Unknown directory')

ctx_line_id: ContextVar[str] = ContextVar('line_id')
ctx_line_id.set('Unknown line')

ctx_word_tag: ContextVar[str] = ContextVar('word_tag')
ctx_word_tag.set('Unknown word')

def log_filter(record: LogRecord) -> LogRecord:
  record.text_path = ctx_text_path.get()
  record.text_id = ctx_text_id.get()
  record.line_id = ctx_line_id.get()
  record.word_tag = ctx_word_tag.get()
  return record

makedirs('logs', exist_ok=True)
for package in ['model.line', 'model.word', 'model.selection', 'model.morph',
                'lexical_database', 'lexical_database.corpus_word']:
  handler = FileHandler(join('logs', f'{package}.log'), 'w', encoding='utf-8')
  handler.setLevel(DEBUG)
  error_handler = FileHandler(join('logs', f'{package}.error.log'), 'w', encoding='utf-8')
  error_handler.setLevel(ERROR)
  formatter = Formatter('%(text_path)s\n%(text_id)s\n%(line_id)s\n%(word_tag)s\n%(levelname)s: %(message)s\n')
  handler.setFormatter(formatter)
  handler.addFilter(log_filter)
  error_handler.setFormatter(formatter)
  error_handler.addFilter(log_filter)
  logger = getLogger(package)
  logger.setLevel(DEBUG)
  logger.addHandler(handler)
  logger.addHandler(error_handler)
