from dataclasses import dataclass
from selection import Selection
from morph import Morph, parseMorph
from re import compile
from bs4 import Tag

@dataclass
class Word(frozen=True):
  transliteration: str
  lang: str
  transcription: str
  selections: list[Selection]
  analyses: dict[int, Morph]

MRP = compile(r'mrp(\d+)')

def make_word(tag: Tag, default_lang: str) -> Word:
  assert tag.name == 'w'
  transliteration = tag.decode_contents()
  lang = tag.attrs.get('lang', default_lang)
  transcription = tag['trans']
  selections = list(map(Selection.parse_string, tag['mrp0sel']))
  analyses = dict[int, Morph]()
  for attr, value in tag.attrs:
    if (match := MRP.fullmatch(attr)) is not None:
      number = int(match.group(1))
      analyses[number] = parseMorph(value)
  return Word(transliteration, lang, transcription, selections, analyses)
