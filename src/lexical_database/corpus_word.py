from dataclasses import dataclass

@dataclass(frozen=True)
class CorpusWord:
  transliteration: str
  segmentation: str
  gloss: str
