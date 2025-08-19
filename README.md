# regexp.py

A Python utility to generate **regular expressions** from plain text phrases or sentences.  
It builds regexes that are:

- **Case-explicit**: each letter is represented as `[Aa]` rather than using `(?i)`.
- **Compact**: consecutive identical characters are compressed (e.g. `ll` → `[Ll]{2}`).
- **Whitespace tolerant**: any run of whitespace is collapsed to `\s+` (one or more whitespace).
- **Optional groups**: parentheses `(...)` make their contents optional, supporting **nested parentheses**.
- **Numeric/text placeholders**: curly braces with a slash `{digit/text}` expand into a regex that matches either the digit(s) or the spelled-out text (e.g. `{2/two}`).
- **Alternatives**: pass two arguments; the script will output a regex matching either phrase.
- **Accented letters**: accented letters also match their unaccented counterparts (e.g. á -> [aAáÁ])

---

## Requirements

- Python 3.7+
- No external dependencies

---

## Installation

Copy `regexp.py` into your project directory and (optionally) make it executable:

    chmod +x regexp.py

---

## Usage

Generate a regex from a single phrase:

    python regexp.py "your text here"

Generate a regex that matches either of two phrases:

    python regexp.py "first phrase" "second phrase"

Show help:

    python regexp.py -h

---

## Examples

Single-word / simple:

    python regexp.py Hello
    # Output:
    # [Hh][Ee][Ll]{2}[Oo]

Multiple spaces collapsed to `\s+`:

    python regexp.py "Good   job!!"
    # Output:
    # [Gg][Oo]{2}[Dd]\s+[Jj][Oo][Bb]\!{2}

Optional parentheses (nested supported):

    python regexp.py "colo(u)r"
    # Output:
    # [Cc][Oo][Ll][Oo](?:[Uu])?[Rr]

More nesting:

    python regexp.py "a(b(c)d)e"
    # Output:
    # [Aa](?:[Bb](?:[Cc])?[Dd])?[Ee]

Numeric/text placeholder:

    python regexp.py "I have {2/two} cats"
    # Example output (grouping may vary):
    # [Ii]\s+[Hh][Aa][Vv][Ee]\s+(?:(?:2)|(?:[Tt][Ww][Oo]))\s+[Cc][Aa][Tt][Ss]

Two-phrase alternation (English / Spanish):

    python regexp.py "I have {2/two} cats" "Tengo {2/dos} gatos"
    # Output will be an alternation of the two generated regexes, e.g.:
    # (?:<regex-for-english>)|(?:<regex-for-spanish>)

---

## How it works (high level)

- Iterates characters of the input phrase.
- Converts letters to explicit case-bracket tokens (`[aA]` style).
- Counts consecutive equal letters (case-insensitive for letters) and uses `{n}` repetition quantifier.
- Escapes and compresses repeated punctuation/symbols as well (e.g. `!!!` → `\!{3}`).
- Replaces any contiguous whitespace with the single token `\s+`.
- Converts parentheses to a non-capturing optional group `(?:...)?`, and handles nesting recursively.
- Parses placeholders of the form `{left/right}` and generates an alternation that matches either `left` or `right` (both sides are processed with the same transformation rules).

---

## Example: Using the generated regex in Python

    import re
    from subprocess import check_output

    # generate regex using the script
    regex = check_output(['python', 'regexp.py', 'Hello']).decode().strip()

    # use it
    pattern = re.compile(regex)
    print(bool(pattern.search("hELLo")))  # True
    print(bool(pattern.search("Hxllo")))  # False

---

> [!WARNING]
> The Google Forms validation may be set to `contains` rather than to `matches` as line init and ending are not handled.

---

## License

MIT License — feel free to use, modify, and share.
