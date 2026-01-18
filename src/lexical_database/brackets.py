import re
brackets = re.compile(r'[\[\]]')

def contains_brackets(transcription: str) -> bool:
  return brackets.search(transcription) is not None

def remove_brackets(transcription: str) -> str:
  return brackets.sub('', transcription)
