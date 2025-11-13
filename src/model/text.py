from __future__ import annotations
from dataclasses import dataclass
from bs4 import Tag, BeautifulSoup
from collections.abc import Iterable
from .line import Line
from more_itertools import split_before
from io import TextIOBase
from os import path
from logging import getLogger
logger = getLogger(__name__)
extension = '.xml'

def is_ao_manuscripts(tag: Tag) -> bool:
  return tag.prefix == 'AO' and tag.name == 'Manuscripts'

@dataclass
class Text:
  rel_path: str
  text_id: str
  text_tag: Tag
  text_lang: str

  @property
  def lines(self) -> Iterable[Line]:
    tokens = list[Tag]()
    for page_element in self.text_tag.children:
      if isinstance(page_element, Tag):
        tokens.append(page_element)
    if is_ao_manuscripts(tokens[0]):
      tokens = tokens[1:]
    for line_elements in split_before(tokens,
                                      lambda tag: tag.name == 'lb'):
      line = Line.parse(self.rel_path, self.text_id, line_elements, self.text_lang)
      yield line

  @classmethod
  def parse(cls, rel_path: str, text_id: str, stream: TextIOBase) -> Text | None:
    soup = BeautifulSoup(stream, 'xml')
    body_tag = soup.body
    if body_tag is None:
      logger.error('The XML tag "body" could not be found.')
      return None
    text_tag = body_tag.find('text')
    if text_tag is None:
      logger.error('The XML tag "text" could not be found.')
      return None
    if not isinstance(text_tag, Tag):
      logger.error('A string was provided instead of the XML tag "text".')
      return None
    if 'xml:lang' in text_tag.attrs and text_tag['xml:lang'] != 'XXXlang':
      text_lang = text_tag['xml:lang']
      if not isinstance(text_lang, str):
        logger.error('The text language attribute had multiple values.')
        return None
      rel_name = path.join(rel_path, text_id + extension)
      logger.info('The text language is set to %s for %s', text_lang, rel_name)
    else:
      text_lang = 'Hit'
    return cls(rel_path, text_id, text_tag, text_lang)
