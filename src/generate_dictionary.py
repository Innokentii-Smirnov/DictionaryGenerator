import json
import os
from os import path
import shutil
from tqdm.auto import tqdm
from bs4 import BeautifulSoup
from line_iterator import LineIterator
import traceback
from os.path import exists
from os import remove
from json import dump
from lexical_database import LexicalDatabase

PROCESSED_FILES_LOG = 'processed_files.log'
SKIPPED_FILES_LOG = 'skipped_files.log'
MAIN_LOG = 'main.log'
ERROR_LOG = 'error.log'
OUTFILE = 'Dictionary.json'

def log_file_skipping(fullname: str) -> None:
  with open(SKIPPED_FILES_LOG, 'a', encoding='utf-8') as skipped_files:
    print(fullname, file=skipped_files)

def log_error(message: str) -> None:
  with open(ERROR_LOG, 'a', encoding='utf-8') as error_log:
    print(message, file=error_log)

if exists(SKIPPED_FILES_LOG):
  remove(SKIPPED_FILES_LOG)

if exists(ERROR_LOG):
  remove(ERROR_LOG)

if exists(MAIN_LOG):
  remove(MAIN_LOG)

with open('config.json', 'r', encoding='utf-8') as fin:
    config = json.load(fin)
for key, value in config.items():
    config[key] = path.expanduser(value)
input_directory = config['inputDirectory']
if not path.exists(input_directory):
    print('Input directory not found: ' + input_directory)
    exit()
walk = list(os.walk(input_directory))
progress_bar = tqdm(walk)
lexdb = LexicalDatabase()
with (open(PROCESSED_FILES_LOG, 'w', encoding='utf-8') as modified_files,
      open(MAIN_LOG, 'w', encoding='utf-8') as log):
    for dirpath, dirnames, filenames in progress_bar:
        _, folder = path.split(dirpath)
        if folder != 'Backup' and 'Annotation' in dirpath:
            print(dirpath, file=modified_files)
            progress_bar.set_postfix_str(folder)
            for filename in filenames:
                fullname = path.join(dirpath, filename)
                text_name, ext = path.splitext(filename)
                print(fullname, file=modified_files)
                if ext == '.xml':
                  try:
                    infile = path.join(dirpath, filename)
                    with open(infile, 'r', encoding='utf-8') as fin:
                        file_text = fin.read()
                    soup = BeautifulSoup(file_text, 'xml')
                    for line in LineIterator(soup, log.write).lines:
                      print('\t{0} ({1})'.format(line.line_id, len(line.words)), file=modified_files)
                      lexdb.add(line)
                  except (KeyError, ValueError) as exc:
                    log_file_skipping(fullname)
                    log_error(fullname)
                    log_error(traceback.format_exc())
with open(OUTFILE, 'w', encoding='utf-8') as fout:
  dump(lexdb.to_dict(), fout, ensure_ascii=False, indent='\t', sort_keys=True)





















