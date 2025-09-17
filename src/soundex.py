# soundex.py
import re

def soundex(word: str) -> str:
    """
    Convert a word to its Soundex code.
    """
    word = word.upper()

    # 1. Keep first letter
    first_letter = word[0]

    # 2. Replace consonants with digits
    mapping = {
        'BFPV': '1',
        'CGJKQSXZ': '2',
        'DT': '3',
        'L': '4',
        'MN': '5',
        'R': '6'
    }

    def get_digit(ch):
        for key, val in mapping.items():
            if ch in key:
                return val
        return ''  # vowels & others ignored

    # Encode the rest
    digits = [get_digit(ch) for ch in word[1:]]

    # 3. Remove consecutive duplicates
    filtered = []
    prev = ''
    for d in digits:
        if d != prev:
            filtered.append(d)
        prev = d

    # 4. Remove empty strings (vowels, h, w, y)
    filtered = [d for d in filtered if d != '']

    # 5. Combine with first letter
    code = first_letter + ''.join(filtered)

    # 6. Pad/truncate to 4 characters
    return (code + "000")[:4]
