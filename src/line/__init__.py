from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from bs4 import Tag
from logging import getLogger
from os.path import join

@dataclass(frozen=True)
class Line:
  text_path: str
  text_id: str
  line_id: str
  language: str
  word_elements: list[Tag]
  logger = getLogger(__name__)
  UNKNOWN_LINE_ID = 'unknown'
  UNKNOWN_LANGUAGE = 'unknown'

  def __iter__(self) -> Iterable[Tag]:
    return self.word_elements.__iter__()

  def __len__(self) -> int:
    return self.word_elements.__len__()

  @classmethod
  def parse_line(cls, text_path: str, text_id: str, elements: list[Tag]) -> Line:
    full_path = join(text_path, text_id)
    if (lb := elements[0]).name == 'lb':
      if 'lnr' in lb.attrs:
        line_id = lb['lnr']
      else:
        cls.logger.error('A line in %s is not numbered.', full_path)
        line_id = cls.UNKNOWN_LINE_ID
      if 'lg' in lb.attrs:
        language = lb.attrs['lg']
      else:
        cls.logger.error('Line %s in %s is not marked for language.', line_id, full_path)
        language = cls.UNKNOWN_LANGUAGE
      word_elements = elements[1:]
    else:
      cls.logger.error('The first line in %s does not start with a linebreak element.', full_path)
      line_id = cls.UNKNOWN_LINE_ID
      language = cls.UNKNOWN_LANGUAGE
      word_elements = elements
    return Line(text_path, text_id, line_id, language, word_elements)
