import argparse
import loggers
from os import path
import os
import json
from itertools import chain
from model.corpus import Corpus, processed_file_logger, skipped_file_logger
from lexical_database import LexicalDatabase
from logging import getLogger
from udapi.block.read.conllu import Conllu
from model.morph import SingleMorph
from gen_morph.gramm_forms.linearizer import Linearizer
from gen_morph.tag_converter import TagConverter

logger = getLogger(__name__)

parser = argparse.ArgumentParser(
  prog='DictionarGenerator',
  description='Generate a JSON dictionary from a conllu corpus',
  epilog='An existing output file will be overwritten'
)
parser.add_argument('infile')
parser.add_argument('linearizer')
parser.add_argument('converter')
parser.add_argument('outfile')
args = parser.parse_args()

def convert(pos, feat):
    return feat.upper()

lin = Linearizer.from_file(args.linearizer)
conv = TagConverter(args.converter, convert)

if path.exists(args.outfile):
  os.remove(args.outfile)

lexdb = LexicalDatabase()

reader = Conllu(files=[args.infile])
document = reader.read_documents()[0]

# for node in chain.from_iterable(root.descendants for root in document.trees):
#     for child in node.children:
#         if child.deprel == 'case' and child.gloss == '' and child.upos == 'ADP':
#             child.feats['Case'] = node.feats['Case']
#             del node.feats['Case']

for tree in document.trees:
  for node in tree.descendants:
    if len(node.feats) > 0:
      try:
        morph_tag = lin(node.upos, conv.convert(node.feats))
      except (AssertionError, KeyError) as exc:
        morph_tag = ''
        print(tree.sent_id)
        print(exc)
    else:
      morph_tag = ''
    morph = SingleMorph(node.lemma if node.lemma != '_' else node.form, node.gloss, morph_tag, node.upos, '', None)
    lexdb.dictionary[node.form].add(str(morph))
    lexdb.parts_of_speech.add(node.upos)

with open(args.outfile, 'w', encoding='utf-8') as fout:
  json.dump(lexdb.to_dict(), fout, ensure_ascii=False, indent='\t', sort_keys=True)
logger.info('The run was completed successfully.')
