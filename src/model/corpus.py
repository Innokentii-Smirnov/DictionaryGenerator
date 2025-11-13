from dataclasses import dataclass
from collections.abc import Iterable
from .text import Text
import os
from tqdm.auto import tqdm
from os import path
from .line import Line
from itertools import chain
from logging import getLogger
logger = getLogger(__name__)

PROCESSED_FILE_LOGGER_NAME = 'processed_files'
processed_file_logger = getLogger(PROCESSED_FILE_LOGGER_NAME)
SKIPPED_FILE_LOGGER_NAME = 'skipped_files'
skipped_file_logger = getLogger(SKIPPED_FILE_LOGGER_NAME)

def to_be_procecced(triple: tuple[str, list[str], list[str]]) -> bool:
  dirpath, dirnames, filenames = triple
  _, folder = path.split(dirpath)
  return folder != 'Backup' and 'Annotation' in dirpath

@dataclass
class Corpus:
  input_directory: str

  @property
  def texts(self) -> Iterable[Text]:
    walk = list(filter(to_be_procecced, os.walk(self.input_directory)))
    progress_bar = tqdm(walk)
    for dirpath, dirnames, filenames in progress_bar:
      rel_path = dirpath.removeprefix(self.input_directory).removeprefix(os.sep)
      processed_file_logger.info(dirpath)
      _, folder = path.split(dirpath)
      progress_bar.set_postfix_str(folder)
      for filename in filenames:
        fullname = path.join(dirpath, filename)
        text_id, ext = path.splitext(filename)
        processed_file_logger.info('\t' + fullname)
        if ext == '.xml':
          try:
            infile = path.join(dirpath, filename)
            with open(infile, 'r', encoding='utf-8') as fin:
                text = Text.parse(rel_path, text_id, fin)
            if text is not None:
              yield text
          except (KeyError, ValueError, AssertionError) as exc:
            skipped_file_logger.info(fullname)
            logger.exception('The file %s could not be proccessed because of the following exception:', fullname)

  @property
  def lines(self) -> Iterable[Line]:
    return chain.from_iterable(text.lines for text in self.texts)
