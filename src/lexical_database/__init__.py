from collections import defaultdict
from line import Line
from word import Word
from morph import MultiMorph
from word import log_selection_issue
from re import compile
from logging import getLogger

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
    if len(line) > 0:
      attestation = '{0},{1}'.format(line.text_id, line.line_id)
      corpus_line = list[dict[str, str]]()
      for word_tag in line:
        try:
          word = Word.make_word(word_tag, line.language)
          if word.lang == 'Hur' and word.transcription is not None:
            for selection in word.selections:
              if selection is not None:
                number = selection.lexeme
                if number in word.analyses:
                  analysis = word.analyses[number]
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
                    corpus_line.append(word.to_dict())
                else:
                  log_selection_issue('Wrong number:', word.tag)
        except (KeyError, ValueError):
          msg = 'Cannot parse word:\n{0}\non line {1} in {2}'.format(
            str(word_tag), line.line_id, line.text_path
          )
          self.logger.exception(msg)
      if (len(corpus_line) > 0):
        self.corpus[attestation] = corpus_line
