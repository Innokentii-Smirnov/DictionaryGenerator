from bs4 import BeautifulSoup
from line_iterator import LineIterator

filename = '/home/bazzite/bwSyncShare/TIVE BASISCORPUS ARBEITSBEREICH/CTH_789_mit_Annotation/KBo 32.14.xml'
with open(filename, 'r', encoding='utf-8') as fin:
    file_text = fin.read()
soup = BeautifulSoup(file_text, 'xml')
li = LineIterator(soup, print)
for line in li.lines:
  print(line.line_id)
