def find_outmost_brackets(string: str) -> tuple[int, int] | None:
    bb = 0 # Bracketing balance
    for i, char in enumerate(string):
        if char == '(':
            if bb == 0:
                start = i
            bb += 1
        elif char == ')':
            bb -= 1
            if bb == 0:
                end = i + 1
                return (start, end)
    return None

def step(expression: str, language: list[str]):
    result = find_outmost_brackets(expression)
    if result is None:
        language.append(expression)
    else:
        start, end = result
        short_variant = expression[:start] + expression[end:]
        step(short_variant, language)
        long_variant = expression[:start] +  expression[start+1:end-1] + expression[end:]
        step(long_variant, language)

def generate_language(expression: str) -> list[str]:
    language = list[str]()
    step(expression, language)
    return set(language)
