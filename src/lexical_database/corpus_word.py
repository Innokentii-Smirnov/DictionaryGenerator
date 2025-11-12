from model.word import Word
from .analysis import make_analysis
from logging import getLogger
logger = getLogger(__name__)

def make_corpus_word(transliteration: str,
                     segmentation: str = '',
                     gloss: str = '') -> dict[str, str]:
  return {
    "transliteration": transliteration,
    "segmentation": segmentation,
    "gloss": gloss
  }

def enclose_with_xml_tag(string: str, tag: str) -> str:
  return '<{0}>{1}</{0}>'.format(tag, string)

def word_to_corpus_word(word: Word) -> dict[str, str]:
  transliteration = enclose_with_xml_tag(word.transliteration, 'w')
  if len(word.selections) > 0:
    selection = word.selections[0]
    if selection is not None:
      if selection.lexeme in word.analyses:
        morph = word[selection.lexeme]
        analysis = make_analysis(selection, morph)
        return make_corpus_word(transliteration, morph.segmentation, analysis)
      else:
        logger.error('The selected morphological analysis number %i is not available.',
                     selection.lexeme)
        analysis = ''
    else:
        logger.warning('No morphological analysis is selected.')
        analysis = ''
  return make_corpus_word(transliteration)
