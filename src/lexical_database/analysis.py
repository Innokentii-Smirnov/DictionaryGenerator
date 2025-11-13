from model.selection import Selection
from model.morph import Morph

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
