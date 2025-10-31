from dataclasses import dataclass
from selection import Selection
from morph import Morph, parseMorph, SingleMorph, MultiMorph
from re import compile
from bs4 import Tag
from os.path import exists
from os import remove

c = 1
SELECTION_LOG = 'selection.log'
if exists(SELECTION_LOG):
  remove(SELECTION_LOG)
def log_selection_issue(message: str, word_tag: str):
  with open(SELECTION_LOG, 'a', encoding= 'utf-8') as fout:
    global c
    print(str(c) + ') ' + message, file=fout)
    print(word_tag, file=fout)
    print(file=fout)
    c += 1

def make_analysis(selection: Selection, morph: Morph, word_tag: str) -> str:
    if selection.gramm_form is not None:
      if isinstance(morph, SingleMorph):
        log_selection_issue('Expected multi:', word_tag)
        morph_tag = morph.morph_tag
      else:
        if selection.gramm_form not in morph.morph_tags:
          log_selection_issue('Missing key:', word_tag)
          morph_tag = ''
        else:
          morph_tag = morph.morph_tags[selection.gramm_form]
    else:
      if isinstance(morph, MultiMorph):
        log_selection_issue('Expected single:', word_tag)
        if morph.is_singletone:
          morph_tag = morph.to_single().morph_tag
        else:
          morph_tag = ''
      else:
        morph_tag = morph.morph_tag
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
  analyses: dict[int, Morph]

  def to_dict(self):
    if len(self.selections) > 0:
      selection = self.selections[0]
      if selection.lexeme in self.analyses:
        morph = self.analyses[selection.lexeme]
        analysis = make_analysis(selection, morph, self.tag)
        return {
          'transliteration': self.transliteration,
          'segmentation': morph.segmentation,
          'gloss': analysis
        }
      else:
        log_selection_issue('Wrong number:', self.tag)
        analysis = ''
    return {
      'transliteration': self.transliteration,
      'segmentation': '',
      'gloss': ''
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
