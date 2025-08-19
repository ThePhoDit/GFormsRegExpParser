#!/usr/bin/env python3
r"""
make_regex.py

Generate a regex from a word or sentence that:
- Matches letters explicitly in either case using brackets, e.g. [Aa]
- Compresses consecutive identical letters/characters using {n}
- Collapses any contiguous whitespace into \s+ (one or more whitespace)
- Treats parentheses (...) as optional groups (?:...)? and handles nesting
 - Supports numeric placeholders {digit/number}, matching either the digits or the spelled-out text
 - Accented letters also match their unaccented counterparts (e.g. á -> [aAáÁ])

Examples:
    python make_regex.py Hello
    python make_regex.py "Good   job!!"
    python make_regex.py "colo(u)r"
    python make_regex.py "a(b(c)d)e"
    python make_regex.py "I have {2/two} cats"
    python make_regex.py "I have {2/two} cats" "Tengo {2/dos} gatos"

Run:
    python make_regex.py -h
for help and more examples.
"""
import re
import unicodedata
import sys
import argparse

def find_matching_paren(s: str, start: int) -> int:
    """Given s[start] == '(', find the index of the matching ')' (handles nesting)."""
    depth = 0
    for i in range(start, len(s)):
        if s[i] == '(':
            depth += 1
        elif s[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("Unmatched '(' in input")

def make_regex_segment(s: str, i: int, end: int) -> (str, int):
    """
    Process s starting at i up to end (exclusive).
    Returns (regex_fragment, new_index).
    """
    ch = s[i]

    # whitespace sequence -> \s+
    if ch.isspace():
        j = i + 1
        while j < end and s[j].isspace():
            j += 1
        return r"\s+", j

    # parenthesis -> recursive optional group
    if ch == '(':
        j = find_matching_paren(s, i)
        inner = build_regex(s[i+1:j])  # recursive
        return f"(?:{inner})?", j + 1

    # numeric/text placeholder: {digit/number}
    if ch == '{':
        j = i + 1
        while j < end and s[j] != '}':
            j += 1
        if j >= end or s[j] != '}':
            raise ValueError("Unmatched '{' in input; expected '}' for placeholder {digit/number}")
        content = s[i+1:j]
        sep = content.find('/')
        if sep == -1:
            raise ValueError("Invalid placeholder; expected format {digit/number}")
        left = content[:sep].strip()
        right = content[sep+1:].strip()
        # Build regex for each side so that whitespace, parentheses, repeats, and case are handled
        left_regex = build_regex(left)
        right_regex = build_regex(right)
        return f"(?:{left_regex})|(?:{right_regex})", j + 1

    # letters: case-insensitive bracket (with accent-insensitive variants) and count repeats
    if ch.isalpha():
        # count consecutive same-letter (case-insensitive)
        j = i + 1
        while j < end and s[j].isalpha() and s[j].lower() == ch.lower():
            j += 1
        count = j - i
        # Build a bracket that includes the letter in both cases, plus the
        # unaccented base letter in both cases if the input letter has accents.
        def strip_accents(c: str) -> str:
            # Decompose and drop combining marks
            return "".join(ch for ch in unicodedata.normalize("NFD", c) if not unicodedata.combining(ch))

        # Prepare ordered unique list: prefer base followed by original
        ordered_chars = []
        seen = set()
        def add_c(c):
            for v in (c.lower(), c.upper()):
                if v not in seen:
                    seen.add(v)
                    ordered_chars.append(v)

        base = strip_accents(ch)
        if base and base.isalpha() and len(base) == 1 and base.lower() != ch.lower():
            add_c(base)
        add_c(ch)
        part = "[" + "".join(ordered_chars) + "]"
        if count > 1:
            part += f"{{{count}}}"
        return part, j

    # other non-space, non-paren characters: escape and compress repeats
    # (comparison is case-sensitive for non-letters)
    j = i + 1
    while j < end and not s[j].isspace() and s[j] != '(' and s[j] != ')' and s[j] == ch:
        j += 1
    count = j - i
    escaped = re.escape(ch)
    if count > 1:
        escaped += f"{{{count}}}"
    return escaped, j

def build_regex(s: str) -> str:
    """Build regex for the full string s."""
    i = 0
    parts = []
    n = len(s)
    while i < n:
        part, i = make_regex_segment(s, i, n)
        parts.append(part)
    return "".join(parts)

def make_regex(text: str) -> str:
    r"""Public wrapper: builds regex from text (keeps the whitespace rule: contiguous whitespace -> \s+)."""
    return build_regex(text)

def parse_args(argv):
    epilog = r"""Examples:
  python make_regex.py Hello
  python make_regex.py "Good   job!!"
  python make_regex.py "colo(u)r"
  python make_regex.py "a(b(c)d)e"
  python make_regex.py "I have {2/two} cats"
  python make_regex.py "I have {2/two} cats" "Tengo {2/dos} gatos"
"""
    parser = argparse.ArgumentParser(
        description="Generate a regex that matches any combination of uppercase/lowercase and compresses repeats. Parentheses become optional (recursive).",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "text1",
        help="First word or sentence to convert into a regex (wrap in quotes for multi-word)."
    )
    parser.add_argument(
        "text2",
        nargs="?",
        help="Optional second word or sentence; if provided, the output regex matches either input."
    )
    parser.add_argument(
        "--version",
        action="version",
        version="make_regex.py 1.0"
    )
    return parser.parse_args(argv)

def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    text1 = args.text1
    text2 = args.text2
    try:
        regex1 = make_regex(text1)
        if text2 is not None:
            regex2 = make_regex(text2)
            regex = f"(?:{regex1})|(?:{regex2})"
        else:
            regex = regex1
        print(regex)
    except ValueError as e:
        print("Error:", e, file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())

