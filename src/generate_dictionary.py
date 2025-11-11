import json
import os
from os import path
import shutil
from tqdm.auto import tqdm
from bs4 import BeautifulSoup
from more_itertools import split_before
import traceback
from os.path import exists
from os import remove, chdir
from json import dump
from typing import Callable
from line import Line
from itertools import filterfalse
from bs4 import Tag, NavigableString, PageElement
from lexical_database import LexicalDatabase
from logging import getLogger
logger = getLogger(__name__)

PROCESSED_FILES_LOG = 'processed_files.log'
SKIPPED_FILES_LOG = 'skipped_files.log'
OUTFILE = 'Dictionary.json'

def log_file_skipping(fullname: str) -> None:
  with open(SKIPPED_FILES_LOG, 'a', encoding='utf-8') as skipped_files:
    print(fullname, file=skipped_files)

if exists(PROCESSED_FILES_LOG):
  remove(PROCESSED_FILES_LOG)

if exists(SKIPPED_FILES_LOG):
  remove(SKIPPED_FILES_LOG)

if exists(OUTFILE):
  remove(OUTFILE)

with open('config.json', 'r', encoding='utf-8') as fin:
    config = json.load(fin)
for key, value in config.items():
    config[key] = path.expanduser(value)
input_directory = config['inputDirectory']
if not path.exists(input_directory):
    print('Input directory not found: ' + input_directory)
    exit()

def to_be_procecced(triple: tuple[str, list[str], list[str]]) -> bool:
  dirpath, dirnames, filenames = triple
  _, folder = path.split(dirpath)
  return folder != 'Backup' and 'Annotation' in dirpath

def is_ao_manuscripts(tag: Tag) -> bool:
  return tag.prefix == 'AO' and tag.name == 'Manuscripts'

walk = list(filter(to_be_procecced, os.walk(input_directory)))
progress_bar = tqdm(walk)

lexdb = LexicalDatabase()

with open(PROCESSED_FILES_LOG, 'w', encoding='utf-8') as modified_files:
    for dirpath, dirnames, filenames in progress_bar:
        rel_path = dirpath.removeprefix(input_directory).removeprefix(os.sep)
        print(dirpath, file=modified_files)
        _, folder = path.split(dirpath)
        progress_bar.set_postfix_str(folder)
        for filename in filenames:
            fullname = path.join(dirpath, filename)
            rel_name = path.join(rel_path, filename)
            text_id, ext = path.splitext(filename)
            print(fullname, file=modified_files)
            if ext == '.xml':
              try:
                infile = path.join(dirpath, filename)
                with open(infile, 'r', encoding='utf-8') as fin:
                    file_text = fin.read()
                soup = BeautifulSoup(file_text, 'xml')
                body_tag = soup.body
                assert body_tag is not None, 'The XML tag "body" could not be found.'
                text_tag = body_tag.find('text')
                assert text_tag is not None, 'The XML tag "text" could not be found.'
                assert isinstance(text_tag, Tag), 'A string was provided instead of the XML tag "text".'
                if 'xml:lang' in text_tag.attrs and text_tag['xml:lang'] != 'XXXlang':
                  text_lang = text_tag['xml:lang']
                  logger.info('The text language is set to %s for %s', text_lang, rel_name)
                else:
                  text_lang = 'Hit'
                tokens = list[Tag]()
                for page_element in text_tag.children:
                  if isinstance(page_element, Tag):
                    tokens.append(page_element)
                if is_ao_manuscripts(tokens[0]):
                  tokens = tokens[1:]
                for line_elements in split_before(tokens,
                                                  lambda tag: tag.name == 'lb'):
                  line = Line.parse_line(rel_path, text_id, line_elements)
                  print('\t{0} ({1})'.format(line.line_id, len(line.word_elements)),
                        file=modified_files)
                  lexdb.add(line)
              except (KeyError, ValueError) as exc:
                log_file_skipping(fullname)
                logger.exception('The file %s could not be proccessed because of the following exception:', fullname)
with open(OUTFILE, 'w', encoding='utf-8') as fout:
  dump(lexdb.to_dict(), fout, ensure_ascii=False, indent='\t', sort_keys=True)
logger.info('The run was completed successfully.')




















