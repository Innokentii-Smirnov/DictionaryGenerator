from collections import defaultdict
from line import Line

fragmentary_form_indicators = {'[', ']', '(-)', 'x'}

def is_fragmentary(form: str) -> bool:
  return any(indicator in form for indicator in fragmentary_form_indicators)

def get_stem(word: str):
  return word.split('-')[0]

def sort_values(dic: defaultdict[str, set[str]]) -> dict[str, list[str]]:
  return {key: sorted(values) for key, values in dic.items()}

class LexicalDatabase:

  def __init__(self):
    self.dictionary = defaultdict[str, set[str]](set)
    self.glosses = defaultdict[str, set[str]](set)
    self.concordance = defaultdict[str, set[str]](set)
    self.corpus = dict[str, dict[str, str]]()

  def to_dict(self):
    return {
      'dictionary': sort_values(self.dictionary),
      'glosses': sort_values(self.glosses),
      'concordance': sort_values(self.concordance),
      'corpus': self.corpus
    }

  def add(self, line: Line):
    for word in line:
      if not is_fragmentary(word.transcription):
        for selection in word.selections:
          number = selection.lexeme
          analysis = word.analyses[number]
          if not is_fragmentary(analysis.segmentation):
            analysis_str = str(analysis)
            self.dictionary[word.transcription].add(analysis_str)
            stem = get_stem(analysis.segmentation)
            glosses_key = '{0},{1}'.format(stem, analysis.pos)
            self.glosses[glosses_key].add(analysis.translation)
            attestation = '{0},{1}'.format(line.text_id, line.line_id)
            self.concordance[analysis_str].add(attestation)
    corpus_line = [word.to_dict() for word in line.words]
    self.corpus[attestation] = corpus_line
