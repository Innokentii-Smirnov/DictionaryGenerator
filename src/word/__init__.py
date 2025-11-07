from __future__ import annotations
from dataclasses import dataclass
from selection import Selection
from morph import Morph, parseMorph, SingleMorph, MultiMorph
from re import compile
from bs4 import Tag
from os.path import exists
from os import remove
from logging import getLogger
from lexical_database.corpus_word import CorpusWord

ERROR_SYMBOL = 'ERROR'

def make_analysis(selection: Selection, morph: Morph, word_tag: str) -> str:
    if selection.gramm_form is None:
        morph_tag = morph.single_morph_tag
    else:
        morph_tag = morph[selection.gramm_form]
    if morph_tag is None:
      morph_tag = ERROR_SYMBOL
    if morph_tag == '':
      return '{0}.{1}'.format(morph.translation, morph.pos)
    elif morph_tag.startswith('.') or morph_tag.startswith('='):
      return '{0}{1}'.format(morph.translation, morph_tag)
    else:
      return '{0}-{1}'.format(morph.translation, morph_tag)

@dataclass(frozen=True)
class Word:
  tag: str
  transliteration: str
  lang: str
  transcription: str
  selections: list[Selection]
  analyses: dict[int, str]
  logger = getLogger(__name__)
  MRP = compile(r'mrp(\d+)')

  def to_corpus_word(self) -> CorpusWord:
    if len(self.selections) > 0:
      selection = self.selections[0]
      if selection is not None and selection.lexeme in self.analyses:
        morph = self[selection.lexeme]
        analysis = make_analysis(selection, morph, self.tag)
        return CorpusWord(self.transliteration, morph.segmentation, analysis)
      else:
        self.logger.error('Wrong number: %s', self.tag)
        analysis = ''
    return CorpusWord(self.transliteration, '', '')

  @classmethod
  def make_word(cls, tag: Tag, default_lang: str) -> Word:
    assert tag.name == 'w'
    transliteration = tag.decode_contents()
    lang = tag.attrs.get('lg', default_lang)
    if 'trans' in tag.attrs:
      transcription = tag['trans']
    else:
      cls.logger.error('A word has no transcription attribute: %s.', tag)
      transcription = None
    if 'mrp0sel' in tag.attrs:
      selections = list(map(Selection.parse_string, tag['mrp0sel'].split()))
    else:
      cls.logger.error('A word has no selection attribute: %s.', tag)
      selections = []
    analyses = dict[int, Morph]()
    for attr, value in tag.attrs.items():
      if (match := cls.MRP.fullmatch(attr)) is not None:
        number = int(match.group(1))
        analyses[number] = value
    return Word(str(tag), transliteration, lang, transcription, selections, analyses)

  def __getitem__(self, number: int) -> Morph:
    return parseMorph(self.analyses[number])
