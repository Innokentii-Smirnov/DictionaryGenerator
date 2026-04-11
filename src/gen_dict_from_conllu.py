import argparse
import loggers
from os import path
import os
import json
from model.corpus import Corpus, processed_file_logger, skipped_file_logger
from lexical_database import LexicalDatabase
from lexical_database.corpus_word import make_corpus_word, enclose_with_xml_tag
from logging import getLogger
from udapi.block.read.conllu import Conllu
from model.morph import SingleMorph

logger = getLogger(__name__)

parser = argparse.ArgumentParser(
  prog='DictionarGenerator',
  description='Generate a JSON dictionary from a conllu corpus',
  epilog='An existing output file will be overwritten'
)
parser.add_argument('infile')
parser.add_argument('outfile')
args = parser.parse_args()

if path.exists(args.outfile):
  os.remove(args.outfile)

lexdb = LexicalDatabase()

reader = Conllu(files=[args.infile])
document = reader.read_documents()[0]

for tree in document.trees:
  attestation = '?,' + tree.sent_id
  corpus_words = list()
  for node in tree.descendants:
    match node.misc['MGloss'].split('-', maxsplit=1):
      case gloss, morph_tag:
        pass
      case gloss,:
        morph_tag = ''
    segmentation = node.misc['MSeg']
    morph = SingleMorph(segmentation, node.gloss, morph_tag, node.upos, '', None)
    lexdb.add_word_attestation(node.form, morph, attestation)
    lexdb.parts_of_speech.add(node.upos)
    gloss = '-'.join(filter(lambda elem: elem != '', [node.gloss, morph_tag]))
    corpus_word = make_corpus_word(enclose_with_xml_tag(node.form, 'w'), segmentation, gloss)
    corpus_words.append(corpus_word)
  lexdb.corpus[attestation] = corpus_words

with open(args.outfile, 'w', encoding='utf-8') as fout:
  json.dump(lexdb.to_dict(), fout, ensure_ascii=False, indent='\t', sort_keys=True)
logger.info('The run was completed successfully.')
