# Test Cases for String Search Algorithms

## 1. Large Alphabet + Long Pattern (BMH's Ideal Case)
```python
import random, string

# Generate a large random text with a large alphabet
text = ''.join(random.choices(string.ascii_letters + string.digits, k=1_000_000))

# Define a long pattern with rare characters
pattern = "xQ7mK9pL2nR8vT4wY6"

# Explanation:
# - BMH skips approximately len(pattern) characters per mismatch.
# - KMP crawls through every character, making it slower in this case.
```

## 2. Long Pattern, Few Matches
```python
# Load a large natural English text
text = open("large_english_text.txt").read()

# Define a long pattern that rarely appears in the text
pattern = "cryptographic hash function verification"

# Explanation:
# - BMH jumps far ahead on each mismatch.
# - The longer the pattern, the bigger the skip, making BMH efficient.
```

## 3. Binary/Byte Data with Long Pattern
```python
# Generate binary data with a large alphabet
text = bytes(range(256)) * 4000  # 256-character alphabet, ~1MB

# Define a long pattern in binary format
pattern = b"\xFA\xFB\xFC\xFD\xFE\xFF\x01\x02\x03\x04"

# Explanation:
# - Large alphabet ensures almost every byte causes a maximum skip.
# - BMH performs well due to the high mismatch rate.
```

## 4. Pattern Characters Rarely Appear in Text
```python
# Generate a repetitive text with a single character
text = "a" * 1_000_000

# Define a pattern with characters that rarely (or never) appear in the text
pattern = "zzzzzzzzzzzzzzzzzzzzb"  # 'z' never appears in the text

# Explanation:
# - Every comparison immediately hits an unmapped character.
# - BMH skips by the full length of the pattern on each mismatch.
```

## 5. Genomic Data with a Long Pattern
```python
import random

# Generate genomic data with a small alphabet
text = ''.join(random.choices("ACGT", k=1_000_000))

# Define a long pattern with repetitive genomic sequences
pattern = "ACGTACGTACGTACGTACGT" * 3  # 60 characters

# Explanation:
# - Small alphabet reduces skip potential.
# - However, the long pattern compensates, allowing decent skips.
```