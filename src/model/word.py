from __future__ import annotations
from dataclasses import dataclass
from .selection import Selection
from morph import Morph, parseMorph, SingleMorph, MultiMorph
from re import compile
from bs4 import Tag
from os.path import exists
from os import remove
from logging import getLogger

@dataclass(frozen=True)
class Word:
  transliteration: str
  lang: str
  transcription: str | None
  selections: list[Selection | None]
  analyses: dict[int, str]
  logger = getLogger(__name__)
  MRP = compile(r'mrp(\d+)')

  @classmethod
  def make_word(cls, tag: Tag, default_lang: str) -> Word:
    assert tag.name == 'w'
    transliteration = tag.decode_contents()
    lang = tag.attrs.get('lg', default_lang)
    if 'trans' in tag.attrs:
      transcription = tag['trans']
      assert isinstance(transcription, str)
    else:
      cls.logger.warning('A word has no transcription attribute: %s.', tag)
      transcription = None
    if 'mrp0sel' in tag.attrs:
      mrp0sel = tag['mrp0sel']
      assert isinstance(mrp0sel, str)
      selections = list(map(Selection.parse_string, mrp0sel.split()))
    else:
      cls.logger.warning('A word has no selection attribute: %s.', tag)
      selections = []
    analyses = dict[int, str]()
    for attr, value in tag.attrs.items():
      if (match := cls.MRP.fullmatch(attr)) is not None:
        number = int(match.group(1))
        analyses[number] = value
    return Word(transliteration, lang, transcription, selections, analyses)

  def __getitem__(self, number: int) -> Morph:
    return parseMorph(self.analyses[number])
