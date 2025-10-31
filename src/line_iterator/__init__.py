from bs4 import BeautifulSoup
from typing import Callable, Iterable
from line import Line
from word import Word, make_word
import traceback

class LineIterator:

  def __init__(self, soup: BeautifulSoup, logging_function: Callable[[str], None]):
    self.soup = soup
    self.logging_function = logging_function

  def __iter__(self) -> Iterable[Line]:
    lang = 'hit'
    publ = self.soup.find('AO:TxtPubl').text
    lnr = '[unknown]'
    words = list[Word]()
    for tag in self.soup(['lb', 'w']):
      match tag.name:
        case 'lb':
          if len(words) > 0:
            yield Line(publ, lnr, words)
            words = list[Word]()
          if 'lnr' in tag.attrs:
            lnr = tag['lnr']
          else:
            raise ValueError('The next line after {0} in {1} is not numbered'.format(lnr, publ))
          if 'lg' in tag.attrs:
            lang = tag['lg']
          else:
            self.logging_function('Line {0} in {1} is not marked for language.\n'.format(lnr, publ))
            lang = 'Hur'
        case 'w':
          if lang == 'Hur':
            if 'lg' in tag.attrs and tag['lg'] != 'Hur':
              continue
            try:
              word = make_word(tag, lang)
              words.append(word)
            except (KeyError, ValueError):
              msg = 'Cannot parse word:\n{0}\non line {1} in {2}\n\n'.format(str(tag), lnr, publ)
              self.logging_function(msg)
              self.logging_function(traceback.format_exc())
              self.logging_function('\n\n')
    if len(words) > 0:
      yield Line(publ, lnr, words)
