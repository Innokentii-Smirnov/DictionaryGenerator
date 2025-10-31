from bs4 import BeautifulSoup
from typing import Callable, Iterable
from line import Line
from word import Word

class LineIterator:

  def __init__(self, soup: BeautifulSoup, logging_function: Callable[[str], None]):
    self.soup = soup
    self.logging_function = logging_function

  def __iter__(self) -> Iterable[Line]:
    lang = 'hit'
    publ = self.soup.find('AO:TxtPubl').text
    lnr = '[unknown]'
    words = list[Word]()
    for tag in soup(['lb', 'w']):
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
            logging_function('Line {0} in {1} is not marked for language.\n'.format(lnr, publ))
            lang = 'Hur'
        case 'w':
          if lang == 'Hur':
            if 'lg' in tag.attrs and tag['lg'] != 'Hur':
              continue
            try:
              word = parseMorph(tag)
            except ValueError:
              raise ValueError(
                'Cannot parse word:\n{0}\non line {1} in {2}'.format(
                  str(tag), lnr, publ
                )
              )
    if len(words) > 0:
      yield Line(publ, lnr, words)
