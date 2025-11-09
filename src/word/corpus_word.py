def make_corpus_word(transliteration: str, segmentation: str = '', gloss: str = ''):
  return {
    "transliteration": transliteration,
    "segmentation": segmentation,
    "gloss": gloss
  }
