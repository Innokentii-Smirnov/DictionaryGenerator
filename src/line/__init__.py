from dataclasses import dataclass
from word import Word
from typing import Iterable

@dataclass(frozen=True)
class Line:
  text_id: str
  line_id: str
  words: list[Word]

  def __iter__(self) -> Iterable[Word]:
    return self.words.__iter__()

  def __len__(self) -> int:
    return self.words.__len__()
