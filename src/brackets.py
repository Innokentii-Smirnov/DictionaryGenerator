import re

bracket_pair = re.compile(r'\[([^\[\]]*)\]')

def remove_bracket_pairs(string: str) -> str:
  return bracket_pair.sub(r'\1', string)
