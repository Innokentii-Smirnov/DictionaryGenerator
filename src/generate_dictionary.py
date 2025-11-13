from os import path
import os
import json
from model.corpus import Corpus
from lexical_database import LexicalDatabase
from logging import getLogger
logger = getLogger(__name__)

OUTFILE = 'Dictionary.json'
if path.exists(OUTFILE):
  os.remove(OUTFILE)

CONFIG_FILENAME = 'config.json'
if not path.exists(CONFIG_FILENAME):
  logger.error('Please, provide a configuration file called "config.json" in the working directory.')
  exit()
with open(CONFIG_FILENAME, 'r', encoding='utf-8') as fin:
  config = json.load(fin)
for key, value in config.items():
  config[key] = path.expanduser(value)
input_directory = config['inputDirectory']
if not path.exists(input_directory):
  logger.error('Input directory not found: ' + input_directory)
  exit()

lexdb = LexicalDatabase()
corpus = Corpus(input_directory)
for line in corpus.lines:
  lexdb.add(line)

with open(OUTFILE, 'w', encoding='utf-8') as fout:
  json.dump(lexdb.to_dict(), fout, ensure_ascii=False, indent='\t', sort_keys=True)
logger.info('The run was completed successfully.')
