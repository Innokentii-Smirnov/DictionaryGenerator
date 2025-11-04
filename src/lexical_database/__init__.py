from collections import defaultdict
from line import Line
from word import Word
from morph import MultiMorph
from word import log_selection_issue
from re import compile
from os import makedirs
from os.path import join
from logging import getLogger, FileHandler, DEBUG, Formatter, LogRecord
from contextvars import ContextVar

ctx_text_path = ContextVar('text_path')
ctx_text_path.set('Unknown directory')

ctx_text_id = ContextVar('text_id')
ctx_text_id.set('Unknown directory')

ctx_line_id = ContextVar('line_id')
ctx_line_id.set('Unknown line')

ctx_word_tag = ContextVar('word_tag')
ctx_word_tag.set('Unknown word')

def log_filter(record: LogRecord) -> LogRecord:
  record.text_path = ctx_text_path.get()
  record.text_id = ctx_text_id.get()
  record.line_id = ctx_line_id.get()
  record.word_tag = ctx_word_tag.get()
  return record

makedirs('logs', exist_ok=True)
for package in ['line', 'word', 'selection', 'morph', 'lexical_database']:
  handler = FileHandler(join('logs', f'{package}.log'), 'w', encoding='utf-8')
  handler.setLevel(DEBUG)
  formatter = Formatter('%(text_path)s\n%(text_id)s\n%(line_id)s\n%(word_tag)s\n%(message)s\n')
  handler.setFormatter(formatter)
  handler.addFilter(log_filter)
  logger = getLogger(package)
  logger.setLevel(DEBUG)
  logger.addHandler(handler)

fragmentary_form_indicators = {'[', ']', '(-)', 'x'}

def is_fragmentary(form: str) -> bool:
  return (any(indicator in form for indicator in fragmentary_form_indicators)
          or form.strip() == '')

stem_split_pattern = compile('[-=]')
def get_stem(word: str):
  return stem_split_pattern.split(word)[0]

def sort_values(dic: defaultdict[str, set[str]]) -> dict[str, list[str]]:
  return {key: sorted(values) for key, values in dic.items()}

class LexicalDatabase:

  def __init__(self):
    self.dictionary = defaultdict[str, set[str]](set)
    self.glosses = defaultdict[str, set[str]](set)
    self.concordance = defaultdict[str, set[str]](set)
    self.corpus = dict[str, dict[str, str]]()
    self.logger = getLogger(__name__)

  def to_dict(self):
    return {
      'dictionary': sort_values(self.dictionary),
      'glosses': sort_values(self.glosses),
      'concordance': sort_values(self.concordance),
      'corpus': self.corpus
    }

  def add(self, line: Line):
    ctx_text_path.set(line.text_path)
    ctx_line_id.set(line.line_id.strip())
    ctx_text_id.set(line.text_id)
    if len(line) > 0:
      attestation = '{0},{1}'.format(line.text_id, line.line_id)
      corpus_line = list[dict[str, str]]()
      for word_tag in line:
        ctx_word_tag.set(word_tag)
        try:
          word = Word.make_word(word_tag, line.language)
          if word.lang == 'Hur' and word.transcription is not None:
            for selection in word.selections:
              if selection is not None:
                number = selection.lexeme
                if number in word.analyses:
                  analysis = word[number]
                  if not is_fragmentary(analysis.segmentation):
                    if isinstance(analysis, MultiMorph) and analysis.is_singletone:
                      analysis_str = str(analysis.to_single())
                    else:
                      analysis_str = str(analysis)
                    self.dictionary[word.transcription].add(analysis_str)
                    stem = get_stem(analysis.segmentation)
                    glosses_key = '{0},{1}'.format(stem, analysis.pos)
                    self.glosses[glosses_key].add(analysis.translation)
                    self.concordance[analysis_str].add(attestation)
                else:
                  log_selection_issue('Wrong number:', word.tag)
            corpus_line.append(word.to_dict())
        except (KeyError, ValueError):
          msg = 'Cannot parse word:\n{0}\non line {1} in {2}'.format(
            str(word_tag), line.line_id, line.text_path
          )
          self.logger.exception(msg)
      if (len(corpus_line) > 0):
        self.corpus[attestation] = corpus_line
