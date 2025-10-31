from dataclasses import dataclass
from selection import Selection
from morph import Morph, parseMorph, SingleMorph, MultiMorph
from re import compile
from bs4 import Tag

def make_analysis(selection: Selection, morph: Morph, debug_str: str) -> str:
    if selection.gramm_form is not None:
      assert isinstance(morph, MultiMorph), debug_str
      morph_tag = morph.morph_tags[selection.gramm_form]
    else:
      assert isinstance(morph, SingleMorph) or morph.is_singletone == 1, debug_str
      if isinstance(morph, SingleMorph):
        morph_tag = morph.morph_tag
      else:
        morph_tag = morph.to_single().morph_tag
    if morph_tag == '':
      return '{0}.{1}'.format(morph.translation, morph.pos)
    else:
      return '{0}-{1}'.format(morph.translation, morph_tag)

@dataclass(frozen=True)
class Word:
  tag: str
  transliteration: str
  lang: str
  transcription: str
  selections: list[Selection]
  analyses: dict[int, Morph]

  def to_dict(self):
    if len(self.selections) > 0:
      idx = 0
      selection = self.selections[0]
      morph = self.analyses[selection.lexeme]
      analysis = None
      while idx < len(self.selections):
        try:
          selection = self.selections[idx]
          analysis = make_analysis(selection, morph, self.tag)
          break
        except AssertionError:
          print(self.tag)
        idx += 1
      if analysis is None:
        raise ValueError('All analyses were inappropriate.')
      return {
        'transliteration': self.transliteration,
        'segmentation': morph.segmentation,
        'analysis': analysis
      }
    else:
      return {
        'transliteration': self.transliteration,
        'segmentation': '',
        'analysis': ''
      }

MRP = compile(r'mrp(\d+)')

def make_word(tag: Tag, default_lang: str) -> Word:
  assert tag.name == 'w'
  transliteration = tag.decode_contents()
  lang = tag.attrs.get('lang', default_lang)
  transcription = tag['trans']
  selections = list(map(Selection.parse_string, tag['mrp0sel'].split()))
  analyses = dict[int, Morph]()
  for attr, value in tag.attrs.items():
    if (match := MRP.fullmatch(attr)) is not None:
      number = int(match.group(1))
      analyses[number] = parseMorph(value)
  return Word(str(tag), transliteration, lang, transcription, selections, analyses)
