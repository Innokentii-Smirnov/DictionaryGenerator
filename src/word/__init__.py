from __future__ import annotations
from dataclasses import dataclass
from selection import Selection
from morph import Morph, parseMorph, SingleMorph, MultiMorph
from re import compile
from bs4 import Tag
from os.path import exists
from os import remove
from logging import getLogger
from .corpus_word import make_corpus_word

ERROR_SYMBOL = 'ERROR'

def join(sep: str, translation: str, grammatical_info: str) -> str:
  return sep.join(filter(lambda x: x != '', (translation, grammatical_info)))

def make_analysis(selection: Selection, morph: Morph) -> str:
    if selection.gramm_form is None:
        morph_tag = morph.single_morph_tag
    else:
        morph_tag = morph[selection.gramm_form]
    if morph_tag is None:
      morph_tag = ERROR_SYMBOL
    if morph_tag == '':
      return morph.translation
    elif morph_tag.startswith('.') or morph_tag.startswith('='):
      return '{0}{1}'.format(morph.translation, morph_tag)
    else:
      return join('-', morph.translation, morph_tag)

def enclose_with_xml_tag(string: str, tag: str) -> str:
  return '<{0}>{1}</{0}>'.format(tag, string)

@dataclass(frozen=True)
class Word:
  transliteration: str
  lang: str
  transcription: str | None
  selections: list[Selection | None]
  analyses: dict[int, str]
  logger = getLogger(__name__)
  MRP = compile(r'mrp(\d+)')

  def to_corpus_word(self) -> dict[str, str]:
    transliteration = enclose_with_xml_tag(self.transliteration, 'w')
    if len(self.selections) > 0:
      selection = self.selections[0]
      if selection is not None:
        if selection.lexeme in self.analyses:
          morph = self[selection.lexeme]
          analysis = make_analysis(selection, morph)
          return make_corpus_word(transliteration, morph.segmentation, analysis)
        else:
          self.logger.error('The selected morphological analysis number %i is not available.',
                            selection.lexeme)
          analysis = ''
      else:
          self.logger.error('No morphological analysis is selected.')
          analysis = ''
    return make_corpus_word(transliteration)

  @classmethod
  def make_word(cls, tag: Tag, default_lang: str) -> Word:
    assert tag.name == 'w'
    transliteration = tag.decode_contents()
    lang = tag.attrs.get('lg', default_lang)
    if 'trans' in tag.attrs:
      transcription = tag['trans']
      assert isinstance(transcription, str)
    else:
      cls.logger.error('A word has no transcription attribute: %s.', tag)
      transcription = None
    if 'mrp0sel' in tag.attrs:
      mrp0sel = tag['mrp0sel']
      assert isinstance(mrp0sel, str)
      selections = list(map(Selection.parse_string, mrp0sel.split()))
    else:
      cls.logger.error('A word has no selection attribute: %s.', tag)
      selections = []
    analyses = dict[int, str]()
    for attr, value in tag.attrs.items():
      if (match := cls.MRP.fullmatch(attr)) is not None:
        number = int(match.group(1))
        analyses[number] = value
    return Word(transliteration, lang, transcription, selections, analyses)

  def __getitem__(self, number: int) -> Morph:
    return parseMorph(self.analyses[number])
