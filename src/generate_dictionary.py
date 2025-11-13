import json
import os
from os import path
import shutil
from tqdm.auto import tqdm
from os.path import exists
from os import remove, chdir
from json import dump
from lexical_database import LexicalDatabase
from model.text import Text
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
            text_id, ext = path.splitext(filename)
            print(fullname, file=modified_files)
            if ext == '.xml':
              try:
                infile = path.join(dirpath, filename)
                with open(infile, 'r', encoding='utf-8') as fin:
                    text = Text.parse(rel_path, text_id, fin)
                if text is not None:
                  for line in text.lines:
                    print('\t{0} ({1})'.format(line.line_id, len(line.word_elements)),
                          file=modified_files)
                    lexdb.add(line)
              except (KeyError, ValueError, AssertionError) as exc:
                log_file_skipping(fullname)
                logger.exception('The file %s could not be proccessed because of the following exception:', fullname)
with open(OUTFILE, 'w', encoding='utf-8') as fout:
  dump(lexdb.to_dict(), fout, ensure_ascii=False, indent='\t', sort_keys=True)
logger.info('The run was completed successfully.')




















