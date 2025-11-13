from collections import defaultdict
from model.line import Line
from model.word import Word
from .corpus_word import make_corpus_word, word_to_corpus_word
from morph import Morph, MultiMorph
from re import compile
from os import makedirs
from os.path import join
from logging import getLogger, FileHandler, DEBUG, Formatter, LogRecord
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
for package in ['model.line', 'model.word', 'model.selection', 'morph',
                'lexical_database', 'lexical_database.corpus_word']:
  handler = FileHandler(join('logs', f'{package}.log'), 'w', encoding='utf-8')
  handler.setLevel(DEBUG)
  formatter = Formatter('%(text_path)s\n%(text_id)s\n%(line_id)s\n%(word_tag)s\n%(levelname)s: %(message)s\n')
  handler.setFormatter(formatter)
  handler.addFilter(log_filter)
  logger = getLogger(package)
  logger.setLevel(DEBUG)
  logger.addHandler(handler)

fragmentary_form_indicators = {'[', ']', 'x'}

def is_fragmentary(form: str) -> bool:
  return (any(indicator in form for indicator in fragmentary_form_indicators)
          or form.strip() == '')

stem_split_pattern = compile('[-=]')
def get_stem(word: str) -> str:
  return stem_split_pattern.split(word)[0]

def sort_values(dic: defaultdict[str, set[str]]) -> dict[str, list[str]]:
  return {key: sorted(values) for key, values in dic.items()}

TRANSLATION_WORD_SEPARATOR = '; '

""" Split a semicolon-delimited translation into separate words

:return: a list of words the translation consists of
"""
def split_translation_into_words(translation: str) -> list[str]:
  return translation.split(TRANSLATION_WORD_SEPARATOR)

class LexicalDatabase:

  def __init__(self) -> None:
    self.dictionary = defaultdict[str, set[str]](set)
    self.glosses = defaultdict[str, set[str]](set)
    self.concordance = defaultdict[str, set[str]](set)
    self.corpus = dict[str, list[dict[str, str]]]()
    self.logger = getLogger(__name__)

  """Add the words occuring in a translation to the
  list possible tranlsations for a particular stem

  :param analysis: An HPM morphological analysis object
  """
  def update_glosses(self, analysis: Morph) -> None:
    stem = get_stem(analysis.segmentation)
    glosses_key = '{0},{1}'.format(stem, analysis.pos)
    values = self.glosses[glosses_key]
    for translation_word in split_translation_into_words(analysis.translation):
      values.add(translation_word)

  def to_dict(self) -> dict[str, dict[str, list[str]] | dict[str, list[dict[str, str]]]]:
    return {
      'dictionary': sort_values(self.dictionary),
      'glosses': sort_values(self.glosses),
      'concordance': sort_values(self.concordance),
      'corpus': self.corpus
    }

  def add(self, line: Line) -> None:
    ctx_text_path.set(line.text_path)
    ctx_line_id.set(line.line_id.strip())
    ctx_text_id.set(line.text_id)
    if len(line) > 0:
      attestation = '{0},{1}'.format(line.text_id, line.line_id)
      corpus_line = list[dict[str, str]]()
      for tag in line:
        ctx_word_tag.set(str(tag))
        if tag.name == 'w':
          try:
            word = Word.parse(tag, line.language)
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
                      self.update_glosses(analysis)
                      self.concordance[analysis_str].add(attestation)
                  else:
                    self.logger.error('The selected morphological analysis number %i is not available.', number)
            corpus_line.append(word_to_corpus_word(word))
          except (KeyError, ValueError):
            msg = 'Cannot parse word:\n{0}\non line {1} in {2}'.format(
              str(tag), line.line_id, line.text_path
            )
            self.logger.exception(msg)
        else:
          corpus_line.append(make_corpus_word(str(tag)))
      if (len(corpus_line) > 0):
        self.corpus[attestation] = corpus_line
