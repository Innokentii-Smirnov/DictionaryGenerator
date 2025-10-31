from collections import defaultdict
from line import Line

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
      for selection in word.selections:
        number = selection.lexeme
        analysis = word.analyses[number]
        self.dictionary[word.transcription].add(str(analysis))
